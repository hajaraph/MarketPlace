"""
Tests du flux d'authentification (api/routers/auth.py + users/services.py).

Couverture : register, login, refresh, me — chemins nominaux ET cas d'erreur.
On tape l'API via le TestClient Ninja (intégration router → service → ORM).
"""
from django.test import TestCase
from ninja.testing import TestClient

from api.ninja_api import api
from users.models import RoleUtilisateur, Utilisateur

MDP = "Sup3rPass!"


class AuthTestCase(TestCase):
    def setUp(self):
        self.client = TestClient(api)

    def _register(self, email="alice@x.com", **extra):
        payload = {"email": email, "password": MDP, "nom": "A", "prenom": "B", **extra}
        return self.client.post("/auth/register", json=payload)

    def _auth_header(self, access):
        return {"Authorization": f"Bearer {access}"}

    # --- register ---------------------------------------------------------

    def test_register_ok(self):
        r = self._register()
        self.assertEqual(r.status_code, 201)
        body = r.json()
        self.assertTrue(body["success"])
        self.assertIn("timestamp", body)
        data = body["data"]
        self.assertEqual(data["user"]["email"], "alice@x.com")
        self.assertEqual(data["user"]["role"], RoleUtilisateur.CLIENT)
        self.assertIn("access", data)
        self.assertIn("refresh", data)

    def test_register_hash_mot_de_passe(self):
        self._register()
        u = Utilisateur.objects.get(email="alice@x.com")
        self.assertNotEqual(u.password, MDP)
        self.assertTrue(u.check_password(MDP))

    def test_register_doublon_409(self):
        self._register()
        r = self._register()
        self.assertEqual(r.status_code, 409)
        body = r.json()
        self.assertFalse(body["success"])
        self.assertIn("error", body)
        self.assertIn("message", body["error"])

    def test_register_role_personnalise(self):
        r = self._register(email="vendor@x.com", role=RoleUtilisateur.VENDEUR)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["data"]["user"]["role"], RoleUtilisateur.VENDEUR)

    # --- login ------------------------------------------------------------

    def test_login_ok(self):
        self._register()
        r = self.client.post("/auth/login", json={"email": "alice@x.com", "password": MDP})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["success"])
        self.assertIn("access", r.json()["data"])

    def test_login_mauvais_mdp_401(self):
        self._register()
        r = self.client.post("/auth/login", json={"email": "alice@x.com", "password": "x"})
        self.assertEqual(r.status_code, 401)
        body = r.json()
        self.assertFalse(body["success"])
        self.assertIn("message", body["error"])

    def test_login_inconnu_401(self):
        r = self.client.post("/auth/login", json={"email": "nobody@x.com", "password": MDP})
        self.assertEqual(r.status_code, 401)

    def test_login_compte_inactif_401(self):
        self._register()
        Utilisateur.objects.filter(email="alice@x.com").update(is_active=False)
        r = self.client.post("/auth/login", json={"email": "alice@x.com", "password": MDP})
        self.assertEqual(r.status_code, 401)

    # --- me ---------------------------------------------------------------

    def test_me_ok(self):
        access = self._register().json()["data"]["access"]
        r = self.client.get("/auth/me", headers=self._auth_header(access))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["data"]["email"], "alice@x.com")

    def test_me_sans_token_401(self):
        r = self.client.get("/auth/me")
        self.assertEqual(r.status_code, 401)

    def test_me_token_invalide_401(self):
        r = self.client.get("/auth/me", headers=self._auth_header("garbage.token.xyz"))
        self.assertEqual(r.status_code, 401)

    # --- refresh ----------------------------------------------------------

    def test_refresh_ok(self):
        refresh = self._register().json()["data"]["refresh"]
        r = self.client.post("/auth/refresh", json={"refresh": refresh})
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertIn("access", data)
        self.assertIn("refresh", data)

    def test_refresh_token_invalide_401(self):
        r = self.client.post("/auth/refresh", json={"refresh": "garbage"})
        self.assertEqual(r.status_code, 401)
