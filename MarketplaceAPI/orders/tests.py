"""Tests du module orders."""
from decimal import Decimal

from django.test import TestCase
from ninja.testing import TestClient

from api.ninja_api import api
from cart.models import LignePanier, Panier
from catalog.models import Produit
from orders.models import Commande, HistoriqueVente, StatutCommande
from places.models import Magasin
from users.models import RoleUtilisateur, Utilisateur

MDP = "Sup3rPass!"


class OrdersTestCase(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.user = Utilisateur.objects.create_user(
            email="client@x.com", password=MDP, nom="C", prenom="C",
            telephone="+261340000001", role=RoleUtilisateur.CLIENT,
        )
        self.panier = Panier.objects.create(utilisateur=self.user)
        self.vendeur = Utilisateur.objects.create_user(
            email="v@x.com", password=MDP, nom="V", prenom="V",
            telephone="+261340000002", role=RoleUtilisateur.VENDEUR,
        )
        self.magasin = Magasin.objects.create(nom="Shop", proprietaire=self.vendeur)
        self.produit = Produit.objects.create(
            magasin=self.magasin, nom="Riz", prix_mga=5000, quantite=100,
        )

    def _auth(self, user):
        from ninja_jwt.tokens import RefreshToken
        return {"Authorization": f"Bearer {RefreshToken.for_user(user).access_token}"}

    # --- Adresses de livraison -------------------------------------------

    def test_creer_adresse_ok(self):
        r = self.client.post("/adresses",
                            json={
                                "adresse_complete": "123 Rue A",
                                "ville": "Tana",
                                "telephone": "+261340000099",
                            },
                            headers=self._auth(self.user))
        self.assertEqual(r.status_code, 201)

    def test_lister_adresses_ok(self):
        self.client.post("/adresses",
                        json={
                            "adresse_complete": "123 Rue A",
                            "ville": "Tana",
                            "telephone": "+261340000099",
                        },
                        headers=self._auth(self.user))
        r = self.client.get("/adresses", headers=self._auth(self.user))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()["meta"]["adresses"]), 1)

    # --- Passer commande -----------------------------------------------

    def test_passer_commande_ok(self):
        LignePanier.objects.create(panier=self.panier, produit=self.produit, quantite=2)
        r = self.client.post("/commandes", json={}, headers=self._auth(self.user))
        self.assertEqual(r.status_code, 201)
        data = r.json()["data"]
        self.assertEqual(data["statut"], StatutCommande.EN_ATTENTE)
        self.assertEqual(data["total_mga"], "10000.00")

    def test_passer_commande_panier_vide(self):
        r = self.client.post("/commandes", json={}, headers=self._auth(self.user))
        self.assertEqual(r.status_code, 400)

    def test_passer_commande_stock_insuffisant(self):
        self.produit.quantite = 1
        self.produit.save()
        LignePanier.objects.create(panier=self.panier, produit=self.produit, quantite=5)
        r = self.client.post("/commandes", json={}, headers=self._auth(self.user))
        self.assertEqual(r.status_code, 400)

    def test_passer_commande_vide_panier(self):
        LignePanier.objects.create(panier=self.panier, produit=self.produit, quantite=1)
        self.client.post("/commandes", json={}, headers=self._auth(self.user))
        panier = Panier.objects.get(utilisateur=self.user)
        self.assertEqual(panier.lignes.count(), 0)

    def test_passer_commande_cree_historique_vente(self):
        LignePanier.objects.create(panier=self.panier, produit=self.produit, quantite=3)
        self.client.post("/commandes", json={}, headers=self._auth(self.user))
        historiques = HistoriqueVente.objects.all()
        self.assertEqual(historiques.count(), 1)
        h = historiques.first()
        self.assertEqual(h.quantite_vendue, 3)
        self.assertEqual(h.montant_total_mga, Decimal("15000"))

    # --- Lister commandes -----------------------------------------------

    def test_lister_commandes_ok(self):
        LignePanier.objects.create(panier=self.panier, produit=self.produit, quantite=1)
        self.client.post("/commandes", json={}, headers=self._auth(self.user))
        r = self.client.get("/commandes", headers=self._auth(self.user))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()["meta"]["commandes"]), 1)

    # --- Obtenir commande -----------------------------------------------

    def test_obtenir_commande_ok(self):
        LignePanier.objects.create(panier=self.panier, produit=self.produit, quantite=1)
        resp = self.client.post("/commandes", json={}, headers=self._auth(self.user))
        commande_id = resp.json()["data"]["id"]
        r = self.client.get(f"/commandes/{commande_id}", headers=self._auth(self.user))
        self.assertEqual(r.status_code, 200)

    def test_obtenir_commande_autre_user(self):
        other_user = Utilisateur.objects.create_user(
            email="other@x.com", password=MDP, nom="O", prenom="O",
            telephone="+261340000099",
        )
        LignePanier.objects.create(panier=self.panier, produit=self.produit, quantite=1)
        resp = self.client.post("/commandes", json={}, headers=self._auth(self.user))
        commande_id = resp.json()["data"]["id"]
        r = self.client.get(f"/commandes/{commande_id}", headers=self._auth(other_user))
        self.assertEqual(r.status_code, 403)

    # --- Annuler commande -----------------------------------------------

    def test_annuler_commande_ok(self):
        LignePanier.objects.create(panier=self.panier, produit=self.produit, quantite=1)
        resp = self.client.post("/commandes", json={}, headers=self._auth(self.user))
        commande_id = resp.json()["data"]["id"]
        r = self.client.post(f"/commandes/{commande_id}/annuler", headers=self._auth(self.user))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["data"]["statut"], StatutCommande.ANNULEE)

    def test_annuler_commande_confirmee(self):
        LignePanier.objects.create(panier=self.panier, produit=self.produit, quantite=1)
        resp = self.client.post("/commandes", json={}, headers=self._auth(self.user))
        commande_id = resp.json()["data"]["id"]
        commande = Commande.objects.get(pk=commande_id)
        commande.statut = StatutCommande.CONFIRMEE
        commande.save()
        r = self.client.post(f"/commandes/{commande_id}/annuler", headers=self._auth(self.user))
        self.assertEqual(r.status_code, 400)
