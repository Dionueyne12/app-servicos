from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from auth.security import decode_access_token
from database.session import get_db
from models import Usuario
from utils.exceptions import ForbiddenError, UnauthorizedError


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    if credentials is None:
        raise UnauthorizedError("Token de acesso nao informado.")

    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Token de acesso invalido.")

    try:
        user_uuid = UUID(user_id)
    except ValueError as exc:
        raise UnauthorizedError("Token de acesso invalido.") from exc

    usuario = db.scalar(select(Usuario).where(Usuario.id == user_uuid, Usuario.ativo.is_(True)))
    if usuario is None:
        raise UnauthorizedError("Usuario nao encontrado ou inativo.")

    return usuario


def require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.tipo_usuario != "admin":
        raise ForbiddenError("Acesso permitido apenas para administradores.")
    return current_user


def require_cliente(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.tipo_usuario != "cliente":
        raise UnauthorizedError("Acesso permitido apenas para clientes.")
    return current_user


def require_prestador(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.tipo_usuario != "prestador":
        raise UnauthorizedError("Acesso permitido apenas para prestadores.")
    return current_user
