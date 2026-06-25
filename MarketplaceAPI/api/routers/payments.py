"""Router payments — tentatives de paiement par commande."""
from ninja import Router
from ninja_jwt.authentication import JWTAuth

from payments import services
from payments.schemas import (
    EchecIn,
    HistoriquePaiementOut,
    PaiementIn,
    PaiementOut,
    RemboursementIn,
)
from shared.api_response import ApiResponse, Envelope

router = Router(tags=["payments"])


@router.get("/commandes/{commande_id}/paiements", response={200: Envelope}, auth=JWTAuth())
def lister_paiements(request, commande_id: int):
    paiements = services.lister_paiements(request.auth, commande_id)
    return ApiResponse.success(
        data=[PaiementOut.model_validate(p) for p in paiements],
        meta={"total": len(paiements)},
    )


@router.post("/commandes/{commande_id}/paiements", response={201: Envelope}, auth=JWTAuth())
def initier_paiement(request, commande_id: int, payload: PaiementIn):
    paiement = services.initier_paiement(
        request.auth, commande_id, payload.methode, payload.note
    )
    return ApiResponse.created(
        data=PaiementOut.model_validate(paiement),
        message="Paiement initié.",
    )


@router.post("/paiements/{paiement_id}/valider", response={200: Envelope}, auth=JWTAuth())
def valider_paiement(request, paiement_id: int):
    paiement = services.valider_paiement(request.auth, paiement_id)
    return ApiResponse.success(
        data=PaiementOut.model_validate(paiement),
        message="Paiement validé.",
    )


@router.post("/paiements/{paiement_id}/echouer", response={200: Envelope}, auth=JWTAuth())
def echouer_paiement(request, paiement_id: int, payload: EchecIn):
    paiement = services.echouer_paiement(request.auth, paiement_id, payload.commentaire)
    return ApiResponse.success(
        data=PaiementOut.model_validate(paiement),
        message="Paiement marqué échoué.",
    )


@router.post("/paiements/{paiement_id}/rembourser", response={200: Envelope}, auth=JWTAuth())
def rembourser_paiement(request, paiement_id: int, payload: RemboursementIn):
    paiement = services.rembourser_paiement(request.auth, paiement_id, payload.commentaire)
    return ApiResponse.success(
        data=PaiementOut.model_validate(paiement),
        message="Paiement remboursé.",
    )


@router.get("/paiements/{paiement_id}/historique", response={200: Envelope}, auth=JWTAuth())
def lister_historiques(request, paiement_id: int):
    historiques = services.lister_historiques(request.auth, paiement_id)
    return ApiResponse.success(
        data=[HistoriquePaiementOut.model_validate(h) for h in historiques],
        meta={"total": len(historiques)},
    )
