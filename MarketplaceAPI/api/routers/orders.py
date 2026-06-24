"""Router orders — commandes + adresses de livraison."""
from ninja import Router
from ninja_jwt.authentication import JWTAuth

from orders import services
from orders.schemas import (
    AdresseLivraisonIn,
    AdresseLivraisonOut,
    CommandeCreateIn,
    CommandeOut,
)
from shared.api_response import ApiResponse, Envelope

router = Router(tags=["orders"])


# --- Adresses de livraison -----------------------------------------------

@router.get("/adresses", response={200: Envelope}, auth=JWTAuth())
def lister_adresses(request):
    adresses = services.lister_adresses(request.auth)
    return ApiResponse.success(
        meta={"adresses": [AdresseLivraisonOut.from_orm(a) for a in adresses]},
    )


@router.post("/adresses", response={201: Envelope}, auth=JWTAuth())
def creer_adresse(request, payload: AdresseLivraisonIn):
    adresse = services.creer_adresse(request.auth, payload.dict())
    return ApiResponse.created(data=AdresseLivraisonOut.from_orm(adresse))


@router.delete("/adresses/{adresse_id}", response={200: Envelope}, auth=JWTAuth())
def supprimer_adresse(request, adresse_id: int):
    services.supprimer_adresse(request.auth, adresse_id)
    return ApiResponse.success(message="Adresse supprimée.")


# --- Commandes -----------------------------------------------------------

@router.get("/commandes", response={200: Envelope}, auth=JWTAuth())
def lister_commandes(request):
    commandes = services.lister_commandes(request.auth)
    return ApiResponse.success(
        meta={
            "commandes": [CommandeOut.from_orm(c) for c in commandes]
        },
    )


@router.get("/commandes/{commande_id}", response={200: Envelope}, auth=JWTAuth())
def obtenir_commande(request, commande_id: int):
    commande = services.obtenir_commande(request.auth, commande_id)
    return ApiResponse.success(data=CommandeOut.from_orm(commande))


@router.post("/commandes", response={201: Envelope}, auth=JWTAuth())
def passer_commande(request, payload: CommandeCreateIn):
    commande = services.passer_commande(request.auth, payload.adresse_id)
    return ApiResponse.created(
        data=CommandeOut.from_orm(commande),
        message="Commande créée.",
    )


@router.post("/commandes/{commande_id}/annuler", response={200: Envelope}, auth=JWTAuth())
def annuler_commande(request, commande_id: int):
    commande = services.annuler_commande(request.auth, commande_id)
    return ApiResponse.success(
        data=CommandeOut.from_orm(commande),
        message="Commande annulée.",
    )
