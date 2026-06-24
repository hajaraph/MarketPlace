"""
Use cases du module users (couche application).

Les routers Ninja restent minces : ils valident l'entrée (schémas Pydantic),
délèguent ici, puis sérialisent la sortie. Toute la règle métier
d'authentification vit dans ce fichier.
"""
from __future__ import annotations

from django.contrib.auth import authenticate
from django.db import IntegrityError, transaction
from ninja.errors import HttpError
from ninja_jwt.tokens import RefreshToken

from users.models import Utilisateur


def _emettre_tokens(utilisateur: Utilisateur) -> dict[str, str]:
    """Génère une paire access + refresh pour un utilisateur."""
    refresh = RefreshToken.for_user(utilisateur)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


@transaction.atomic
def register(*, email: str, password: str, nom: str, prenom: str,
             telephone: str = "", role: str | None = None) -> dict:
    """Crée un compte puis renvoie l'utilisateur + ses tokens. Fail-fast sur doublon."""
    # Pré-contrôle pour un message ciblé par champ (meilleure UX qu'un 409 générique).
    if Utilisateur.objects.filter(email=email).exists():
        raise HttpError(409, "Un compte existe déjà avec cet email.")
    if Utilisateur.objects.filter(telephone=telephone).exists():
        raise HttpError(409, "Un compte existe déjà avec ce téléphone.")

    extra = {"nom": nom, "prenom": prenom, "telephone": telephone}
    if role is not None:
        extra["role"] = role
    try:
        utilisateur = Utilisateur.objects.create_user(
            email=email, password=password, **extra
        )
    except IntegrityError:
        # Filet de sécurité en cas de course (deux inscriptions simultanées).
        raise HttpError(409, "Un compte existe déjà avec cet email ou ce téléphone.")

    return {"user": utilisateur, **_emettre_tokens(utilisateur)}


def login(*, identifiant: str, password: str) -> dict:
    """
    Authentifie par email OU téléphone + mot de passe. 401 si invalide.

    L'identifiant est traité comme un email s'il contient '@', sinon comme un
    téléphone : on résout alors l'email correspondant avant de déléguer à
    `authenticate` (qui reste basé sur USERNAME_FIELD = email).
    """
    email = identifiant
    if "@" not in identifiant:
        compte = Utilisateur.objects.filter(telephone=identifiant).first()
        if compte is None:
            raise HttpError(401, "Identifiants invalides.")
        email = compte.email

    utilisateur = authenticate(username=email, password=password)
    if utilisateur is None:
        raise HttpError(401, "Identifiants invalides.")
    return {"user": utilisateur, **_emettre_tokens(utilisateur)}


def refresh(*, refresh_token: str) -> dict:
    """Rafraîchit la paire de tokens (rotation gérée par ninja_jwt). 401 si invalide."""
    from ninja_jwt.exceptions import TokenError

    try:
        ancien = RefreshToken(refresh_token)
        nouvel_access = str(ancien.access_token)
        ancien.set_jti()
        ancien.set_exp()
        ancien.set_iat()
        nouveau_refresh = str(ancien)
    except TokenError:
        raise HttpError(401, "Refresh token invalide ou expiré.")
    return {"access": nouvel_access, "refresh": nouveau_refresh}
