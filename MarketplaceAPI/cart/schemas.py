"""Schémas Pydantic du module cart."""
from __future__ import annotations

from datetime import datetime

from ninja import Schema


class LignePanierIn(Schema):
    produit_id: int
    quantite: int = 1


class LignePanierUpdate(Schema):
    quantite: int


class LignePanierOut(Schema):
    id: int
    produit_id: int
    quantite: int
    sous_total: float
    date_creation: datetime


class PanierOut(Schema):
    id: int
    utilisateur_id: int
    total: float
    nombre_articles: int
    date_creation: datetime
