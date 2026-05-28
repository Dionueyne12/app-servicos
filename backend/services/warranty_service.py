from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.pagination import PageParams
from models import (
    GarantiaServico,
    HistoricoEdicao,
    Notificacao,
    PagamentoSimulado,
    Prestador,
    Repasse,
    SolicitacaoServico,
    Usuario,
)
from utils.exceptions import BadRequestError, ForbiddenError, UnauthorizedError


STATUS_GARANTIA = {"ativa", "expirada", "acionada", "em_analise", "resolvida", "negada"}
STATUS_BLOQUEIAM_REPASSE = {"acionada", "em_analise"}


def calcular_retencao_garantia(solicitacao: SolicitacaoServico, valor_prestador) -> tuple[Decimal, Decimal]:
    servico = solicitacao.servico_tabelado
    valor = _money(valor_prestador)
    if (
        servico is None
        or not servico.possui_garantia
        or servico.dias_garantia <= 0
        or _money(servico.percentual_retencao_garantia) <= 0
    ):
        return Decimal("0.00"), valor

    percentual = _money(servico.percentual_retencao_garantia)
    valor_retido = _money(valor * percentual / Decimal("100"))
    valor_liberado = _money(max(valor - valor_retido, Decimal("0.00")))
    return valor_retido, valor_liberado


def criar_garantia_apos_conclusao(
    db: Session,
    solicitacao: SolicitacaoServico,
    usuario: Usuario,
    pagamento: PagamentoSimulado | None = None,
) -> GarantiaServico | None:
    servico = solicitacao.servico_tabelado
    if (
        servico is None
        or solicitacao.prestador_id is None
        or not servico.possui_garantia
        or servico.dias_garantia <= 0
    ):
        return None

    garantia = db.scalar(
        select(GarantiaServico).where(
            GarantiaServico.solicitacao_id == solicitacao.id,
            GarantiaServico.deleted_at.is_(None),
        )
    )
    if garantia is not None:
        return garantia

    valor_base = pagamento.valor_prestador if pagamento is not None else solicitacao.preco_mao_obra_snapshot
    valor_retido, valor_liberado = calcular_retencao_garantia(solicitacao, valor_base)
    now = datetime.now(timezone.utc)
    garantia = GarantiaServico(
        solicitacao_id=solicitacao.id,
        prestador_id=solicitacao.prestador_id,
        cliente_id=solicitacao.cliente_id,
        servico_tabelado_id=solicitacao.servico_tabelado_id,
        pagamento_simulado_id=pagamento.id if pagamento is not None else None,
        data_inicio_garantia=now,
        data_fim_garantia=now + timedelta(days=servico.dias_garantia),
        status_garantia="ativa",
        valor_retido=valor_retido,
        valor_liberado_inicial=valor_liberado,
        percentual_retencao=servico.percentual_retencao_garantia,
        dias_garantia=servico.dias_garantia,
        dias_liberacao_primeiro_repasse=servico.dias_liberacao_primeiro_repasse,
        bloqueio_repasse=valor_retido > 0,
        created_by_usuario_id=usuario.id,
    )
    db.add(garantia)
    db.flush()
    _registrar_historico(
        db,
        garantia.id,
        usuario.id,
        [("status_garantia", None, "ativa"), ("valor_retido", None, valor_retido)],
    )
    return garantia


def acionar_garantia(
    db: Session,
    solicitacao_id: str,
    descricao_problema: str,
    observacao_cliente: str | None,
    fotos: list[str] | None,
    usuario: Usuario,
) -> GarantiaServico:
    garantia = _buscar_garantia_por_solicitacao(db, solicitacao_id)
    _garantir_cliente_dono(garantia, usuario)
    if garantia.status_garantia not in {"ativa", "expirada"}:
        raise BadRequestError("Garantia ja esta em atendimento ou finalizada.")

    changes = [
        ("status_garantia", garantia.status_garantia, "acionada"),
        ("descricao_problema", garantia.descricao_problema, descricao_problema.strip()),
        ("observacao_cliente", garantia.observacao_cliente, observacao_cliente),
        ("bloqueio_repasse", garantia.bloqueio_repasse, True),
    ]
    garantia.status_garantia = "acionada"
    garantia.descricao_problema = descricao_problema.strip()
    garantia.observacao_cliente = observacao_cliente.strip() if observacao_cliente else None
    garantia.fotos = "\n".join(fotos or []) if fotos else None
    garantia.data_acionamento = datetime.now(timezone.utc)
    garantia.bloqueio_repasse = True
    garantia.updated_by_usuario_id = usuario.id
    if garantia.prestador:
        garantia.prestador.garantias_acionadas += 1
        garantia.prestador.reincidencia_garantia += 1

    _registrar_historico(db, garantia.id, usuario.id, changes)
    _notificar_garantia_acionada(db, garantia, usuario.id)
    db.commit()
    return buscar_garantia(db, str(garantia.id), usuario)


