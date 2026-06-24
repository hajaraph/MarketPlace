"""Tests du module catalog (produits & médias)."""
from django.test import TestCase
from ninja.testing import TestClient

from api.ninja_api import api
from catalog.models import EtatStock, MediaProduit, Produit
from places.models import Magasin
from users.models import RoleUtilisateur, Utilisateur

MDP = "Sup3rPass!"


class CatalogTestCase(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.vendeur = Utilisateur.objects.create_user(
            email="v@x.com", password=MDP, nom="V", prenom="V",
            telephone="+261340000001", role=RoleUtilisateur.VENDEUR,
        )
        self.autre = Utilisateur.objects.create_user(
            email="o@x.com", password=MDP, nom="O", prenom="O",
            telephone="+261340000002", role=RoleUtilisateur.VENDEUR,
        )
        self.magasin = Magasin.objects.create(nom="Chez V", proprietaire=self.vendeur)

    def _auth(self, user):
        from ninja_jwt.tokens import RefreshToken
        return {"Authorization": f"Bearer {RefreshToken.for_user(user).access_token}"}

    def _creer_produit(self, user, **extra):
        payload = {"magasin_id": self.magasin.id, "nom": "Riz", "prix_mga": 5000,
                   "quantite": 10, **extra}
        return self.client.post("/catalog/produits", json=payload, headers=self._auth(user))

    # --- création / lecture ---------------------------------------------

    def test_creer_produit_ok(self):
        r = self._creer_produit(self.vendeur)
        self.assertEqual(r.status_code, 201)
        data = r.json()["data"]
        self.assertEqual(data["nom"], "Riz")
        self.assertEqual(data["etat_stock"], EtatStock.EN_STOCK)
        self.assertTrue(data["est_disponible"])

    def test_creer_produit_non_proprietaire_403(self):
        r = self._creer_produit(self.autre)
        self.assertEqual(r.status_code, 403)

    def test_creer_produit_magasin_introuvable_404(self):
        r = self.client.post("/catalog/produits",
                             json={"magasin_id": 999, "nom": "X", "prix_mga": 1},
                             headers=self._auth(self.vendeur))
        self.assertEqual(r.status_code, 404)

    def test_lister_produits_public(self):
        self._creer_produit(self.vendeur)
        r = self.client.get(f"/catalog/produits?magasin_id={self.magasin.id}")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["meta"]["total"], 1)

    # --- état du stock dérivé -------------------------------------------

    def test_etat_stock_rupture(self):
        p = Produit.objects.create(magasin=self.magasin, nom="X", prix_mga=1, quantite=0)
        self.assertEqual(p.etat_stock, EtatStock.RUPTURE_STOCK)
        self.assertFalse(p.est_disponible)

    def test_etat_stock_faible(self):
        p = Produit.objects.create(magasin=self.magasin, nom="X", prix_mga=1, quantite=3)
        self.assertEqual(p.etat_stock, EtatStock.STOCK_FAIBLE)

    def test_modifier_quantite_recalcule_etat(self):
        pid = self._creer_produit(self.vendeur).json()["data"]["id"]
        r = self.client.patch(f"/catalog/produits/{pid}", json={"quantite": 0},
                             headers=self._auth(self.vendeur))
        self.assertEqual(r.json()["data"]["etat_stock"], EtatStock.RUPTURE_STOCK)

    # --- suppression -----------------------------------------------------

    def test_supprimer_soft_delete(self):
        pid = self._creer_produit(self.vendeur).json()["data"]["id"]
        r = self.client.delete(f"/catalog/produits/{pid}", headers=self._auth(self.vendeur))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(Produit.objects.get(pk=pid).est_supprime)

    # --- médias ----------------------------------------------------------

    def test_ajouter_media_ok(self):
        pid = self._creer_produit(self.vendeur).json()["data"]["id"]
        r = self.client.post(f"/catalog/produits/{pid}/medias",
                             json={"url_photo": "https://x/p.jpg", "ordre": 1},
                             headers=self._auth(self.vendeur))
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["data"]["url_photo"], "https://x/p.jpg")

    def test_ajouter_media_non_proprietaire_403(self):
        pid = self._creer_produit(self.vendeur).json()["data"]["id"]
        r = self.client.post(f"/catalog/produits/{pid}/medias",
                             json={"url_photo": "https://x/p.jpg"},
                             headers=self._auth(self.autre))
        self.assertEqual(r.status_code, 403)

    def test_lister_medias_public(self):
        pid = self._creer_produit(self.vendeur).json()["data"]["id"]
        MediaProduit.objects.create(produit_id=pid, url_photo="https://x/a.jpg")
        r = self.client.get(f"/catalog/produits/{pid}/medias")
        self.assertEqual(r.json()["meta"]["total"], 1)
