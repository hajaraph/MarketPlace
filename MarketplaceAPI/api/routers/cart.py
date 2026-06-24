"""Router cart — panier transitoire."""
from ninja import Router
from ninja_jwt.authentication import JWTAuth

from cart import services
from cart.schemas import LignePanierIn, LignePanierOut, LignePanierUpdate, PanierOut
from shared.api_response import ApiResponse, Envelope

router = Router(tags=["cart"])


@router.get("/panier", response={200: Envelope}, auth=JWTAuth())
def get_panier(request):
    panier = services.get_panier(request.auth)
    lignes = panier.lignes.all()
    return ApiResponse.success(
        data=PanierOut(
            id=panier.id,
            utilisateur_id=panier.utilisateur_id,
            total=panier.calculer_total(),
            nombre_articles=lignes.count(),
            date_creation=panier.date_creation,
        ),
        meta={"articles": [LignePanierOut.from_orm(l) for l in lignes]},
    )


@router.post("/panier/articles", response={201: Envelope}, auth=JWTAuth())
def ajouter_article(request, payload: LignePanierIn):
    ligne = services.ajouter_ligne(request.auth, payload.produit_id, payload.quantite)
    return ApiResponse.created(data=LignePanierOut.from_orm(ligne), message="Article ajouté.")


@router.patch("/panier/articles/{ligne_id}", response={200: Envelope}, auth=JWTAuth())
def modifier_article(request, ligne_id: int, payload: LignePanierUpdate):
    ligne = services.modifier_ligne(request.auth, ligne_id, payload.quantite)
    return ApiResponse.success(data=LignePanierOut.from_orm(ligne), message="Quantité mise à jour.")


@router.delete("/panier/articles/{ligne_id}", response={200: Envelope}, auth=JWTAuth())
def retirer_article(request, ligne_id: int):
    services.retirer_ligne(request.auth, ligne_id)
    return ApiResponse.success(message="Article retiré du panier.")


@router.post("/panier/vider", response={200: Envelope}, auth=JWTAuth())
def vider_panier(request):
    services.vider_panier(request.auth)
    return ApiResponse.success(message="Panier vidé.")
