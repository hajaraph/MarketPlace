"""
Router d'authentification — mince, délègue aux use cases (users.services).

Routes :
  POST /api/auth/register  → création de compte
  POST /api/auth/login     → connexion
  POST /api/auth/refresh   → rafraîchissement de token
  GET  /api/auth/me        → profil de l'utilisateur connecté (JWT requis)
"""
from ninja import Router
from ninja_jwt.authentication import JWTAuth

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


@router.post("/register", response=AuthResponseOut, auth=None)
def register(request, payload: RegisterIn):
    return services.register(**payload.dict())


@router.post("/login", response=AuthResponseOut, auth=None)
def login(request, payload: LoginIn):
    return services.login(email=payload.email, password=payload.password)


@router.post("/refresh", response=TokenOut, auth=None)
def refresh(request, payload: RefreshIn):
    return services.refresh(refresh_token=payload.refresh)


@router.get("/me", response=UserOut, auth=JWTAuth())
def me(request):
    return request.auth
