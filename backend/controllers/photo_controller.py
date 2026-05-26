from sqlalchemy.orm import Session

from app.schemas import FotoServicoResponse
from models import FotoServico, Usuario
from services.photo_service import excluir_foto_servico, listar_fotos_solicitacao, salvar_foto_solicitacao


def upload_foto_controller(
    solicitacao_id: str,
    usuario: Usuario,
    db: Session,
    arquivo: bytes,
    nome_original: str,
    mime_type: str,
    tipo_foto: str,
    descricao: str | None,
) -> FotoServicoResponse:
    foto = salvar_foto_solicitacao(
        db,
        solicitacao_id,
        usuario,
        arquivo,
        nome_original,
        mime_type,
        tipo_foto,
        descricao,
    )
    return _to_response(foto)


def listar_fotos_controller(
    solicitacao_id: str,
    usuario: Usuario,
    db: Session,
) -> list[FotoServicoResponse]:
    return [_to_response(foto) for foto in listar_fotos_solicitacao(db, solicitacao_id, usuario)]


def excluir_foto_controller(foto_id: str, usuario: Usuario, db: Session) -> FotoServicoResponse:
    return _to_response(excluir_foto_servico(db, foto_id, usuario))


def _to_response(foto: FotoServico) -> FotoServicoResponse:
    return FotoServicoResponse(
        id=str(foto.id),
        solicitacao_id=str(foto.solicitacao_id),
        usuario_id=str(foto.usuario_id),
        caminho_arquivo=foto.caminho_arquivo,
        nome_original=foto.nome_original,
        mime_type=foto.mime_type,
        tamanho_bytes=foto.tamanho_bytes,
        tipo_foto=foto.tipo_foto,
        descricao=foto.descricao,
        created_at=foto.created_at.isoformat(),
    )
