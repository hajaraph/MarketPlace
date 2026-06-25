"""Tests du module payments."""
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from ninja.testing import TestClient

from api.ninja_api import api
from orders.models import Commande, StatutCommande
from payments.models import Declencheur, HistoriquePaiement, MethodePaiement, Paiement, StatutPaiement
from payments.services import expirer_paiements_expires
from users.models import RoleUtilisateur, Utilisateur

MDP = "Sup3rPass!"


class PaymentsTestCase(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.user = Utilisateur.objects.create_user(
            email="buyer@test.com", password=MDP,
            nom="B", prenom="B",
            telephone="+261340000001", role=RoleUtilisateur.CLIENT,
        )
        self.autre = Utilisateur.objects.create_user(
            email="autre@test.com", password=MDP,
            nom="A", prenom="A",
            telephone="+261340000002", role=RoleUtilisateur.CLIENT,
        )
        self.commande = Commande.objects.create(
            utilisateur=self.user,
            adresse_snapshot="Rue du Test, Tana",
            statut=StatutCommande.EN_ATTENTE,
            total_mga=Decimal("25000"),
        )

    def _auth(self, user=None):
        from ninja_jwt.tokens import RefreshToken
        u = user or self.user
        return {"Authorization": f"Bearer {RefreshToken.for_user(u).access_token}"}

    def _paiement(self, expire_dans=None):
        p = Paiement(
            commande=self.commande,
            methode=MethodePaiement.MOBILE_MONEY,
            montant_mga=Decimal("25000"),
        )
        p.save()
        if expire_dans is not None:
            p.expire_le = timezone.now() + timedelta(minutes=expire_dans)
            Paiement.objects.filter(pk=p.pk).update(expire_le=p.expire_le)
            p.refresh_from_db()
        return p

    # --- initier_paiement --------------------------------------------------

    def test_initier_paiement_ok(self):
        r = self.client.post(
            f"/commandes/{self.commande.id}/paiements",
            json={"methode": "MOBILE_MONEY"},
            headers=self._auth(),
        )
        self.assertEqual(r.status_code, 201)
        data = r.json()["data"]
        self.assertEqual(data["statut"], "EN_ATTENTE")
        self.assertEqual(data["methode"], "MOBILE_MONEY")
        self.assertTrue(data["reference_transaction"].startswith("PAY-"))
        self.assertIn("expire_le", data)
        self.assertIsNone(data["date_paiement"])

    def test_initier_paiement_especes_avec_note(self):
        r = self.client.post(
            f"/commandes/{self.commande.id}/paiements",
            json={"methode": "ESPECES", "note": "Paiement à la livraison"},
            headers=self._auth(),
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["data"]["methode"], "ESPECES")

    def test_initier_paiement_methode_invalide(self):
        r = self.client.post(
            f"/commandes/{self.commande.id}/paiements",
            json={"methode": "BITCOIN"},
            headers=self._auth(),
        )
        self.assertEqual(r.status_code, 400)

    def test_initier_paiement_commande_annulee(self):
        self.commande.statut = StatutCommande.ANNULEE
        self.commande.save(update_fields=["statut"])
        r = self.client.post(
            f"/commandes/{self.commande.id}/paiements",
            json={"methode": "ESPECES"},
            headers=self._auth(),
        )
        self.assertEqual(r.status_code, 400)

    def test_initier_paiement_commande_deja_confirmee(self):
        self.commande.statut = StatutCommande.CONFIRMEE
        self.commande.save(update_fields=["statut"])
        r = self.client.post(
            f"/commandes/{self.commande.id}/paiements",
            json={"methode": "ESPECES"},
            headers=self._auth(),
        )
        self.assertEqual(r.status_code, 400)

    def test_initier_paiement_commande_autre_utilisateur(self):
        r = self.client.post(
            f"/commandes/{self.commande.id}/paiements",
            json={"methode": "ESPECES"},
            headers=self._auth(self.autre),
        )
        self.assertEqual(r.status_code, 403)

    # --- valider_paiement --------------------------------------------------

    def test_valider_paiement_ok(self):
        p = self._paiement()
        r = self.client.post(f"/paiements/{p.id}/valider", headers=self._auth())
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertEqual(data["statut"], "VALIDE")
        self.assertIsNotNone(data["date_paiement"])
        self.commande.refresh_from_db()
        self.assertEqual(self.commande.statut, StatutCommande.CONFIRMEE)
        self.assertEqual(HistoriquePaiement.objects.filter(paiement=p).count(), 1)

    def test_valider_paiement_cree_historique(self):
        p = self._paiement()
        self.client.post(f"/paiements/{p.id}/valider", headers=self._auth())
        h = HistoriquePaiement.objects.get(paiement=p)
        self.assertEqual(h.statut_avant, StatutPaiement.EN_ATTENTE)
        self.assertEqual(h.statut_apres, StatutPaiement.VALIDE)
        self.assertEqual(h.declencheur, Declencheur.UTILISATEUR)

    def test_valider_paiement_expire(self):
        p = self._paiement(expire_dans=-1)
        r = self.client.post(f"/paiements/{p.id}/valider", headers=self._auth())
        self.assertEqual(r.status_code, 400)
        p.refresh_from_db()
        self.assertEqual(p.statut, StatutPaiement.EXPIRE)
        h = HistoriquePaiement.objects.get(paiement=p)
        self.assertEqual(h.statut_apres, StatutPaiement.EXPIRE)
        self.assertEqual(h.declencheur, Declencheur.SYSTEME)

    def test_valider_paiement_deja_valide(self):
        p = self._paiement()
        p.valider()
        r = self.client.post(f"/paiements/{p.id}/valider", headers=self._auth())
        self.assertEqual(r.status_code, 400)

    def test_valider_paiement_autre_utilisateur(self):
        p = self._paiement()
        r = self.client.post(f"/paiements/{p.id}/valider", headers=self._auth(self.autre))
        self.assertEqual(r.status_code, 403)

    # --- echouer_paiement --------------------------------------------------

    def test_echouer_paiement_ok(self):
        p = self._paiement()
        r = self.client.post(
            f"/paiements/{p.id}/echouer",
            json={"commentaire": "Solde insuffisant"},
            headers=self._auth(),
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["data"]["statut"], "ECHOUE")
        h = HistoriquePaiement.objects.get(paiement=p)
        self.assertEqual(h.commentaire, "Solde insuffisant")

    def test_echouer_paiement_non_en_attente(self):
        p = self._paiement()
        p.echouer()
        r = self.client.post(
            f"/paiements/{p.id}/echouer",
            json={},
            headers=self._auth(),
        )
        self.assertEqual(r.status_code, 400)

    # --- rembourser_paiement -----------------------------------------------

    def test_rembourser_paiement_ok(self):
        p = self._paiement()
        p.valider()
        self.commande.statut = StatutCommande.CONFIRMEE
        self.commande.save(update_fields=["statut"])
        r = self.client.post(
            f"/paiements/{p.id}/rembourser",
            json={"commentaire": "Retour client"},
            headers=self._auth(),
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["data"]["statut"], "REMBOURSE")
        self.commande.refresh_from_db()
        self.assertEqual(self.commande.statut, StatutCommande.EN_ATTENTE)

    def test_rembourser_paiement_non_valide(self):
        p = self._paiement()
        r = self.client.post(
            f"/paiements/{p.id}/rembourser",
            json={},
            headers=self._auth(),
        )
        self.assertEqual(r.status_code, 400)

    # --- expiration automatique --------------------------------------------

    def test_expirer_paiements_expires_bulk(self):
        p_expire = self._paiement(expire_dans=-1)
        p_valide_encore = self._paiement(expire_dans=30)
        count = expirer_paiements_expires()
        self.assertEqual(count, 1)
        p_expire.refresh_from_db()
        p_valide_encore.refresh_from_db()
        self.assertEqual(p_expire.statut, StatutPaiement.EXPIRE)
        self.assertEqual(p_valide_encore.statut, StatutPaiement.EN_ATTENTE)
        self.assertTrue(HistoriquePaiement.objects.filter(
            paiement=p_expire, statut_apres=StatutPaiement.EXPIRE).exists())

    # --- lister_paiements --------------------------------------------------

    def test_lister_paiements_ok(self):
        p = self._paiement()
        r = self.client.get(
            f"/commandes/{self.commande.id}/paiements",
            headers=self._auth(),
        )
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["meta"]["total"], 1)
        self.assertEqual(body["data"][0]["id"], p.id)

    def test_lister_paiements_commande_introuvable(self):
        r = self.client.get("/commandes/99999/paiements", headers=self._auth())
        self.assertEqual(r.status_code, 404)

    # --- historique --------------------------------------------------------

    def test_lister_historiques_ok(self):
        p = self._paiement()
        p.valider()
        p.rembourser(commentaire="Annulation", declencheur=Declencheur.ADMIN)
        r = self.client.get(f"/paiements/{p.id}/historique", headers=self._auth())
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["meta"]["total"], 2)
        self.assertEqual(body["data"][0]["statut_apres"], StatutPaiement.VALIDE)
        self.assertEqual(body["data"][1]["statut_apres"], StatutPaiement.REMBOURSE)
        self.assertEqual(body["data"][1]["declencheur"], Declencheur.ADMIN)

    def test_historique_autre_utilisateur(self):
        p = self._paiement()
        r = self.client.get(f"/paiements/{p.id}/historique", headers=self._auth(self.autre))
        self.assertEqual(r.status_code, 403)
