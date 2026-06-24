"""Schémas Pydantic du module catalog."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from ninja import Schema

from catalog.models import CategorieProduit, EtatStock


# =========================================================
# Produit
# =========================================================

class ProduitIn(Schema):
    magasin_id: int
    nom: str
    description: str = ""
    categorie: CategorieProduit = CategorieProduit.AUTRE
    prix_mga: float
    quantite: int = 0
    est_actif: bool = True


class ProduitUpdate(Schema):
    nom: Optional[str] = None
    description: Optional[str] = None
    categorie: Optional[CategorieProduit] = None
    prix_mga: Optional[float] = None
    quantite: Optional[int] = None
    est_actif: Optional[bool] = None


class ProduitOut(Schema):
    id: int
    magasin_id: int
    nom: str
    description: str
    categorie: CategorieProduit
    prix_mga: float
    quantite: int
    etat_stock: EtatStock
    est_actif: bool
    est_disponible: bool
    date_creation: datetime


# =========================================================
# MediaProduit
# =========================================================

class MediaIn(Schema):
    url_photo: str
    legende: str = ""
    ordre: int = 0


class MediaOut(Schema):
    id: int
    produit_id: int
    url_photo: str
    legende: str
    ordre: int
    date_creation: datetime
