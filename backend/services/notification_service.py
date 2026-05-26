from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.pagination import PageParams
from models import Cliente, HistoricoEdicao, Notificacao, Prestador, SolicitacaoServico, Usuario
from utils.exceptions import BadRequestError, UnauthorizedError


TIPOS_NOTIFICACAO = {
    "servico_criado",
    "servico_aceito",
    "material_enviado",
    "material_aprovado",
    "material_recusado",
    "servico_iniciado",
    "servico_concluido",
    "problema_informado",
    "nova_mensagem",
    "avaliacao_recebida",
    "repasse_pendente",
    "alerta_admin",
}
PRIORIDADES = {"baixa", "normal", "alta", "critica"}
CANAIS = {"interna", "push_futura", "email_futuro", "whatsapp_futuro"}


def criar_notificacao(
    db: Session,
    usuario_id: UUID,
    tipo_notificacao: str,
    titulo: str,
    mensagem: str,
    solicitacao_id: UUID | None = None,
    prioridade: str = "normal",
    canal: str = "interna",
    created_by_usuario_id: UUID | None = None,
) -> Notificacao:
    if tipo_notificacao not in TIPOS_NOTIFICACAO:
        raise BadRequestError("Tipo de notificacao invalido.")
    if prioridade not in PRIORIDADES:
        raise BadRequestError("Prioridade invalida.")
    if canal not in CANAIS:
        raise BadRequestError("Canal invalido.")

    notificacao = Notificacao(
        usuario_id=usuario_id,
        solicitacao_id=solicitacao_id,
        tipo_notificacao=tipo_notificacao,
        titulo=titulo.strip(),
        mensagem=mensagem.strip(),
        prioridade=prioridade,
        canal=canal,
        created_by_usuario_id=created_by_usuario_id,
    )
    db.add(notificacao)
    db.flush()
    _registrar_historico(
        db,
        notificacao.id,
        created_by_usuario_id or usuario_id,
        [("tipo_notificacao", None, tipo_notificacao), ("titulo", None, titulo)],
    )
    return notificacao


def notificar_participante_solicitacao(
    db: Session,
    solicitacao_id: UUID,
    destinatario: str,
    tipo_notificacao: str,
    titulo: str,
    mensagem: str,
    prioridade: str = "normal",
    created_by_usuario_id: UUID | None = None,
) -> None:
    solicitacao = _buscar_solicitacao(db, solicitacao_id)
    if destinatario == "cliente":
        usuario_id = solicitacao.cliente.usuario_id
    elif destinatario == "prestador":
        if solicitacao.prestador is None:
            return
        usuario_id = solicitacao.prestador.usuario_id
    else:
        raise BadRequestError("Destinatario de notificacao invalido.")

    criar_notificacao(
        db,
        usuario_id=usuario_id,
        solicitacao_id=solicitacao.id,
        tipo_notificacao=tipo_notificacao,
        titulo=titulo,
        mensagem=mensagem,
        prioridade=prioridade,
        created_by_usuario_id=created_by_usuario_id,
    )


