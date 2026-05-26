from sqlalchemy.orm import Session

from app.schemas import AuthMeResponse, CadastroUsuarioRequest, LoginRequest, TokenResponse, UsuarioResponse
from auth.security import create_access_token
from services.user_service import cadastrar_usuario, autenticar_usuario
from utils.exceptions import ForbiddenError


def cadastro_controller(payload: CadastroUsuarioRequest, db: Session) -> UsuarioResponse:
    usuario = cadastrar_usuario(db, payload)
    return _usuario_response(usuario)


def login_controller(payload: LoginRequest, db: Session) -> TokenResponse:
    usuario = autenticar_usuario(db, payload.email, payload.senha)
    return TokenResponse(
        access_token=create_access_token(str(usuario.id)),
        usuario=_usuario_response(usuario),
    )


def admin_login_controller(payload: LoginRequest, db: Session) -> TokenResponse:
    usuario = autenticar_usuario(db, payload.email, payload.senha)
    if usuario.tipo_usuario != "admin":
        raise ForbiddenError("Acesso permitido apenas para administradores.")
    return TokenResponse(
        access_token=create_access_token(str(usuario.id)),
        usuario=_usuario_response(usuario),
    )


def me_controller(usuario) -> AuthMeResponse:
    return AuthMeResponse(
        usuario=_usuario_response(usuario),
        cliente_id=str(usuario.cliente.id) if usuario.cliente else None,
        prestador_id=str(usuario.prestador.id) if usuario.prestador else None,
        status_validacao_prestador=(
            usuario.prestador.validacao.status_validacao
            if usuario.prestador and usuario.prestador.validacao
            else None
        ),
    )


def _usuario_response(usuario) -> UsuarioResponse:
    return UsuarioResponse(
        id=str(usuario.id),
        nome=usuario.nome,
        email=usuario.email,
        telefone=usuario.telefone,
        tipo_usuario=usuario.tipo_usuario,
        ativo=usuario.ativo,
    )
