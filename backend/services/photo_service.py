from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from models import FotoServico, SolicitacaoServico, Usuario
from utils.exceptions import BadRequestError, UnauthorizedError


ALLOWED_MIME_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
ALLOWED_PHOTO_TYPES = {
    "problema",
    "material_cliente",
    "antes_servico",
    "depois_servico",
    "comprovante_material",
}


def salvar_foto_solicitacao(
    db: Session,
    solicitacao_id: str,
    usuario: Usuario,
    arquivo: bytes,
    nome_original: str,
    mime_type: str,
    tipo_foto: str,
    descricao: str | None,
) -> FotoServico:
    solicitacao = _buscar_solicitacao(db, solicitacao_id)
    _garantir_permissao_foto(solicitacao, usuario, escrita=True)
    _validar_upload(arquivo, nome_original, mime_type, tipo_foto)

    extension = ALLOWED_MIME_TYPES[mime_type]
    safe_name = f"{uuid4()}{extension}"
    target_dir = settings.upload_dir / "solicitacoes" / str(solicitacao.id)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / safe_name
    target_path.write_bytes(arquivo)

    relative_path = Path("uploads") / "solicitacoes" / str(solicitacao.id) / safe_name
    foto = FotoServico(
        solicitacao_id=solicitacao.id,
        enviado_por_usuario_id=usuario.id,
        usuario_id=usuario.id,
        url=str(relative_path).replace("\\", "/"),
        caminho_arquivo=str(relative_path).replace("\\", "/"),
        nome_original=nome_original.strip(),
        mime_type=mime_type,
        tamanho_bytes=len(arquivo),
        tipo_foto=tipo_foto,
        descricao=descricao,
        created_by_usuario_id=usuario.id,
    )
    db.add(foto)
    db.commit()
    db.refresh(foto)
    return foto


def listar_fotos_solicitacao(db: Session, solicitacao_id: str, usuario: Usuario) -> list[FotoServico]:
    solicitacao = _buscar_solicitacao(db, solicitacao_id)
    _garantir_permissao_foto(solicitacao, usuario, escrita=False)
    return list(
        db.scalars(
            select(FotoServico)
            .where(
                FotoServico.solicitacao_id == solicitacao.id,
                FotoServico.deleted_at.is_(None),
            )
            .order_by(FotoServico.created_at.desc())
        )
    )


def excluir_foto_servico(db: Session, foto_id: str, usuario: Usuario) -> FotoServico:
    foto = db.get(FotoServico, _parse_uuid(foto_id, "Foto invalida."))
    if foto is None or foto.deleted_at is not None:
        raise BadRequestError("Foto nao encontrada.")

    solicitacao = _buscar_solicitacao(db, str(foto.solicitacao_id))
    if usuario.tipo_usuario != "admin" and foto.usuario_id != usuario.id:
        _garantir_permissao_foto(solicitacao, usuario, escrita=True)
        if foto.usuario_id != usuario.id:
            raise UnauthorizedError("Usuario nao pode excluir esta foto.")

    now = datetime.now(timezone.utc)
    foto.deleted_at = now
    foto.deleted_by_usuario_id = usuario.id
    foto.updated_by_usuario_id = usuario.id
    db.commit()
    db.refresh(foto)
    return foto


def _buscar_solicitacao(db: Session, solicitacao_id: str) -> SolicitacaoServico:
    solicitacao = db.get(SolicitacaoServico, _parse_uuid(solicitacao_id, "Solicitacao invalida."))
    if solicitacao is None or solicitacao.deleted_at is not None:
        raise BadRequestError("Solicitacao nao encontrada.")
    return solicitacao


def _garantir_permissao_foto(solicitacao: SolicitacaoServico, usuario: Usuario, escrita: bool) -> None:
    if usuario.tipo_usuario == "admin":
        return
    if usuario.tipo_usuario == "cliente" and usuario.cliente and solicitacao.cliente_id == usuario.cliente.id:
        return
    if (
        usuario.tipo_usuario == "prestador"
        and usuario.prestador
        and solicitacao.prestador_id == usuario.prestador.id
    ):
        return
    if escrita:
        raise UnauthorizedError("Usuario nao pode enviar foto para esta solicitacao.")
    raise UnauthorizedError("Usuario nao pode visualizar fotos desta solicitacao.")


def _validar_upload(arquivo: bytes, nome_original: str, mime_type: str, tipo_foto: str) -> None:
    if not arquivo:
        raise BadRequestError("Arquivo nao informado.")
    if len(arquivo) > settings.max_upload_bytes:
        raise BadRequestError("Arquivo excede o tamanho maximo permitido.")
    if mime_type not in ALLOWED_MIME_TYPES:
        raise BadRequestError("Formato de arquivo nao permitido. Use jpg, png ou webp.")
    if tipo_foto not in ALLOWED_PHOTO_TYPES:
        raise BadRequestError("Tipo de foto invalido.")
    if not nome_original.strip():
        raise BadRequestError("Nome original do arquivo e obrigatorio.")


def _parse_uuid(value: str, message: str) -> UUID:
    try:
        return UUID(value)
    except (TypeError, ValueError) as exc:
        raise BadRequestError(message) from exc
