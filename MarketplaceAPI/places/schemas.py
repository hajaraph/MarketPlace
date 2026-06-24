"""Schémas Pydantic du module places."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from ninja import Schema

from places.models import CategorieMagasin

# Horaires : { "1".."7" : [["08:00","18:00"], ...] }
Horaires = dict[str, list[list[str]]]


# =========================================================
# Inputs
# =========================================================

class _EmplacementInBase(Schema):
    nom: str
    description: str = ""
    banniere: str = ""
    adresse: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    horaires_ouverture: Horaires = {}


class MagasinIn(_EmplacementInBase):
    categorie: CategorieMagasin = CategorieMagasin.AUTRE
    etage: str = ""
    numero_local: str = ""
    centre_commercial_id: Optional[int] = None


class MagasinUpdate(Schema):
    nom: Optional[str] = None
    description: Optional[str] = None
    banniere: Optional[str] = None
    adresse: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    horaires_ouverture: Optional[Horaires] = None
    categorie: Optional[CategorieMagasin] = None
    etage: Optional[str] = None
    numero_local: Optional[str] = None
    centre_commercial_id: Optional[int] = None


class CentreCommercialIn(_EmplacementInBase):
    nombre_etages: int = 1
    parking_disponible: bool = False


class CentreCommercialUpdate(Schema):
    nom: Optional[str] = None
    description: Optional[str] = None
    banniere: Optional[str] = None
    adresse: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    horaires_ouverture: Optional[Horaires] = None
    nombre_etages: Optional[int] = None
    parking_disponible: Optional[bool] = None


# =========================================================
# Outputs
# =========================================================

class _EmplacementOutBase(Schema):
    id: int
    nom: str
    description: str
    banniere: str
    adresse: str
    latitude: Optional[float]
    longitude: Optional[float]
    est_ouvert: Optional[bool]
    est_valide: bool
    date_validation: Optional[datetime]
    date_creation: datetime


class MagasinOut(_EmplacementOutBase):
    categorie: CategorieMagasin
    etage: str
    numero_local: str
    proprietaire_id: int
    centre_commercial_id: Optional[int]


class CentreCommercialOut(_EmplacementOutBase):
    nombre_etages: int
    parking_disponible: bool
