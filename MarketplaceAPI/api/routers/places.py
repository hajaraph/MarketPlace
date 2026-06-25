"""
Router places — magasins & centres commerciaux.

Lecture publique (carte). Écriture authentifiée (JWT) ; les permissions fines
(propriétaire / admin) sont appliquées dans places.services.
"""
from typing import Optional

from ninja import Router
from ninja_jwt.authentication import JWTAuth

from places import services
from places.schemas import (
    CentreCommercialIn,
    CentreCommercialOut,
    CentreCommercialUpdate,
    MagasinIn,
    MagasinOut,
    MagasinUpdate,
)
from shared.api_response import ApiResponse, Envelope

router = Router(tags=["places"])


# --- Magasins ---------------------------------------------------------------

@router.get("/magasins", response={200: Envelope}, auth=None)
def lister_magasins(request, centre_id: Optional[int] = None,
                    categorie: Optional[str] = None, valides: bool = False):
    qs = services.lister_magasins(
        centre_id=centre_id, categorie=categorie, valides_seulement=valides
    )
    data = [MagasinOut.model_validate(m) for m in qs]
    return ApiResponse.success(data=data, meta={"total": len(data)})


@router.get("/magasins/{magasin_id}", response={200: Envelope}, auth=None)
def get_magasin(request, magasin_id: int):
    return ApiResponse.success(data=MagasinOut.model_validate(services.get_magasin(magasin_id)))


@router.post("/magasins", response={201: Envelope}, auth=JWTAuth())
def creer_magasin(request, payload: MagasinIn):
    magasin = services.creer_magasin(proprietaire=request.auth, data=payload.dict())
    return ApiResponse.created(data=MagasinOut.model_validate(magasin), message="Magasin créé.")


@router.patch("/magasins/{magasin_id}", response={200: Envelope}, auth=JWTAuth())
def modifier_magasin(request, magasin_id: int, payload: MagasinUpdate):
    magasin = services.modifier_magasin(
        magasin_id=magasin_id, user=request.auth, data=payload.dict(exclude_unset=True)
    )
    return ApiResponse.success(data=MagasinOut.model_validate(magasin), message="Magasin mis à jour.")


@router.delete("/magasins/{magasin_id}", response={200: Envelope}, auth=JWTAuth())
def supprimer_magasin(request, magasin_id: int):
    services.supprimer_magasin(magasin_id=magasin_id, user=request.auth)
    return ApiResponse.success(message="Magasin supprimé.")


@router.post("/magasins/{magasin_id}/valider", response={200: Envelope}, auth=JWTAuth())
def valider_magasin(request, magasin_id: int):
    magasin = services.valider_magasin(magasin_id=magasin_id, admin=request.auth)
    return ApiResponse.success(data=MagasinOut.model_validate(magasin), message="Magasin validé.")


# --- Centres commerciaux ----------------------------------------------------

@router.get("/centres", response={200: Envelope}, auth=None)
def lister_centres(request):
    data = [CentreCommercialOut.model_validate(c) for c in services.lister_centres()]
    return ApiResponse.success(data=data, meta={"total": len(data)})


@router.get("/centres/{centre_id}", response={200: Envelope}, auth=None)
def get_centre(request, centre_id: int):
    return ApiResponse.success(data=CentreCommercialOut.model_validate(services.get_centre(centre_id)))


@router.post("/centres", response={201: Envelope}, auth=JWTAuth())
def creer_centre(request, payload: CentreCommercialIn):
    centre = services.creer_centre(user=request.auth, data=payload.dict())
    return ApiResponse.created(data=CentreCommercialOut.model_validate(centre), message="Centre créé.")


@router.patch("/centres/{centre_id}", response={200: Envelope}, auth=JWTAuth())
def modifier_centre(request, centre_id: int, payload: CentreCommercialUpdate):
    centre = services.modifier_centre(
        centre_id=centre_id, user=request.auth, data=payload.dict(exclude_unset=True)
    )
    return ApiResponse.success(data=CentreCommercialOut.model_validate(centre), message="Centre mis à jour.")


@router.delete("/centres/{centre_id}", response={200: Envelope}, auth=JWTAuth())
def supprimer_centre(request, centre_id: int):
    services.supprimer_centre(centre_id=centre_id, user=request.auth)
    return ApiResponse.success(message="Centre supprimé.")


@router.post("/centres/{centre_id}/valider", response={200: Envelope}, auth=JWTAuth())
def valider_centre(request, centre_id: int):
    centre = services.valider_centre(centre_id=centre_id, admin=request.auth)
    return ApiResponse.success(data=CentreCommercialOut.model_validate(centre), message="Centre validé.")