def listar_notificacoes(
    db: Session,
    usuario: Usuario,
    pagination: PageParams,
    apenas_nao_lidas: bool = False,
) -> tuple[list[Notificacao], int, int]:
    filters = [Notificacao.usuario_id == usuario.id, Notificacao.deleted_at.is_(None)]
    if apenas_nao_lidas:
        filters.append(Notificacao.lida.is_(False))
    total = db.scalar(select(func.count()).select_from(Notificacao).where(*filters)) or 0
    nao_lidas = contar_nao_lidas(db, usuario)
    items = list(
        db.scalars(
            select(Notificacao)
            .where(*filters)
            .order_by(Notificacao.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return items, total, nao_lidas


def contar_nao_lidas(db: Session, usuario: Usuario) -> int:
    return db.scalar(
        select(func.count()).select_from(Notificacao).where(
            Notificacao.usuario_id == usuario.id,
            Notificacao.lida.is_(False),
            Notificacao.deleted_at.is_(None),
        )
    ) or 0


def marcar_notificacao_lida(db: Session, notificacao_id: str, usuario: Usuario) -> Notificacao:
    notificacao = _buscar_notificacao(db, notificacao_id)
    _garantir_dono(notificacao, usuario)
    changes = []
    now = datetime.now(timezone.utc)
    _set_if_changed(notificacao, "lida", True, changes)
    _set_if_changed(notificacao, "data_leitura", now, changes)
    notificacao.updated_by_usuario_id = usuario.id
    _registrar_historico(db, notificacao.id, usuario.id, changes)
    db.commit()
    return _buscar_notificacao(db, str(notificacao.id))


def marcar_todas_lidas(db: Session, usuario: Usuario) -> int:
    notificacoes = list(
        db.scalars(
            select(Notificacao).where(
                Notificacao.usuario_id == usuario.id,
                Notificacao.lida.is_(False),
                Notificacao.deleted_at.is_(None),
            )
        )
    )
    now = datetime.now(timezone.utc)
    for notificacao in notificacoes:
        notificacao.lida = True
        notificacao.data_leitura = now
        notificacao.updated_by_usuario_id = usuario.id
        _registrar_historico(db, notificacao.id, usuario.id, [("lida", False, True)])
    db.commit()
    return len(notificacoes)


def excluir_notificacao(db: Session, notificacao_id: str, usuario: Usuario) -> Notificacao:
    notificacao = _buscar_notificacao(db, notificacao_id)
    _garantir_dono(notificacao, usuario)
    changes = []
    now = datetime.now(timezone.utc)
    _set_if_changed(notificacao, "deleted_at", now, changes)
    _set_if_changed(notificacao, "deleted_by_usuario_id", usuario.id, changes)
    notificacao.updated_by_usuario_id = usuario.id
    _registrar_historico(db, notificacao.id, usuario.id, changes)
    db.commit()
    return notificacao


def _buscar_solicitacao(db: Session, solicitacao_id: UUID) -> SolicitacaoServico:
    solicitacao = db.scalar(
        select(SolicitacaoServico)
        .where(SolicitacaoServico.id == solicitacao_id, SolicitacaoServico.deleted_at.is_(None))
        .options(
            selectinload(SolicitacaoServico.cliente).selectinload(Cliente.usuario),
            selectinload(SolicitacaoServico.prestador).selectinload(Prestador.usuario),
        )
    )
    if solicitacao is None:
        raise BadRequestError("Solicitacao nao encontrada para notificacao.")
    return solicitacao


def _buscar_notificacao(db: Session, notificacao_id: str) -> Notificacao:
    try:
        parsed_id = UUID(notificacao_id)
    except (TypeError, ValueError) as exc:
        raise BadRequestError("Notificacao invalida.") from exc
    notificacao = db.get(Notificacao, parsed_id)
    if notificacao is None or notificacao.deleted_at is not None:
        raise BadRequestError("Notificacao nao encontrada.")
    return notificacao


def _garantir_dono(notificacao: Notificacao, usuario: Usuario) -> None:
    if notificacao.usuario_id != usuario.id:
        raise UnauthorizedError("Usuario nao pode acessar esta notificacao.")


def _set_if_changed(target, field: str, new_value, changes: list[tuple[str, object, object]]) -> None:
    old_value = getattr(target, field)
    if old_value != new_value:
        setattr(target, field, new_value)
        changes.append((field, old_value, new_value))


def _registrar_historico(
    db: Session,
    notificacao_id: UUID,
    usuario_id: UUID,
    changes: list[tuple[str, object, object]],
) -> None:
    for field, old_value, new_value in changes:
        db.add(
            HistoricoEdicao(
                entidade="notificacoes",
                entidade_id=notificacao_id,
                campo=field,
                valor_anterior=str(old_value) if old_value is not None else None,
                valor_novo=str(new_value) if new_value is not None else None,
                alterado_por_usuario_id=usuario_id,
                origem="backend",
            )
        )
