"""
Router d'authentification — mince, délègue aux use cases (users.services).

Réponses enveloppées via shared.api_response.ApiResponse :
    { success, timestamp, data, message?, error?, meta? }

Routes :
  POST /api/auth/register  → création de compte (201)
  POST /api/auth/login     → connexion
  POST /api/auth/refresh   → rafraîchissement de token
  GET  /api/auth/me        → profil de l'utilisateur connecté (JWT requis)
"""
from ninja import Router
from ninja_jwt.authentication import JWTAuth

from shared.api_response import ApiResponse, Envelope
from users import services
from users.schemas import (
    AuthResponseOut,
    LoginIn,
    RefreshIn,
    RegisterIn,
    TokenOut,
    UserOut,
)

router = Router(tags=["auth"])


@router.post("/register", response={201: Envelope}, auth=None)
def register(request, payload: RegisterIn):
    res = services.register(**payload.dict())
    data = AuthResponseOut(
        user=UserOut.from_orm(res["user"]),
        access=res["access"],
        refresh=res["refresh"],
    )
    return ApiResponse.created(data=data, message="Compte créé avec succès.")


@router.post("/login", response={200: Envelope}, auth=None)
def login(request, payload: LoginIn):
    res = services.login(email=payload.email, password=payload.password)
    data = AuthResponseOut(
        user=UserOut.from_orm(res["user"]),
        access=res["access"],
        refresh=res["refresh"],
    )
    return ApiResponse.success(data=data, message="Connexion réussie.")


@router.post("/refresh", response={200: Envelope}, auth=None)
def refresh(request, payload: RefreshIn):
    res = services.refresh(refresh_token=payload.refresh)
    data = TokenOut(access=res["access"], refresh=res["refresh"])
    return ApiResponse.success(data=data)


@router.get("/me", response={200: Envelope}, auth=JWTAuth())
def me(request):
    return ApiResponse.success(data=UserOut.from_orm(request.auth))
