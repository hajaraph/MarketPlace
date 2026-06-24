"""
Use cases du module catalog.

Règle d'accès : seul le propriétaire du magasin (ou un admin) gère le
catalogue et les médias de ce magasin. Lecture publique.
"""
from __future__ import annotations

from ninja.errors import HttpError

from catalog.models import MediaProduit, Produit
from places.models import Magasin
from users.models import RoleUtilisateur


# --- Helpers ----------------------------------------------------------------

def _est_admin(user) -> bool:
    return bool(user.is_staff or user.role == RoleUtilisateur.ADMIN)


def _get_magasin(magasin_id: int) -> Magasin:
    magasin = Magasin.objects.vivants().filter(pk=magasin_id).first()
    if magasin is None:
        raise HttpError(404, "Magasin introuvable.")
    return magasin


def _get_produit(produit_id: int) -> Produit:
    produit = (Produit.objects.vivants()
               .select_related("magasin").filter(pk=produit_id).first())
    if produit is None:
        raise HttpError(404, "Produit introuvable.")
    return produit


def _exiger_gestion(magasin: Magasin, user) -> None:
    if magasin.proprietaire_id != user.id and not _est_admin(user):
        raise HttpError(403, "Seul le propriétaire du magasin peut gérer son catalogue.")


# --- Produits ---------------------------------------------------------------

def lister_produits(*, magasin_id: int | None = None, categorie: str | None = None,
                    actifs_seulement: bool = False, disponibles: bool = False):
    qs = Produit.objects.vivants().select_related("magasin")
    if magasin_id is not None:
        qs = qs.filter(magasin_id=magasin_id)
    if categorie is not None:
        qs = qs.filter(categorie=categorie)
    if actifs_seulement:
        qs = qs.filter(est_actif=True)
    if disponibles:
        qs = qs.filter(est_actif=True, quantite__gt=0)
    return qs


def get_produit(produit_id: int) -> Produit:
    return _get_produit(produit_id)


def creer_produit(*, user, data: dict) -> Produit:
    magasin = _get_magasin(data.pop("magasin_id"))
    _exiger_gestion(magasin, user)
    return Produit.objects.create(magasin=magasin, **data)


def modifier_produit(*, produit_id: int, user, data: dict) -> Produit:
    produit = _get_produit(produit_id)
    _exiger_gestion(produit.magasin, user)
    for champ, valeur in data.items():
        setattr(produit, champ, valeur)
    produit.save()
    return produit


def supprimer_produit(*, produit_id: int, user) -> None:
    produit = _get_produit(produit_id)
    _exiger_gestion(produit.magasin, user)
    produit.supprimer()


# --- Médias -----------------------------------------------------------------

def lister_medias(*, produit_id: int):
    _get_produit(produit_id)  # 404 si le produit n'existe pas
    return MediaProduit.objects.vivants().filter(produit_id=produit_id)


def ajouter_media(*, produit_id: int, user, data: dict) -> MediaProduit:
    produit = _get_produit(produit_id)
    _exiger_gestion(produit.magasin, user)
    return MediaProduit.objects.create(produit=produit, **data)


def supprimer_media(*, media_id: int, user) -> None:
    media = (MediaProduit.objects.vivants()
             .select_related("produit__magasin").filter(pk=media_id).first())
    if media is None:
        raise HttpError(404, "Média introuvable.")
    _exiger_gestion(media.produit.magasin, user)
    media.supprimer()
