from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas import AuthMeResponse, CadastroUsuarioRequest, LoginRequest, TokenResponse, UsuarioResponse
from auth.dependencies import get_current_user
from controllers.auth_controller import cadastro_controller, login_controller, me_controller
from database.session import get_db
from models import Usuario


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/cadastro", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def cadastrar(payload: CadastroUsuarioRequest, db: Session = Depends(get_db)) -> UsuarioResponse:
    return cadastro_controller(payload, db)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return login_controller(payload, db)


@router.get("/me", response_model=AuthMeResponse)
def me(usuario: Usuario = Depends(get_current_user)) -> AuthMeResponse:
    return me_controller(usuario)
