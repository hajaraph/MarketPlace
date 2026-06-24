"""
Use cases du module places.

Règles d'accès :
- Création magasin : tout utilisateur authentifié (il en devient propriétaire).
- Modification / suppression magasin : propriétaire OU admin.
- Centre commercial (création/modif/suppression) : admin uniquement.
- Validation d'un emplacement : admin uniquement.
"""
from __future__ import annotations

from django.db.models import Model
from ninja.errors import HttpError

from places.models import CentreCommercial, Magasin
from users.models import RoleUtilisateur


# --- Helpers ----------------------------------------------------------------

def _est_admin(user) -> bool:
    return bool(user.is_staff or user.role == RoleUtilisateur.ADMIN)


def _exiger_admin(user) -> None:
    if not _est_admin(user):
        raise HttpError(403, "Action réservée aux administrateurs.")


def _exiger_vendeur(user) -> None:
    if not (user.role == RoleUtilisateur.VENDEUR or _est_admin(user)):
        raise HttpError(403, "Seul un vendeur peut créer un emplacement.")


def _get_vivant(model: type[Model], pk: int):
    obj = model.objects.vivants().filter(pk=pk).first()
    if obj is None:
        raise HttpError(404, f"{model._meta.verbose_name} introuvable.")
    return obj


def _resoudre_centre(centre_id: int | None) -> CentreCommercial | None:
    if centre_id is None:
        return None
    return _get_vivant(CentreCommercial, centre_id)


# --- Magasins ---------------------------------------------------------------

def lister_magasins(*, centre_id: int | None = None,
                    categorie: str | None = None, valides_seulement: bool = False):
    qs = Magasin.objects.vivants().select_related("centre_commercial", "proprietaire")
    if centre_id is not None:
        qs = qs.filter(centre_commercial_id=centre_id)
    if categorie is not None:
        qs = qs.filter(categorie=categorie)
    if valides_seulement:
        qs = qs.filter(est_valide=True)
    return qs


def get_magasin(magasin_id: int) -> Magasin:
    return _get_vivant(Magasin, magasin_id)


def creer_magasin(*, proprietaire, data: dict) -> Magasin:
    _exiger_vendeur(proprietaire)
    centre = _resoudre_centre(data.pop("centre_commercial_id", None))
    return Magasin.objects.create(proprietaire=proprietaire, centre_commercial=centre, **data)


def modifier_magasin(*, magasin_id: int, user, data: dict) -> Magasin:
    magasin = _get_vivant(Magasin, magasin_id)
    if magasin.proprietaire_id != user.id and not _est_admin(user):
        raise HttpError(403, "Seul le propriétaire ou un admin peut modifier ce magasin.")

    if "centre_commercial_id" in data:
        magasin.centre_commercial = _resoudre_centre(data.pop("centre_commercial_id"))
    for champ, valeur in data.items():
        setattr(magasin, champ, valeur)
    magasin.save()
    return magasin


def supprimer_magasin(*, magasin_id: int, user) -> None:
    magasin = _get_vivant(Magasin, magasin_id)
    if magasin.proprietaire_id != user.id and not _est_admin(user):
        raise HttpError(403, "Seul le propriétaire ou un admin peut supprimer ce magasin.")
    magasin.supprimer()


# --- Centres commerciaux ----------------------------------------------------

def lister_centres():
    return CentreCommercial.objects.vivants()


def get_centre(centre_id: int) -> CentreCommercial:
    return _get_vivant(CentreCommercial, centre_id)


def creer_centre(*, user, data: dict) -> CentreCommercial:
    _exiger_vendeur(user)
    return CentreCommercial.objects.create(**data)


def modifier_centre(*, centre_id: int, user, data: dict) -> CentreCommercial:
    _exiger_admin(user)
    centre = _get_vivant(CentreCommercial, centre_id)
    for champ, valeur in data.items():
        setattr(centre, champ, valeur)
    centre.save()
    return centre


def supprimer_centre(*, centre_id: int, user) -> None:
    _exiger_admin(user)
    _get_vivant(CentreCommercial, centre_id).supprimer()


# --- Validation administrateur ---------------------------------------------

def valider_magasin(*, magasin_id: int, admin) -> Magasin:
    _exiger_admin(admin)
    magasin = _get_vivant(Magasin, magasin_id)
    magasin.valider(par=admin)
    return magasin


def valider_centre(*, centre_id: int, admin) -> CentreCommercial:
    _exiger_admin(admin)
    centre = _get_vivant(CentreCommercial, centre_id)
    centre.valider(par=admin)
    return centre
