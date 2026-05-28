from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from app.pagination import PageParams
from models import (
    HistoricoEdicao,
    PagamentoSimulado,
    Repasse,
    SolicitacaoServico,
    Usuario,
)
from utils.exceptions import BadRequestError, UnauthorizedError
from services.warranty_service import calcular_retencao_garantia


COMISSAO_PERCENTUAL = 0.15


def gerar_pagamento_simulado(
    db: Session,
    solicitacao: SolicitacaoServico,
    usuario: Usuario,
) -> PagamentoSimulado:
    if solicitacao.status_codigo != "concluido":
        raise BadRequestError("Pagamento simulado so pode ser gerado apos conclusao.")
    if solicitacao.prestador is None:
        raise BadRequestError("Solicitacao nao possui prestador para repasse.")

    pagamento = db.scalar(
        select(PagamentoSimulado).where(PagamentoSimulado.solicitacao_id == solicitacao.id)
    )
    pagamento_novo = pagamento is None
    if pagamento is None:
        pagamento = PagamentoSimulado(
            solicitacao_id=solicitacao.id,
            created_by_usuario_id=usuario.id,
        )
        db.add(pagamento)
        db.flush()

    valor_mao_obra = round(float(solicitacao.preco_mao_obra_snapshot or 0), 2)
    material = solicitacao.material
    valor_material = round(float(material.valor_estimado or 0), 2) if material else 0
    valor_comissao = round(valor_mao_obra * COMISSAO_PERCENTUAL, 2)
    valor_prestador = round(valor_mao_obra - valor_comissao, 2)
    valor_empresa = valor_material if material and material.empresa_fornecedora_id else 0

    changes = []
    _set_if_changed(pagamento, "valor_mao_obra", valor_mao_obra, changes)
    _set_if_changed(pagamento, "valor_material", valor_material, changes)
    _set_if_changed(pagamento, "valor_comissao", valor_comissao, changes)
    _set_if_changed(pagamento, "valor_prestador", valor_prestador, changes)
    _set_if_changed(pagamento, "valor_empresa", valor_empresa, changes)
    _set_if_changed(pagamento, "status_pagamento", "simulado", changes)
    pagamento.updated_by_usuario_id = usuario.id
    _registrar_historico(db, pagamento.id, usuario.id, changes)

    valor_retido_garantia, valor_liberado_prestador = calcular_retencao_garantia(solicitacao, valor_prestador)

    db.execute(delete(Repasse).where(Repasse.pagamento_id == pagamento.id))
    if float(valor_liberado_prestador) > 0:
        _criar_repasse(
            db,
            pagamento,
            solicitacao.prestador.usuario_id,
            None,
            "prestador",
            float(valor_liberado_prestador),
            usuario,
        )
    if float(valor_retido_garantia) > 0:
        _criar_repasse(
            db,
            pagamento,
            solicitacao.prestador.usuario_id,
            None,
            "garantia",
            float(valor_retido_garantia),
            usuario,
            status_repasse="retido_garantia",
        )
    if valor_empresa > 0:
        _criar_repasse(
            db,
            pagamento,
            None,
            material.empresa_fornecedora_id,
            "empresa",
            valor_empresa,
            usuario,
        )
    _criar_repasse(db, pagamento, None, None, "plataforma", valor_comissao, usuario)
    if pagamento_novo:
        from services.notification_service import criar_notificacao

        criar_notificacao(
            db,
            usuario_id=solicitacao.prestador.usuario_id,
            solicitacao_id=solicitacao.id,
            tipo_notificacao="repasse_pendente",
            titulo="Repasse pendente",
            mensagem="Um repasse simulado foi gerado para este servico.",
            created_by_usuario_id=usuario.id,
        )
    db.flush()
    return buscar_pagamento_por_id(db, pagamento.id)


def gerar_pagamento_por_solicitacao(
    db: Session,
    solicitacao_id: str,
    usuario: Usuario,
) -> PagamentoSimulado:
    solicitacao = _buscar_solicitacao(db, solicitacao_id)
    _garantir_acesso_pagamento(solicitacao, usuario, permitir_admin=True)
    pagamento = gerar_pagamento_simulado(db, solicitacao, usuario)
    db.commit()
    return buscar_pagamento_por_id(db, pagamento.id)


def buscar_pagamento_solicitacao(
    db: Session,
    solicitacao_id: str,
    usuario: Usuario,
) -> PagamentoSimulado:
    solicitacao = _buscar_solicitacao(db, solicitacao_id)
    _garantir_acesso_pagamento(solicitacao, usuario, permitir_admin=True)
    pagamento = db.scalar(
        select(PagamentoSimulado)
        .where(PagamentoSimulado.solicitacao_id == solicitacao.id, PagamentoSimulado.deleted_at.is_(None))
        .options(selectinload(PagamentoSimulado.repasses))
    )
    if pagamento is None:
        raise BadRequestError("Pagamento simulado ainda nao foi gerado.")
    return pagamento


