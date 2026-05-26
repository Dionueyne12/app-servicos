from sqlalchemy.orm import Session

from app.schemas import CadastroPerfilRequest, CadastroUsuarioRequest, UsuarioResponse
from services.user_service import cadastrar_usuario


def cadastro_cliente_controller(payload: CadastroPerfilRequest, db: Session) -> UsuarioResponse:
    usuario = cadastrar_usuario(
        db,
        CadastroUsuarioRequest(**payload.model_dump(), tipo_usuario="cliente"),
    )
    return UsuarioResponse(
        id=str(usuario.id),
        nome=usuario.nome,
        email=usuario.email,
        telefone=usuario.telefone,
        tipo_usuario=usuario.tipo_usuario,
        ativo=usuario.ativo,
    )
