"""Schémas Pydantic du module orders."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import field_validator

from ninja import Schema


class AdresseLivraisonIn(Schema):
    adresse_complete: str
    ville: str
    quartier: str = ""
    code_postal: str = ""
    complement: str = ""
    telephone: str
    est_par_defaut: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class AdresseLivraisonOut(Schema):
    id: int
    adresse_complete: str
    ville: str
    quartier: str
    code_postal: str
    complement: str
    telephone: str
    est_par_defaut: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    est_geolocalise: bool = False
    date_creation: datetime


class LigneCommandeOut(Schema):
    id: int
    nom_produit_snapshot: str
    quantite: int
    prix_unitaire_mga: Decimal
    sous_total: Decimal
    date_creation: datetime


class CommandeOut(Schema):
    id: int
    utilisateur_id: int
    statut: str
    adresse_snapshot: str
    total_mga: Decimal
    date_creation: datetime
    lignes: list[LigneCommandeOut] = []


class CommandeCreateIn(Schema):
    adresse_id: Optional[int] = None
