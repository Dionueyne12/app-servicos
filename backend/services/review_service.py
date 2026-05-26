from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.pagination import PageParams
from app.schemas import AvaliacaoCreateRequest
from models import Avaliacao, Cliente, HistoricoEdicao, Prestador, SolicitacaoServico, Usuario
from utils.exceptions import BadRequestError, ConflictError, UnauthorizedError


TIPO_CLIENTE_AVALIA_PRESTADOR = "cliente_avalia_prestador"
TIPO_PRESTADOR_AVALIA_CLIENTE = "prestador_avalia_cliente"


def criar_avaliacao(
    db: Session,
    solicitacao_id: str,
    payload: AvaliacaoCreateRequest,
    usuario: Usuario,
) -> Avaliacao:
    solicitacao = _buscar_solicitacao(db, solicitacao_id)
    if solicitacao.status_codigo != "concluido":
        raise BadRequestError("Avaliacao so e permitida apos conclusao do servico.")
    if solicitacao.prestador is None:
        raise BadRequestError("Solicitacao nao possui prestador vinculado.")

    if usuario.tipo_usuario == "cliente":
        if usuario.cliente is None or usuario.cliente.id != solicitacao.cliente_id:
            raise UnauthorizedError("Cliente nao pode avaliar esta solicitacao.")
        tipo_avaliacao = TIPO_CLIENTE_AVALIA_PRESTADOR
        avaliado_usuario_id = solicitacao.prestador.usuario_id
    elif usuario.tipo_usuario == "prestador":
        if usuario.prestador is None or usuario.prestador.id != solicitacao.prestador_id:
            raise UnauthorizedError("Prestador nao pode avaliar esta solicitacao.")
        tipo_avaliacao = TIPO_PRESTADOR_AVALIA_CLIENTE
        avaliado_usuario_id = solicitacao.cliente.usuario_id
    else:
        raise UnauthorizedError("Apenas cliente ou prestador podem avaliar solicitacao.")

    existente = db.scalar(
        select(Avaliacao).where(
            Avaliacao.solicitacao_id == solicitacao.id,
            Avaliacao.tipo_avaliacao == tipo_avaliacao,
            Avaliacao.deleted_at.is_(None),
        )
    )
    if existente is not None:
        raise ConflictError("Avaliacao duplicada para esta solicitacao.")

    avaliacao = Avaliacao(
        solicitacao_id=solicitacao.id,
        avaliador_usuario_id=usuario.id,
        avaliado_usuario_id=avaliado_usuario_id,
        tipo_avaliacao=tipo_avaliacao,
        nota=payload.nota,
        comentario=payload.comentario.strip() if payload.comentario else None,
        created_by_usuario_id=usuario.id,
    )
    db.add(avaliacao)
    db.flush()

    _registrar_historico_criacao(db, avaliacao, usuario)
    _recalcular_reputacao_prestador(db, solicitacao.prestador)
    _recalcular_reputacao_cliente(db, solicitacao.cliente)
    from services.notification_service import criar_notificacao

    criar_notificacao(
        db,
        usuario_id=avaliado_usuario_id,
        solicitacao_id=solicitacao.id,
        tipo_notificacao="avaliacao_recebida",
        titulo="Avaliacao recebida",
        mensagem="Voce recebeu uma nova avaliacao.",
        created_by_usuario_id=usuario.id,
    )
    db.commit()
    return _buscar_avaliacao(db, avaliacao.id)


def listar_avaliacoes_prestador(
    db: Session,
    prestador_id: str,
    usuario: Usuario,
    pagination: PageParams,
) -> tuple[list[Avaliacao], int]:
    prestador = db.get(Prestador, _parse_uuid(prestador_id, "Prestador invalido."))
    if prestador is None or prestador.deleted_at is not None:
        raise BadRequestError("Prestador nao encontrado.")
    _garantir_visualizacao_prestador(prestador, usuario)
    return _listar_avaliacoes_por_avaliado(db, prestador.usuario_id, TIPO_CLIENTE_AVALIA_PRESTADOR, pagination)


def listar_avaliacoes_cliente(
    db: Session,
    cliente_id: str,
    usuario: Usuario,
    pagination: PageParams,
) -> tuple[list[Avaliacao], int]:
    cliente = db.get(Cliente, _parse_uuid(cliente_id, "Cliente invalido."))
    if cliente is None or cliente.deleted_at is not None:
        raise BadRequestError("Cliente nao encontrado.")
    _garantir_visualizacao_cliente(cliente, usuario)
    return _listar_avaliacoes_por_avaliado(db, cliente.usuario_id, TIPO_PRESTADOR_AVALIA_CLIENTE, pagination)


