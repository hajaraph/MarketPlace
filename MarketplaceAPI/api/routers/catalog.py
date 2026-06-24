"""
Router catalog — produits & médias.

Lecture publique. Écriture authentifiée (JWT) ; permission « propriétaire du
magasin » appliquée dans catalog.services.
"""
from typing import Optional

from ninja import Router
from ninja_jwt.authentication import JWTAuth

from catalog import services
from catalog.schemas import (
    MediaIn,
    MediaOut,
    ProduitIn,
    ProduitOut,
    ProduitUpdate,
)
from shared.api_response import ApiResponse, Envelope

router = Router(tags=["catalog"])


# --- Produits ---------------------------------------------------------------

@router.get("/produits", response={200: Envelope}, auth=None)
def lister_produits(request, magasin_id: Optional[int] = None,
                    categorie: Optional[str] = None,
                    actifs: bool = False, disponibles: bool = False):
    qs = services.lister_produits(
        magasin_id=magasin_id, categorie=categorie,
        actifs_seulement=actifs, disponibles=disponibles,
    )
    data = [ProduitOut.from_orm(p) for p in qs]
    return ApiResponse.success(data=data, meta={"total": len(data)})


@router.get("/produits/{produit_id}", response={200: Envelope}, auth=None)
def get_produit(request, produit_id: int):
    return ApiResponse.success(data=ProduitOut.from_orm(services.get_produit(produit_id)))


@router.post("/produits", response={201: Envelope}, auth=JWTAuth())
def creer_produit(request, payload: ProduitIn):
    produit = services.creer_produit(user=request.auth, data=payload.dict())
    return ApiResponse.created(data=ProduitOut.from_orm(produit), message="Produit créé.")


@router.patch("/produits/{produit_id}", response={200: Envelope}, auth=JWTAuth())
def modifier_produit(request, produit_id: int, payload: ProduitUpdate):
    produit = services.modifier_produit(
        produit_id=produit_id, user=request.auth, data=payload.dict(exclude_unset=True)
    )
    return ApiResponse.success(data=ProduitOut.from_orm(produit), message="Produit mis à jour.")


@router.delete("/produits/{produit_id}", response={200: Envelope}, auth=JWTAuth())
def supprimer_produit(request, produit_id: int):
    services.supprimer_produit(produit_id=produit_id, user=request.auth)
    return ApiResponse.success(message="Produit supprimé.")


# --- Médias -----------------------------------------------------------------

@router.get("/produits/{produit_id}/medias", response={200: Envelope}, auth=None)
def lister_medias(request, produit_id: int):
    data = [MediaOut.from_orm(m) for m in services.lister_medias(produit_id=produit_id)]
    return ApiResponse.success(data=data, meta={"total": len(data)})


@router.post("/produits/{produit_id}/medias", response={201: Envelope}, auth=JWTAuth())
def ajouter_media(request, produit_id: int, payload: MediaIn):
    media = services.ajouter_media(produit_id=produit_id, user=request.auth, data=payload.dict())
    return ApiResponse.created(data=MediaOut.from_orm(media), message="Média ajouté.")


@router.delete("/medias/{media_id}", response={200: Envelope}, auth=JWTAuth())
def supprimer_media(request, media_id: int):
    services.supprimer_media(media_id=media_id, user=request.auth)
    return ApiResponse.success(message="Média supprimé.")