def listar_garantias(
    db: Session,
    usuario: Usuario,
    pagination: PageParams,
    status_garantia: str | None = None,
) -> tuple[list[GarantiaServico], int]:
    _garantir_admin(usuario)
    filters = [GarantiaServico.deleted_at.is_(None)]
    if status_garantia:
        if status_garantia not in STATUS_GARANTIA:
            raise BadRequestError("Status de garantia invalido.")
        filters.append(GarantiaServico.status_garantia == status_garantia)

    total = db.scalar(select(func.count()).select_from(GarantiaServico).where(*filters)) or 0
    items = list(
        db.scalars(
            select(GarantiaServico)
            .where(*filters)
            .options(selectinload(GarantiaServico.prestador), selectinload(GarantiaServico.cliente))
            .order_by(GarantiaServico.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return items, total


def buscar_garantia(db: Session, garantia_id: str, usuario: Usuario) -> GarantiaServico:
    garantia = db.scalar(
        select(GarantiaServico)
        .where(GarantiaServico.id == _parse_uuid(garantia_id, "Garantia invalida."), GarantiaServico.deleted_at.is_(None))
        .options(selectinload(GarantiaServico.prestador), selectinload(GarantiaServico.cliente))
    )
    if garantia is None:
        raise BadRequestError("Garantia nao encontrada.")
    _garantir_acesso_garantia(garantia, usuario)
    return garantia


def alterar_status_garantia_admin(
    db: Session,
    garantia_id: str,
    acao: str,
    observacao_admin: str | None,
    procedente: bool | None,
    admin: Usuario,
) -> GarantiaServico:
    _garantir_admin(admin)
    garantia = buscar_garantia(db, garantia_id, admin)
    status_anterior = garantia.status_garantia
    bloqueio_anterior = garantia.bloqueio_repasse
    procedente_anterior = garantia.procedente

    if acao == "bloquear":
        garantia.status_garantia = "em_analise"
        garantia.bloqueio_repasse = True
    elif acao == "liberar":
        garantia.status_garantia = "expirada"
        garantia.bloqueio_repasse = False
        _liberar_repasse_retido(db, garantia, admin)
    elif acao == "resolver":
        garantia.status_garantia = "resolvida"
        garantia.bloqueio_repasse = False
        garantia.procedente = True if procedente is None else procedente
        garantia.data_resolucao = datetime.now(timezone.utc)
        _atualizar_metricas_resolucao(garantia)
        _liberar_repasse_retido(db, garantia, admin)
    elif acao == "negar":
        garantia.status_garantia = "negada"
        garantia.bloqueio_repasse = False
        garantia.procedente = False
        garantia.data_resolucao = datetime.now(timezone.utc)
        _liberar_repasse_retido(db, garantia, admin)
    else:
        raise BadRequestError("Acao de garantia invalida.")

    garantia.observacao_admin = observacao_admin.strip() if observacao_admin else garantia.observacao_admin
    garantia.updated_by_usuario_id = admin.id
    _registrar_historico(
        db,
        garantia.id,
        admin.id,
        [
            ("status_garantia", status_anterior, garantia.status_garantia),
            ("bloqueio_repasse", bloqueio_anterior, garantia.bloqueio_repasse),
            ("procedente", procedente_anterior, garantia.procedente),
        ],
    )
    db.commit()
    return buscar_garantia(db, str(garantia.id), admin)


def existe_garantia_bloqueando_repasse(db: Session, solicitacao_id) -> bool:
    garantia = db.scalar(
        select(GarantiaServico).where(
            GarantiaServico.solicitacao_id == solicitacao_id,
            GarantiaServico.deleted_at.is_(None),
            GarantiaServico.bloqueio_repasse.is_(True),
            GarantiaServico.status_garantia.in_(STATUS_BLOQUEIAM_REPASSE),
        )
    )
    return garantia is not None


def _buscar_garantia_por_solicitacao(db: Session, solicitacao_id: str) -> GarantiaServico:
    garantia = db.scalar(
        select(GarantiaServico)
        .where(
            GarantiaServico.solicitacao_id == _parse_uuid(solicitacao_id, "Solicitacao invalida."),
            GarantiaServico.deleted_at.is_(None),
        )
        .options(selectinload(GarantiaServico.prestador), selectinload(GarantiaServico.cliente))
    )
    if garantia is None:
        raise BadRequestError("Esta solicitacao nao possui garantia ativa na plataforma.")
    return garantia


def _garantir_cliente_dono(garantia: GarantiaServico, usuario: Usuario) -> None:
    if usuario.tipo_usuario != "cliente" or usuario.cliente is None or garantia.cliente_id != usuario.cliente.id:
        raise UnauthorizedError("Apenas o cliente dono pode acionar esta garantia.")


def _garantir_acesso_garantia(garantia: GarantiaServico, usuario: Usuario) -> None:
    if usuario.tipo_usuario == "admin":
        return
    if usuario.tipo_usuario == "cliente" and usuario.cliente and garantia.cliente_id == usuario.cliente.id:
        return
    if usuario.tipo_usuario == "prestador" and usuario.prestador and garantia.prestador_id == usuario.prestador.id:
        return
    raise ForbiddenError("Usuario nao pode acessar esta garantia.")


def _garantir_admin(usuario: Usuario) -> None:
    if usuario.tipo_usuario != "admin":
        raise ForbiddenError("Acesso permitido apenas para administradores.")


def _liberar_repasse_retido(db: Session, garantia: GarantiaServico, admin: Usuario) -> None:
    if garantia.pagamento_simulado_id is None:
        return
    repasses = list(
        db.scalars(
            select(Repasse).where(
                Repasse.pagamento_id == garantia.pagamento_simulado_id,
                Repasse.tipo_repasse == "garantia",
                Repasse.status_repasse == "retido_garantia",
                Repasse.deleted_at.is_(None),
            )
        )
    )
    for repasse in repasses:
        status_anterior = repasse.status_repasse
        repasse.status_repasse = "pendente"
        repasse.updated_by_usuario_id = admin.id
        _registrar_historico(db, repasse.id, admin.id, [("status_repasse", status_anterior, "pendente")])


def _atualizar_metricas_resolucao(garantia: GarantiaServico) -> None:
    prestador = garantia.prestador
    if prestador is None:
        return
    prestador.garantias_resolvidas += 1
    if garantia.data_acionamento:
        horas = (datetime.now(timezone.utc) - garantia.data_acionamento).total_seconds() / 3600
        total = max(prestador.garantias_resolvidas, 1)
        media_atual = Decimal(str(prestador.tempo_medio_resolucao_garantia_horas or 0))
        prestador.tempo_medio_resolucao_garantia_horas = _money(
            ((media_atual * Decimal(total - 1)) + Decimal(str(horas))) / Decimal(total)
        )


def _notificar_garantia_acionada(db: Session, garantia: GarantiaServico, usuario_id: UUID) -> None:
    if garantia.prestador:
        db.add(
            Notificacao(
                usuario_id=garantia.prestador.usuario_id,
                solicitacao_id=garantia.solicitacao_id,
                tipo_notificacao="garantia_acionada",
                titulo="Garantia acionada",
                mensagem="O cliente acionou a garantia deste servico. Aguarde analise do admin.",
                prioridade="alta",
                created_by_usuario_id=usuario_id,
            )
        )
    admins = list(db.scalars(select(Usuario).where(Usuario.tipo_usuario == "admin", Usuario.deleted_at.is_(None))))
    for admin in admins:
        db.add(
            Notificacao(
                usuario_id=admin.id,
                solicitacao_id=garantia.solicitacao_id,
                tipo_notificacao="garantia_acionada",
                titulo="Garantia acionada",
                mensagem="Uma garantia foi acionada e precisa de analise administrativa.",
                prioridade="alta",
                created_by_usuario_id=usuario_id,
            )
        )


def _registrar_historico(
    db: Session,
    entidade_id: UUID,
    usuario_id: UUID,
    changes: list[tuple[str, object, object]],
) -> None:
    for field, old_value, new_value in changes:
        db.add(
            HistoricoEdicao(
                entidade="garantias_servico",
                entidade_id=entidade_id,
                campo=field,
                valor_anterior=str(old_value) if old_value is not None else None,
                valor_novo=str(new_value) if new_value is not None else None,
                alterado_por_usuario_id=usuario_id,
                origem="backend",
            )
        )


def _money(value) -> Decimal:
    if value is None:
        value = 0
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _parse_uuid(value: str, message: str) -> UUID:
    try:
        return UUID(str(value))
    except (TypeError, ValueError) as exc:
        raise BadRequestError(message) from exc
