"""Use cases du module payments."""
from __future__ import annotations

from django.utils import timezone
from ninja.errors import HttpError

from orders.models import Commande, StatutCommande
from payments.models import Declencheur, MethodePaiement, Paiement, StatutPaiement


def _get_commande(user, commande_id: int) -> Commande:
    try:
        commande = Commande.objects.vivants().get(pk=commande_id)
    except Commande.DoesNotExist:
        raise HttpError(404, "Commande introuvable.")
    if commande.utilisateur_id != user.id:
        raise HttpError(403, "Accès refusé.")
    return commande


def _get_paiement(user, paiement_id: int) -> Paiement:
    try:
        paiement = Paiement.objects.select_related("commande").get(pk=paiement_id)
    except Paiement.DoesNotExist:
        raise HttpError(404, "Paiement introuvable.")
    if paiement.commande.utilisateur_id != user.id:
        raise HttpError(403, "Accès refusé.")
    return paiement


def initier_paiement(user, commande_id: int, methode: str, note: str = "") -> Paiement:
    commande = _get_commande(user, commande_id)

    if commande.statut == StatutCommande.ANNULEE:
        raise HttpError(400, "Impossible de payer une commande annulée.")

    if commande.statut == StatutCommande.CONFIRMEE:
        raise HttpError(400, "La commande est déjà confirmée.")

    if methode not in MethodePaiement.values:
        raise HttpError(400, f"Méthode de paiement invalide : {methode}.")

    paiement = Paiement.objects.create(
        commande=commande,
        methode=methode,
        montant_mga=commande.total_mga,
        note=note,
    )
    return paiement


def lister_paiements(user, commande_id: int) -> list[Paiement]:
    commande = _get_commande(user, commande_id)
    return list(Paiement.objects.filter(commande=commande).vivants())


def valider_paiement(user, paiement_id: int) -> Paiement:
    paiement = _get_paiement(user, paiement_id)

    if paiement.statut != StatutPaiement.EN_ATTENTE:
        raise HttpError(400, "Seul un paiement en attente peut être validé.")

    if paiement.est_expire:
        paiement.expirer()
        raise HttpError(400, "Paiement expiré (délai dépassé). Initiez une nouvelle tentative.")

    paiement.valider()

    commande = paiement.commande
    if commande.statut == StatutCommande.EN_ATTENTE:
        commande.statut = StatutCommande.CONFIRMEE
        commande.save(update_fields=["statut", "date_mise_a_jour"])

    return paiement


def echouer_paiement(user, paiement_id: int, commentaire: str = "") -> Paiement:
    paiement = _get_paiement(user, paiement_id)

    if paiement.statut != StatutPaiement.EN_ATTENTE:
        raise HttpError(400, "Seul un paiement en attente peut être marqué échoué.")

    paiement.echouer(commentaire=commentaire)
    return paiement


def rembourser_paiement(user, paiement_id: int, commentaire: str = "") -> Paiement:
    paiement = _get_paiement(user, paiement_id)

    if paiement.statut != StatutPaiement.VALIDE:
        raise HttpError(400, "Seul un paiement validé peut être remboursé.")

    paiement.rembourser(commentaire=commentaire, declencheur=Declencheur.UTILISATEUR)

    commande = paiement.commande
    if commande.statut == StatutCommande.CONFIRMEE:
        commande.statut = StatutCommande.EN_ATTENTE
        commande.save(update_fields=["statut", "date_mise_a_jour"])

    return paiement


def lister_historiques(user, paiement_id: int):
    paiement = _get_paiement(user, paiement_id)
    return list(paiement.historiques.all())


def expirer_paiements_expires() -> int:
    """Bulk-expire les paiements EN_ATTENTE dont le délai est dépassé."""
    candidats = Paiement.objects.filter(
        statut=StatutPaiement.EN_ATTENTE,
        expire_le__lt=timezone.now(),
    ).select_related("commande")

    count = 0
    for paiement in candidats:
        paiement.expirer()
        count += 1

    return count
