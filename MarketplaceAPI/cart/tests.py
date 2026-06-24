"""Tests du module cart."""
from django.test import TestCase
from ninja.testing import TestClient

from api.ninja_api import api
from cart.models import LignePanier, Panier
from catalog.models import Produit
from places.models import Magasin
from users.models import RoleUtilisateur, Utilisateur

MDP = "Sup3rPass!"


class CartTestCase(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.user = Utilisateur.objects.create_user(
            email="u@x.com", password=MDP, nom="U", prenom="U",
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

    # --- Get panier --------------------------------------------------

    def test_get_panier_cree_si_absent(self):
        r = self.client.get("/panier", headers=self._auth(self.user))
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertEqual(data["nombre_articles"], 0)
        self.assertEqual(data["total"], 0)

    # --- Ajouter article ---------------------------------------------

    def test_ajouter_article_ok(self):
        r = self.client.post("/panier/articles",
                             json={"produit_id": self.produit.id, "quantite": 2},
                             headers=self._auth(self.user))
        self.assertEqual(r.status_code, 201)
        data = r.json()["data"]
        self.assertEqual(data["quantite"], 2)
        self.assertEqual(data["sous_total"], 10000.0)

    def test_ajouter_article_quantite_invalide(self):
        r = self.client.post("/panier/articles",
                             json={"produit_id": self.produit.id, "quantite": 0},
                             headers=self._auth(self.user))
        self.assertEqual(r.status_code, 400)

    def test_ajouter_article_stock_insuffisant(self):
        r = self.client.post("/panier/articles",
                             json={"produit_id": self.produit.id, "quantite": 999},
                             headers=self._auth(self.user))
        self.assertEqual(r.status_code, 400)

    def test_ajouter_article_produit_indisponible(self):
        self.produit.quantite = 0
        self.produit.save()
        r = self.client.post("/panier/articles",
                             json={"produit_id": self.produit.id, "quantite": 1},
                             headers=self._auth(self.user))
        self.assertEqual(r.status_code, 400)

    # --- Modifier quantité -------------------------------------------

    def test_modifier_quantite_ok(self):
        ligne = LignePanier.objects.create(panier=self.panier,
                                            produit=self.produit, quantite=1)
        r = self.client.patch(f"/panier/articles/{ligne.id}",
                             json={"quantite": 5},
                             headers=self._auth(self.user))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["data"]["quantite"], 5)

    # --- Retirer article ---------------------------------------------

    def test_retirer_article_ok(self):
        ligne = LignePanier.objects.create(panier=self.panier,
                                            produit=self.produit)
        r = self.client.delete(f"/panier/articles/{ligne.id}",
                              headers=self._auth(self.user))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(LignePanier.objects.filter(pk=ligne.id).exists())

    # --- Vider panier ------------------------------------------------

    def test_vider_panier_ok(self):
        LignePanier.objects.create(panier=self.panier, produit=self.produit)
        self.client.post("/panier/vider", headers=self._auth(self.user))
        panier = Panier.objects.get(utilisateur=self.user)
        self.assertEqual(panier.lignes.count(), 0)

    # --- Calcul prix -------------------------------------------------

    def test_calculer_total(self):
        LignePanier.objects.create(panier=self.panier,
                                    produit=self.produit, quantite=3)
        panier = Panier.objects.get(utilisateur=self.user)
        self.assertEqual(panier.calculer_total(), 15000.0)