def listar_pagamentos(
    db: Session,
    usuario: Usuario,
    pagination: PageParams,
    status_pagamento: str | None,
) -> tuple[list[PagamentoSimulado], int]:
    filters = [PagamentoSimulado.deleted_at.is_(None)]
    if usuario.tipo_usuario == "cliente":
        filters.append(PagamentoSimulado.solicitacao.has(SolicitacaoServico.cliente_id == usuario.cliente.id))
    elif usuario.tipo_usuario == "prestador":
        filters.append(PagamentoSimulado.solicitacao.has(SolicitacaoServico.prestador_id == usuario.prestador.id))
    elif usuario.tipo_usuario != "admin":
        raise UnauthorizedError("Usuario nao pode listar pagamentos.")
    if status_pagamento:
        filters.append(PagamentoSimulado.status_pagamento == status_pagamento)

    total = db.scalar(select(func.count()).select_from(PagamentoSimulado).where(*filters)) or 0
    items = list(
        db.scalars(
            select(PagamentoSimulado)
            .where(*filters)
            .options(selectinload(PagamentoSimulado.repasses))
            .order_by(PagamentoSimulado.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return items, total


def listar_repasses(
    db: Session,
    usuario: Usuario,
    pagination: PageParams,
    status_repasse: str | None,
) -> tuple[list[Repasse], int]:
    filters = [Repasse.deleted_at.is_(None)]
    if usuario.tipo_usuario == "prestador":
        filters.append(Repasse.destinatario_usuario_id == usuario.id)
    elif usuario.tipo_usuario != "admin":
        raise UnauthorizedError("Usuario nao pode listar repasses.")
    if status_repasse:
        filters.append(Repasse.status_repasse == status_repasse)

    total = db.scalar(select(func.count()).select_from(Repasse).where(*filters)) or 0
    items = list(
        db.scalars(
            select(Repasse)
            .where(*filters)
            .order_by(Repasse.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return items, total


def buscar_pagamento_por_id(db: Session, pagamento_id: UUID) -> PagamentoSimulado:
    pagamento = db.scalar(
        select(PagamentoSimulado)
        .where(PagamentoSimulado.id == pagamento_id, PagamentoSimulado.deleted_at.is_(None))
        .options(selectinload(PagamentoSimulado.repasses))
    )
    if pagamento is None:
        raise BadRequestError("Pagamento simulado nao encontrado.")
    return pagamento


def _buscar_solicitacao(db: Session, solicitacao_id: str) -> SolicitacaoServico:
    try:
        parsed_id = UUID(solicitacao_id)
    except (TypeError, ValueError) as exc:
        raise BadRequestError("Solicitacao invalida.") from exc
    solicitacao = db.scalar(
        select(SolicitacaoServico)
        .where(SolicitacaoServico.id == parsed_id, SolicitacaoServico.deleted_at.is_(None))
        .options(
            selectinload(SolicitacaoServico.material),
            selectinload(SolicitacaoServico.prestador),
            selectinload(SolicitacaoServico.servico_tabelado),
        )
    )
    if solicitacao is None:
        raise BadRequestError("Solicitacao nao encontrada.")
    return solicitacao


def _garantir_acesso_pagamento(
    solicitacao: SolicitacaoServico,
    usuario: Usuario,
    permitir_admin: bool,
) -> None:
    if permitir_admin and usuario.tipo_usuario == "admin":
        return
    if usuario.tipo_usuario == "cliente" and usuario.cliente and solicitacao.cliente_id == usuario.cliente.id:
        return
    if usuario.tipo_usuario == "prestador" and usuario.prestador and solicitacao.prestador_id == usuario.prestador.id:
        return
    raise UnauthorizedError("Usuario nao pode acessar este pagamento.")


def _criar_repasse(
    db: Session,
    pagamento: PagamentoSimulado,
    destinatario_usuario_id: UUID | None,
    empresa_fornecedora_id: UUID | None,
    tipo_repasse: str,
    valor: float,
    usuario: Usuario,
    status_repasse: str = "pendente",
) -> None:
    repasse = Repasse(
        pagamento_id=pagamento.id,
        destinatario_usuario_id=destinatario_usuario_id,
        empresa_fornecedora_id=empresa_fornecedora_id,
        tipo_repasse=tipo_repasse,
        valor=valor,
        status_repasse=status_repasse,
        created_by_usuario_id=usuario.id,
    )
    db.add(repasse)
    db.flush()
    _registrar_historico(db, repasse.id, usuario.id, [("valor", None, valor)])


def _set_if_changed(target, field: str, new_value, changes: list[tuple[str, object, object]]) -> None:
    old_value = getattr(target, field)
    comparable_old = float(old_value) if old_value is not None and isinstance(new_value, float) else old_value
    if comparable_old != new_value:
        setattr(target, field, new_value)
        changes.append((field, old_value, new_value))


def _registrar_historico(
    db: Session,
    entidade_id: UUID,
    usuario_id: UUID,
    changes: list[tuple[str, object, object]],
) -> None:
    for field, old_value, new_value in changes:
        db.add(
            HistoricoEdicao(
                entidade="pagamentos_repasses",
                entidade_id=entidade_id,
                campo=field,
                valor_anterior=str(old_value) if old_value is not None else None,
                valor_novo=str(new_value) if new_value is not None else None,
                alterado_por_usuario_id=usuario_id,
                origem="backend",
            )
        )
