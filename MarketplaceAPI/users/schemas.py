"""
Schémas Pydantic du module users.

- Schemas *In  : validation des données entrantes (payload des requêtes)
- Schemas *Out : sérialisation des données sortantes (réponses API)
"""
from datetime import datetime
from typing import Optional

from ninja import Schema

from users.models import RoleUtilisateur


# =========================================================
# Inputs
# =========================================================

class RegisterIn(Schema):
    """Payload de création de compte."""
    email: str
    password: str
    nom: str
    prenom: str
    telephone: str
    role: RoleUtilisateur = RoleUtilisateur.CLIENT


class LoginIn(Schema):
    """Payload de connexion : identifiant = email OU téléphone."""
    identifiant: str
    password: str


class RefreshIn(Schema):
    """Payload de rafraîchissement de token."""
    refresh: str


# =========================================================
# Outputs
# =========================================================

class UserOut(Schema):
    """Représentation publique d'un utilisateur."""
    id: int
    email: str
    nom: str
    prenom: str
    telephone: str
    photo_profil: Optional[str] = None
    role: RoleUtilisateur
    date_creation: datetime

    @staticmethod
    def resolve_photo_profil(obj):
        # URLField vide → on renvoie null plutôt qu'une chaîne vide
        return obj.photo_profil or None


class TokenOut(Schema):
    """Réponse d'authentification : paire access + refresh."""
    access: str
    refresh: str


class AuthResponseOut(Schema):
    """Réponse complète de login/register : utilisateur + tokens."""
    user: UserOut
    access: str
    refresh: str
