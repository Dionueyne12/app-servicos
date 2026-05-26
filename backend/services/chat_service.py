from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.pagination import PageParams
from app.schemas import MensagemSolicitacaoCreateRequest
from models import Cliente, HistoricoEdicao, MensagemSolicitacao, Prestador, SolicitacaoServico, Usuario
from utils.exceptions import BadRequestError, UnauthorizedError


TIPOS_MENSAGEM = {"texto", "imagem", "sistema", "alerta", "comprovante"}
STATUS_BLOQUEIA_MENSAGEM = {"cancelado"}


def criar_mensagem(
    db: Session,
    solicitacao_id: str,
    payload: MensagemSolicitacaoCreateRequest,
    usuario: Usuario,
) -> MensagemSolicitacao:
    solicitacao = _buscar_solicitacao(db, solicitacao_id)
    if solicitacao.status_codigo in STATUS_BLOQUEIA_MENSAGEM:
        raise BadRequestError("Nao e permitido enviar mensagem em solicitacao cancelada.")
    if payload.tipo_mensagem == "sistema":
        raise UnauthorizedError("Mensagem de sistema e gerada automaticamente pelo backend.")
    remetente_id, destinatario_id = _resolver_participantes_chat(solicitacao, usuario)

    mensagem = MensagemSolicitacao(
        solicitacao_id=solicitacao.id,
        remetente_usuario_id=remetente_id,
        destinatario_usuario_id=destinatario_id,
        tipo_mensagem=payload.tipo_mensagem,
        mensagem=payload.mensagem.strip(),
        arquivo_url=payload.arquivo_url,
        created_by_usuario_id=usuario.id,
    )
    db.add(mensagem)
    db.flush()
    _registrar_historico(db, mensagem.id, usuario.id, [("mensagem", None, mensagem.mensagem)])
    from services.notification_service import criar_notificacao

    criar_notificacao(
        db,
        usuario_id=destinatario_id,
        solicitacao_id=solicitacao.id,
        tipo_notificacao="nova_mensagem",
        titulo="Nova mensagem",
        mensagem="Voce recebeu uma nova mensagem na solicitacao.",
        created_by_usuario_id=usuario.id,
    )
    db.commit()
    return _buscar_mensagem(db, mensagem.id)


