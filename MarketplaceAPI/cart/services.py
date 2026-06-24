"""Use cases du module cart."""
from __future__ import annotations

from ninja.errors import HttpError

from cart.models import LignePanier, Panier
from catalog.models import Produit


def _get_ou_creer_panier(user) -> Panier:
    panier, _ = Panier.objects.get_or_create(utilisateur=user)
    return panier


def _get_produit(produit_id: int) -> Produit:
    try:
        p = Produit.objects.vivants().get(pk=produit_id)
    except Produit.DoesNotExist:
        raise HttpError(404, "Produit introuvable.")
    if not p.est_disponible:
        raise HttpError(400, "Ce produit n'est pas disponible.")
    return p


def get_panier(user) -> Panier:
    return _get_ou_creer_panier(user)


def ajouter_ligne(user, produit_id: int, quantite: int) -> LignePanier:
    panier = _get_ou_creer_panier(user)
    produit = _get_produit(produit_id)
    if quantite <= 0:
        raise HttpError(400, "La quantité doit être positive.")
    if quantite > produit.quantite:
        raise HttpError(400, f"Stock insuffisant. Disponible : {produit.quantite}.")
    ligne, created = LignePanier.objects.get_or_create(
        panier=panier, produit=produit,
        defaults={"quantite": quantite},
    )
    if not created:
        ligne.quantite = quantite
        ligne.save()
    return ligne


def modifier_ligne(user, ligne_id: int, quantite: int) -> LignePanier:
    panier = _get_ou_creer_panier(user)
    try:
        ligne = panier.lignes.get(pk=ligne_id)
    except LignePanier.DoesNotExist:
        raise HttpError(404, "Ligne introuvable.")
    if quantite <= 0:
        raise HttpError(400, "La quantité doit être positive.")
    if quantite > ligne.produit.quantite:
        raise HttpError(400, f"Stock insuffisant. Disponible : {ligne.produit.quantite}.")
    ligne.quantite = quantite
    ligne.save()
    return ligne


def retirer_ligne(user, ligne_id: int) -> None:
    panier = _get_ou_creer_panier(user)
    try:
        ligne = panier.lignes.get(pk=ligne_id)
        ligne.delete()
    except LignePanier.DoesNotExist:
        raise HttpError(404, "Ligne introuvable.")


def vider_panier(user) -> None:
    panier = _get_ou_creer_panier(user)
    panier.vider()
