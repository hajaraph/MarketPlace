"""Schémas Pydantic du module payments."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from ninja import Schema


class PaiementIn(Schema):
    methode: str
    note: str = ""


class EchecIn(Schema):
    commentaire: str = ""


class RemboursementIn(Schema):
    commentaire: str = ""


class PaiementOut(Schema):
    id: int
    commande_id: int
    methode: str
    statut: str
    montant_mga: Decimal
    reference_transaction: str
    note: str
    expire_le: datetime
    date_paiement: Optional[datetime] = None
    date_creation: datetime


class HistoriquePaiementOut(Schema):
    id: int
    paiement_id: int
    statut_avant: str
    statut_apres: str
    declencheur: str
    commentaire: str
    date_creation: datetime