def listar_mensagens(
    db: Session,
    solicitacao_id: str,
    usuario: Usuario,
    pagination: PageParams,
) -> tuple[list[MensagemSolicitacao], int, int]:
    solicitacao = _buscar_solicitacao(db, solicitacao_id)
    _garantir_acesso_chat(solicitacao, usuario)
    filters = [
        MensagemSolicitacao.solicitacao_id == solicitacao.id,
        MensagemSolicitacao.deleted_at.is_(None),
    ]
    total = db.scalar(select(func.count()).select_from(MensagemSolicitacao).where(*filters)) or 0
    nao_lidas = _contar_nao_lidas(db, solicitacao.id, usuario)
    items = list(
        db.scalars(
            select(MensagemSolicitacao)
            .where(*filters)
            .order_by(MensagemSolicitacao.created_at.asc())
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return items, total, nao_lidas


def visualizar_mensagem(db: Session, mensagem_id: str, usuario: Usuario) -> MensagemSolicitacao:
    mensagem = _buscar_mensagem(db, _parse_uuid(mensagem_id, "Mensagem invalida."))
    _garantir_visualizacao_mensagem(mensagem, usuario)

    changes = []
    now = datetime.now(timezone.utc)
    _set_if_changed(mensagem, "visualizada", True, changes)
    _set_if_changed(mensagem, "data_visualizacao", now, changes)
    mensagem.updated_by_usuario_id = usuario.id
    _registrar_historico(db, mensagem.id, usuario.id, changes)
    db.commit()
    return _buscar_mensagem(db, mensagem.id)


def excluir_mensagem(db: Session, mensagem_id: str, usuario: Usuario) -> MensagemSolicitacao:
    mensagem = _buscar_mensagem(db, _parse_uuid(mensagem_id, "Mensagem invalida."))
    if usuario.tipo_usuario != "admin" and mensagem.remetente_usuario_id != usuario.id:
        raise UnauthorizedError("Usuario nao pode excluir esta mensagem.")
    if mensagem.deleted_at is not None:
        return mensagem

    changes = []
    now = datetime.now(timezone.utc)
    _set_if_changed(mensagem, "deleted_at", now, changes)
    _set_if_changed(mensagem, "deleted_by_usuario_id", usuario.id, changes)
    mensagem.updated_by_usuario_id = usuario.id
    _registrar_historico(db, mensagem.id, usuario.id, changes)
    db.commit()
    return mensagem


def registrar_mensagem_sistema(
    db: Session,
    solicitacao: SolicitacaoServico,
    mensagem: str,
    remetente_usuario_id: UUID,
) -> None:
    if solicitacao.cliente is None:
        solicitacao = _buscar_solicitacao(db, str(solicitacao.id))
    if solicitacao.prestador is None:
        return
    cliente_usuario_id = solicitacao.cliente.usuario_id
    prestador_usuario_id = solicitacao.prestador.usuario_id
    destinatario_id = (
        prestador_usuario_id if remetente_usuario_id == cliente_usuario_id else cliente_usuario_id
    )
    item = MensagemSolicitacao(
        solicitacao_id=solicitacao.id,
        remetente_usuario_id=remetente_usuario_id,
        destinatario_usuario_id=destinatario_id,
        tipo_mensagem="sistema",
        mensagem=mensagem,
        visualizada=False,
        created_by_usuario_id=remetente_usuario_id,
    )
    db.add(item)
    db.flush()
    _registrar_historico(db, item.id, remetente_usuario_id, [("mensagem_sistema", None, mensagem)])


def _buscar_solicitacao(db: Session, solicitacao_id: str) -> SolicitacaoServico:
    solicitacao = db.scalar(
        select(SolicitacaoServico)
        .where(
            SolicitacaoServico.id == _parse_uuid(solicitacao_id, "Solicitacao invalida."),
            SolicitacaoServico.deleted_at.is_(None),
        )
        .options(
            selectinload(SolicitacaoServico.cliente).selectinload(Cliente.usuario),
            selectinload(SolicitacaoServico.prestador).selectinload(Prestador.usuario),
        )
    )
    if solicitacao is None:
        raise BadRequestError("Solicitacao nao encontrada.")
    return solicitacao


def _buscar_mensagem(db: Session, mensagem_id: UUID) -> MensagemSolicitacao:
    mensagem = db.scalar(
        select(MensagemSolicitacao)
        .where(MensagemSolicitacao.id == mensagem_id)
        .options(selectinload(MensagemSolicitacao.solicitacao))
    )
    if mensagem is None or mensagem.deleted_at is not None:
        raise BadRequestError("Mensagem nao encontrada.")
    return mensagem


def _resolver_participantes_chat(solicitacao: SolicitacaoServico, usuario: Usuario) -> tuple[UUID, UUID]:
    if solicitacao.prestador is None:
        raise BadRequestError("Chat fica disponivel apos aceite do prestador.")
    if usuario.tipo_usuario == "cliente" and usuario.cliente and usuario.cliente.id == solicitacao.cliente_id:
        return usuario.id, solicitacao.prestador.usuario_id
    if usuario.tipo_usuario == "prestador" and usuario.prestador and usuario.prestador.id == solicitacao.prestador_id:
        return usuario.id, solicitacao.cliente.usuario_id
    raise UnauthorizedError("Usuario nao participa do chat desta solicitacao.")


def _garantir_acesso_chat(solicitacao: SolicitacaoServico, usuario: Usuario) -> None:
    if usuario.tipo_usuario == "admin":
        return
    if usuario.tipo_usuario == "cliente" and usuario.cliente and usuario.cliente.id == solicitacao.cliente_id:
        return
    if usuario.tipo_usuario == "prestador" and usuario.prestador and usuario.prestador.id == solicitacao.prestador_id:
        return
    raise UnauthorizedError("Usuario nao pode visualizar este chat.")


def _garantir_visualizacao_mensagem(mensagem: MensagemSolicitacao, usuario: Usuario) -> None:
    if usuario.tipo_usuario == "admin":
        return
    if mensagem.destinatario_usuario_id == usuario.id:
        return
    raise UnauthorizedError("Somente o destinatario pode marcar mensagem como visualizada.")


def _contar_nao_lidas(db: Session, solicitacao_id: UUID, usuario: Usuario) -> int:
    if usuario.tipo_usuario == "admin":
        return 0
    return db.scalar(
        select(func.count()).select_from(MensagemSolicitacao).where(
            MensagemSolicitacao.solicitacao_id == solicitacao_id,
            MensagemSolicitacao.destinatario_usuario_id == usuario.id,
            MensagemSolicitacao.visualizada.is_(False),
            MensagemSolicitacao.deleted_at.is_(None),
        )
    ) or 0


def _set_if_changed(target, field: str, new_value, changes: list[tuple[str, object, object]]) -> None:
    old_value = getattr(target, field)
    if old_value != new_value:
        setattr(target, field, new_value)
        changes.append((field, old_value, new_value))


def _registrar_historico(
    db: Session,
    mensagem_id: UUID,
    usuario_id: UUID,
    changes: list[tuple[str, object, object]],
) -> None:
    for field, old_value, new_value in changes:
        db.add(
            HistoricoEdicao(
                entidade="mensagens_solicitacao",
                entidade_id=mensagem_id,
                campo=field,
                valor_anterior=str(old_value) if old_value is not None else None,
                valor_novo=str(new_value) if new_value is not None else None,
                alterado_por_usuario_id=usuario_id,
                origem="backend",
            )
        )


def _parse_uuid(value: str, message: str) -> UUID:
    try:
        return UUID(value)
    except (TypeError, ValueError) as exc:
        raise BadRequestError(message) from exc