def _listar_avaliacoes_por_avaliado(
    db: Session,
    avaliado_usuario_id: UUID,
    tipo_avaliacao: str,
    pagination: PageParams,
) -> tuple[list[Avaliacao], int]:
    filters = [
        Avaliacao.avaliado_usuario_id == avaliado_usuario_id,
        Avaliacao.tipo_avaliacao == tipo_avaliacao,
        Avaliacao.deleted_at.is_(None),
    ]
    total = db.scalar(select(func.count()).select_from(Avaliacao).where(*filters)) or 0
    items = list(
        db.scalars(
            select(Avaliacao)
            .where(*filters)
            .order_by(Avaliacao.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return items, total


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


def _buscar_avaliacao(db: Session, avaliacao_id: UUID) -> Avaliacao:
    avaliacao = db.get(Avaliacao, avaliacao_id)
    if avaliacao is None:
        raise BadRequestError("Avaliacao nao encontrada.")
    return avaliacao


def _recalcular_reputacao_prestador(db: Session, prestador: Prestador) -> None:
    media, total = _metricas_avaliacoes(db, prestador.usuario_id, TIPO_CLIENTE_AVALIA_PRESTADOR)
    concluidos = _total_servicos(db, SolicitacaoServico.prestador_id == prestador.id, "concluido")
    total_servicos = db.scalar(
        select(func.count()).select_from(SolicitacaoServico).where(
            SolicitacaoServico.prestador_id == prestador.id,
            SolicitacaoServico.deleted_at.is_(None),
        )
    ) or 0
    cancelados = _total_servicos(db, SolicitacaoServico.prestador_id == prestador.id, "cancelado")
    problemas = _total_servicos(db, SolicitacaoServico.prestador_id == prestador.id, "em_analise")
    tempo_medio = _tempo_medio_conclusao(db, SolicitacaoServico.prestador_id == prestador.id)

    prestador.media_notas = media
    prestador.media_avaliacao = media
    prestador.total_avaliacoes = total
    prestador.total_servicos_concluidos = concluidos
    prestador.total_servicos = concluidos
    prestador.quantidade_problemas = problemas
    prestador.tempo_medio_conclusao_minutos = tempo_medio
    prestador.taxa_cancelamento = _percentual(cancelados, total_servicos)


def _recalcular_reputacao_cliente(db: Session, cliente: Cliente) -> None:
    media, total = _metricas_avaliacoes(db, cliente.usuario_id, TIPO_PRESTADOR_AVALIA_CLIENTE)
    total_solicitados = db.scalar(
        select(func.count()).select_from(SolicitacaoServico).where(
            SolicitacaoServico.cliente_id == cliente.id,
            SolicitacaoServico.deleted_at.is_(None),
        )
    ) or 0
    cancelados = _total_servicos(db, SolicitacaoServico.cliente_id == cliente.id, "cancelado")
    problemas = _total_servicos(db, SolicitacaoServico.cliente_id == cliente.id, "em_analise")
    tempo_medio = _tempo_medio_conclusao(db, SolicitacaoServico.cliente_id == cliente.id)

    cliente.media_notas = media
    cliente.total_avaliacoes = total
    cliente.total_servicos_solicitados = total_solicitados
    cliente.quantidade_problemas = problemas
    cliente.tempo_medio_conclusao_minutos = tempo_medio
    cliente.taxa_cancelamento = _percentual(cancelados, total_solicitados)


def _metricas_avaliacoes(db: Session, usuario_id: UUID, tipo_avaliacao: str) -> tuple[float, int]:
    row = db.execute(
        select(func.coalesce(func.avg(Avaliacao.nota), 0), func.count(Avaliacao.id)).where(
            Avaliacao.avaliado_usuario_id == usuario_id,
            Avaliacao.tipo_avaliacao == tipo_avaliacao,
            Avaliacao.deleted_at.is_(None),
        )
    ).one()
    return round(float(row[0]), 2), int(row[1])


def _total_servicos(db: Session, profile_filter, status: str) -> int:
    return db.scalar(
        select(func.count()).select_from(SolicitacaoServico).where(
            profile_filter,
            SolicitacaoServico.status_codigo == status,
            SolicitacaoServico.deleted_at.is_(None),
        )
    ) or 0


def _tempo_medio_conclusao(db: Session, profile_filter) -> float:
    solicitacoes = list(
        db.scalars(
            select(SolicitacaoServico).where(
                profile_filter,
                SolicitacaoServico.status_codigo == "concluido",
                SolicitacaoServico.data_inicio.is_not(None),
                SolicitacaoServico.data_confirmacao_cliente.is_not(None),
                SolicitacaoServico.deleted_at.is_(None),
            )
        )
    )
    if not solicitacoes:
        return 0
    minutos = []
    for solicitacao in solicitacoes:
        inicio = _sem_timezone(solicitacao.data_inicio)
        fim = _sem_timezone(solicitacao.data_confirmacao_cliente)
        minutos.append((fim - inicio).total_seconds() / 60)
    return round(sum(minutos) / len(minutos), 2)


def _sem_timezone(value: datetime) -> datetime:
    return value.replace(tzinfo=None) if value.tzinfo else value


def _percentual(parte: int, total: int) -> float:
    if total == 0:
        return 0
    return round((parte / total) * 100, 2)


def _registrar_historico_criacao(db: Session, avaliacao: Avaliacao, usuario: Usuario) -> None:
    for campo, valor in (
        ("tipo_avaliacao", avaliacao.tipo_avaliacao),
        ("nota", avaliacao.nota),
        ("comentario", avaliacao.comentario),
    ):
        db.add(
            HistoricoEdicao(
                entidade="avaliacoes",
                entidade_id=avaliacao.id,
                campo=campo,
                valor_anterior=None,
                valor_novo=str(valor) if valor is not None else None,
                alterado_por_usuario_id=usuario.id,
                origem="backend",
            )
        )


def _garantir_visualizacao_prestador(prestador: Prestador, usuario: Usuario) -> None:
    if usuario.tipo_usuario == "admin":
        return
    if usuario.tipo_usuario == "prestador" and usuario.prestador and usuario.prestador.id == prestador.id:
        return
    raise UnauthorizedError("Usuario nao pode visualizar avaliacoes deste prestador.")


def _garantir_visualizacao_cliente(cliente: Cliente, usuario: Usuario) -> None:
    if usuario.tipo_usuario == "admin":
        return
    if usuario.tipo_usuario == "cliente" and usuario.cliente and usuario.cliente.id == cliente.id:
        return
    raise UnauthorizedError("Usuario nao pode visualizar avaliacoes deste cliente.")


def _parse_uuid(value: str, message: str) -> UUID:
    try:
        return UUID(value)
    except (TypeError, ValueError) as exc:
        raise BadRequestError(message) from exc
