"""Tests du module places (magasins & centres commerciaux)."""
from django.test import TestCase
from ninja.testing import TestClient

from api.ninja_api import api
from places.models import CentreCommercial, Magasin
from users.models import RoleUtilisateur, Utilisateur

MDP = "Sup3rPass!"


class PlacesTestCase(TestCase):
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
        self.admin = Utilisateur.objects.create_user(
            email="a@x.com", password=MDP, nom="A", prenom="A",
            telephone="+261340000003", role=RoleUtilisateur.ADMIN,
        )

    def _token(self, user):
        from ninja_jwt.tokens import RefreshToken
        return str(RefreshToken.for_user(user).access_token)

    def _auth(self, user):
        return {"Authorization": f"Bearer {self._token(user)}"}

    def _creer_magasin(self, user, **extra):
        payload = {"nom": "Chez V", "latitude": -18.9, "longitude": 47.5, **extra}
        return self.client.post("/places/magasins", json=payload, headers=self._auth(user))

    # --- création / lecture ---------------------------------------------

    def test_creer_magasin_ok(self):
        r = self._creer_magasin(self.vendeur)
        self.assertEqual(r.status_code, 201)
        data = r.json()["data"]
        self.assertEqual(data["nom"], "Chez V")
        self.assertEqual(data["proprietaire_id"], self.vendeur.id)
        self.assertFalse(data["est_valide"])

    def test_creer_magasin_non_authentifie_401(self):
        r = self.client.post("/places/magasins", json={"nom": "X"})
        self.assertEqual(r.status_code, 401)

    def test_lister_magasins_public(self):
        self._creer_magasin(self.vendeur)
        r = self.client.get("/places/magasins")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["meta"]["total"], 1)

    def test_get_magasin_introuvable_404(self):
        self.assertEqual(self.client.get("/places/magasins/999").status_code, 404)

    # --- permissions ----------------------------------------------------

    def test_modifier_par_non_proprietaire_403(self):
        mid = self._creer_magasin(self.vendeur).json()["data"]["id"]
        r = self.client.patch(f"/places/magasins/{mid}", json={"nom": "Hack"},
                              headers=self._auth(self.autre))
        self.assertEqual(r.status_code, 403)

    def test_modifier_par_proprietaire_ok(self):
        mid = self._creer_magasin(self.vendeur).json()["data"]["id"]
        r = self.client.patch(f"/places/magasins/{mid}", json={"nom": "Nouveau"},
                              headers=self._auth(self.vendeur))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["data"]["nom"], "Nouveau")

    def test_supprimer_soft_delete(self):
        mid = self._creer_magasin(self.vendeur).json()["data"]["id"]
        r = self.client.delete(f"/places/magasins/{mid}", headers=self._auth(self.vendeur))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(Magasin.objects.get(pk=mid).est_supprime)
        self.assertEqual(self.client.get("/places/magasins").json()["meta"]["total"], 0)

    # --- validation admin -----------------------------------------------

    def test_valider_par_admin_ok(self):
        mid = self._creer_magasin(self.vendeur).json()["data"]["id"]
        r = self.client.post(f"/places/magasins/{mid}/valider", headers=self._auth(self.admin))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["data"]["est_valide"])

    def test_valider_par_non_admin_403(self):
        mid = self._creer_magasin(self.vendeur).json()["data"]["id"]
        r = self.client.post(f"/places/magasins/{mid}/valider", headers=self._auth(self.vendeur))
        self.assertEqual(r.status_code, 403)

    # --- centres commerciaux --------------------------------------------

    def test_creer_centre_admin_ok(self):
        r = self.client.post("/places/centres", json={"nom": "Mall", "nombre_etages": 3},
                            headers=self._auth(self.admin))
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["data"]["nombre_etages"], 3)

    def test_creer_centre_non_admin_403(self):
        r = self.client.post("/places/centres", json={"nom": "Mall"},
                            headers=self._auth(self.vendeur))
        self.assertEqual(r.status_code, 403)

    def test_magasin_dans_centre(self):
        centre = CentreCommercial.objects.create(nom="Mall")
        r = self._creer_magasin(self.vendeur, centre_commercial_id=centre.id)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["data"]["centre_commercial_id"], centre.id)

    # --- est_ouvert calculé ---------------------------------------------

    def test_est_ouvert_sans_horaires_null(self):
        m = Magasin.objects.create(nom="H", proprietaire=self.vendeur)
        self.assertIsNone(m.est_ouvert)

    def test_est_ouvert_calcule(self):
        from django.utils import timezone
        now = timezone.localtime()
        jour = str(now.isoweekday())
        m = Magasin.objects.create(
            nom="H", proprietaire=self.vendeur,
            horaires_ouverture={jour: [["00:00", "23:59"]]},
        )
        self.assertTrue(m.est_ouvert)
