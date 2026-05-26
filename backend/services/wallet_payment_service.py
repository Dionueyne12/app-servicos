from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.pagination import PageParams
from app.schemas import PagamentoCreateRequest
from models import (
    CarteiraUsuario,
    EmpresaFornecedora,
    HistoricoEdicao,
    MaterialServico,
    MovimentacaoCarteira,
    Pagamento,
    SolicitacaoServico,
    Usuario,
)
from utils.exceptions import BadRequestError, ForbiddenError, UnauthorizedError


COMISSAO_PLATAFORMA = Decimal("0.15")
STATUS_PAGAMENTO = {
    "aguardando_pagamento",
    "pagamento_aprovado",
    "pagamento_recusado",
    "aguardando_repasse",
    "repasse_liberado",
    "cancelado",
    "reembolso",
    "em_analise",
}
METODOS_PAGAMENTO = {"pix", "cartao", "boleto", "carteira_interna", "pagamento_futuro"}
TIPOS_MOVIMENTACAO = {"entrada", "saida", "bloqueio", "desbloqueio", "repasse", "estorno", "comissao"}


def simular_pagamento(db: Session, payload: PagamentoCreateRequest, usuario: Usuario) -> Pagamento:
    if payload.metodo_pagamento not in METODOS_PAGAMENTO:
        raise BadRequestError("Metodo de pagamento invalido.")

    solicitacao = _buscar_solicitacao(db, _parse_uuid(payload.solicitacao_id, "Solicitacao invalida."))
    _garantir_cliente_ou_admin(solicitacao, usuario)
    if solicitacao.prestador_id is None:
        raise BadRequestError("Solicitacao precisa estar aceita por um prestador para gerar pagamento.")
    if solicitacao.status_codigo in {"cancelado", "em_analise"}:
        raise BadRequestError("Nao e possivel gerar pagamento para solicitacao cancelada ou em analise.")

    pagamento = db.scalar(
        select(Pagamento)
        .where(Pagamento.solicitacao_id == solicitacao.id, Pagamento.deleted_at.is_(None))
        .options(selectinload(Pagamento.solicitacao))
    )
    valores = _calcular_valores(solicitacao)
    if pagamento is None:
        pagamento = Pagamento(
            solicitacao_id=solicitacao.id,
            cliente_id=solicitacao.cliente_id,
            prestador_id=solicitacao.prestador_id,
            status_pagamento="aguardando_pagamento",
            metodo_pagamento=payload.metodo_pagamento,
            comprovante_pagamento=payload.comprovante_pagamento,
            created_by_usuario_id=usuario.id,
        )
        db.add(pagamento)
        db.flush()

    changes = []
    for campo, valor in valores.items():
        _set_if_changed(pagamento, campo, valor, changes)
    _set_if_changed(pagamento, "metodo_pagamento", payload.metodo_pagamento, changes)
    if payload.comprovante_pagamento is not None:
        _set_if_changed(pagamento, "comprovante_pagamento", payload.comprovante_pagamento, changes)
    pagamento.updated_by_usuario_id = usuario.id
    _registrar_historico(db, pagamento.id, usuario.id, changes or [("status_pagamento", None, pagamento.status_pagamento)])
    db.commit()
    return buscar_pagamento(db, str(pagamento.id), usuario)


def listar_pagamentos(
    db: Session,
    usuario: Usuario,
    pagination: PageParams,
    status_pagamento: str | None = None,
    metodo_pagamento: str | None = None,
) -> tuple[list[Pagamento], int]:
    filters = [Pagamento.deleted_at.is_(None)]
    if usuario.tipo_usuario == "cliente":
        if usuario.cliente is None:
            raise UnauthorizedError("Usuario nao possui cadastro de cliente.")
        filters.append(Pagamento.cliente_id == usuario.cliente.id)
    elif usuario.tipo_usuario == "prestador":
        if usuario.prestador is None:
            raise UnauthorizedError("Usuario nao possui cadastro de prestador.")
        filters.append(Pagamento.prestador_id == usuario.prestador.id)
    elif usuario.tipo_usuario != "admin":
        raise ForbiddenError("Usuario nao pode listar pagamentos.")

    if status_pagamento:
        if status_pagamento not in STATUS_PAGAMENTO:
            raise BadRequestError("Status de pagamento invalido.")
        filters.append(Pagamento.status_pagamento == status_pagamento)
    if metodo_pagamento:
        if metodo_pagamento not in METODOS_PAGAMENTO:
            raise BadRequestError("Metodo de pagamento invalido.")
        filters.append(Pagamento.metodo_pagamento == metodo_pagamento)

    total = db.scalar(select(func.count()).select_from(Pagamento).where(*filters)) or 0
    pagamentos = list(
        db.scalars(
            select(Pagamento)
            .where(*filters)
            .order_by(Pagamento.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return pagamentos, total


def buscar_pagamento(db: Session, pagamento_id: str, usuario: Usuario) -> Pagamento:
    pagamento = db.scalar(
        select(Pagamento)
        .where(Pagamento.id == _parse_uuid(pagamento_id, "Pagamento invalido."), Pagamento.deleted_at.is_(None))
        .options(selectinload(Pagamento.solicitacao))
    )
    if pagamento is None:
        raise BadRequestError("Pagamento nao encontrado.")
    _garantir_acesso_pagamento(pagamento, usuario)
    return pagamento


def aprovar_pagamento(db: Session, pagamento_id: str, usuario: Usuario) -> Pagamento:
    _garantir_admin(usuario)
    pagamento = buscar_pagamento(db, pagamento_id, usuario)
    if pagamento.status_pagamento not in {"aguardando_pagamento", "pagamento_recusado"}:
        raise BadRequestError("Pagamento nao pode ser aprovado neste status.")

    now = datetime.now(timezone.utc)
    novo_status = "aguardando_repasse" if pagamento.solicitacao.status_codigo == "concluido" else "pagamento_aprovado"
    changes = [
        ("status_pagamento", pagamento.status_pagamento, novo_status),
        ("data_pagamento", pagamento.data_pagamento, now),
    ]
    pagamento.status_pagamento = novo_status
    pagamento.data_pagamento = now
    pagamento.updated_by_usuario_id = usuario.id

    cliente_usuario_id = pagamento.solicitacao.cliente.usuario_id
    _garantir_carteira(db, cliente_usuario_id, usuario.id)
    carteira_plataforma = _garantir_carteira(db, usuario.id, usuario.id)

    valor_total = _money(pagamento.valor_total)
    _movimentar_carteira(
        db,
        carteira_plataforma,
        "entrada",
        valor_total,
        "Pagamento recebido pela plataforma e aguardando repasse.",
        usuario.id,
        pagamento.id,
        pendente_delta=valor_total,
        total_recebido_delta=valor_total,
    )
    _movimentar_carteira(
        db,
        _garantir_carteira(db, cliente_usuario_id, usuario.id),
        "saida",
        valor_total,
        "Pagamento simulado do cliente para a plataforma.",
        usuario.id,
        pagamento.id,
        total_movimentado_delta=valor_total,
    )

    _registrar_historico(db, pagamento.id, usuario.id, changes)
    _notificar_repasse_pendente(db, pagamento, usuario.id)
    db.commit()
    return buscar_pagamento(db, str(pagamento.id), usuario)


def recusar_pagamento(db: Session, pagamento_id: str, usuario: Usuario) -> Pagamento:
    _garantir_admin(usuario)
    pagamento = buscar_pagamento(db, pagamento_id, usuario)
    if pagamento.status_pagamento in {"repasse_liberado", "cancelado", "reembolso"}:
        raise BadRequestError("Pagamento nao pode ser recusado neste status.")
    changes = [("status_pagamento", pagamento.status_pagamento, "pagamento_recusado")]
    pagamento.status_pagamento = "pagamento_recusado"
    pagamento.updated_by_usuario_id = usuario.id
    _registrar_historico(db, pagamento.id, usuario.id, changes)
    db.commit()
    return buscar_pagamento(db, str(pagamento.id), usuario)


def liberar_repasse(db: Session, pagamento_id: str, usuario: Usuario) -> Pagamento:
    _garantir_admin(usuario)
    pagamento = buscar_pagamento(db, pagamento_id, usuario)
    if pagamento.status_pagamento not in {"pagamento_aprovado", "aguardando_repasse"}:
        raise BadRequestError("Pagamento precisa estar aprovado para liberar repasse.")
    if pagamento.solicitacao.status_codigo != "concluido":
        raise BadRequestError("Repasse so pode ser liberado apos confirmacao de conclusao pelo cliente.")

    carteira_plataforma = _garantir_carteira(db, usuario.id, usuario.id)
    carteira_prestador = _garantir_carteira(db, pagamento.solicitacao.prestador.usuario_id, usuario.id)
    fornecedor_usuario_id = _buscar_usuario_fornecedor(db, pagamento.solicitacao)
    valor_total = _money(pagamento.valor_total)
    valor_prestador = _money(pagamento.valor_prestador)
    valor_fornecedor = _money(pagamento.valor_fornecedor)
    valor_comissao = _money(pagamento.valor_comissao_plataforma)
    valor_repassado = valor_prestador + valor_fornecedor

    _movimentar_carteira(
        db,
        carteira_plataforma,
        "saida",
        valor_repassado,
        "Saida de saldo da plataforma para repasses.",
        usuario.id,
        pagamento.id,
        pendente_delta=-valor_total,
        disponivel_delta=valor_comissao,
        total_movimentado_delta=valor_repassado,
    )
    _movimentar_carteira(
        db,
        carteira_plataforma,
        "comissao",
        valor_comissao,
        "Comissao da plataforma retida.",
        usuario.id,
        pagamento.id,
        total_movimentado_delta=valor_comissao,
    )
    _movimentar_carteira(
        db,
        carteira_prestador,
        "repasse",
        valor_prestador,
        "Repasse liberado ao prestador.",
        usuario.id,
        pagamento.id,
        disponivel_delta=valor_prestador,
        total_recebido_delta=valor_prestador,
        total_movimentado_delta=valor_prestador,
    )
    if fornecedor_usuario_id and valor_fornecedor > 0:
        _movimentar_carteira(
            db,
            _garantir_carteira(db, fornecedor_usuario_id, usuario.id),
            "repasse",
            valor_fornecedor,
            "Repasse liberado ao fornecedor.",
            usuario.id,
            pagamento.id,
            disponivel_delta=valor_fornecedor,
            total_recebido_delta=valor_fornecedor,
            total_movimentado_delta=valor_fornecedor,
        )

    now = datetime.now(timezone.utc)
    changes = [
        ("status_pagamento", pagamento.status_pagamento, "repasse_liberado"),
        ("data_liberacao_repasse", pagamento.data_liberacao_repasse, now),
    ]
    pagamento.status_pagamento = "repasse_liberado"
    pagamento.data_liberacao_repasse = now
    pagamento.updated_by_usuario_id = usuario.id
    _registrar_historico(db, pagamento.id, usuario.id, changes)
    _notificar_repasse_liberado(db, pagamento, usuario.id)
    db.commit()
    return buscar_pagamento(db, str(pagamento.id), usuario)


def buscar_saldo_carteira(db: Session, usuario: Usuario, usuario_id: str | None = None) -> CarteiraUsuario:
    dono_id = _resolver_usuario_carteira(usuario, usuario_id)
    carteira = _garantir_carteira(db, dono_id, usuario.id)
    db.commit()
    return carteira


def listar_movimentacoes_carteira(
    db: Session,
    usuario: Usuario,
    pagination: PageParams,
    usuario_id: str | None = None,
) -> tuple[list[MovimentacaoCarteira], int]:
    dono_id = _resolver_usuario_carteira(usuario, usuario_id)
    filters = [MovimentacaoCarteira.usuario_id == dono_id, MovimentacaoCarteira.deleted_at.is_(None)]
    total = db.scalar(select(func.count()).select_from(MovimentacaoCarteira).where(*filters)) or 0
    movimentacoes = list(
        db.scalars(
            select(MovimentacaoCarteira)
            .where(*filters)
            .order_by(MovimentacaoCarteira.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return movimentacoes, total


def _calcular_valores(solicitacao: SolicitacaoServico) -> dict[str, Decimal]:
    valor_mao_obra = _money(solicitacao.preco_mao_obra_snapshot)
    valor_material = Decimal("0.00")
    valor_fornecedor = Decimal("0.00")
    if solicitacao.material and solicitacao.material.deleted_at is None:
        valor_material = _money(solicitacao.material.valor_estimado)
        if solicitacao.material.empresa_fornecedora_id:
            valor_fornecedor = valor_material
    valor_comissao = _money(valor_mao_obra * COMISSAO_PLATAFORMA)
    valor_prestador = _money(max(valor_mao_obra - valor_comissao, Decimal("0.00")))
    valor_total = _money(valor_mao_obra + valor_material)
    return {
        "valor_mao_obra": valor_mao_obra,
        "valor_material": valor_material,
        "valor_total": valor_total,
        "valor_comissao_plataforma": valor_comissao,
        "valor_prestador": valor_prestador,
        "valor_fornecedor": valor_fornecedor,
    }


def _buscar_solicitacao(db: Session, solicitacao_id: UUID) -> SolicitacaoServico:
    solicitacao = db.scalar(
        select(SolicitacaoServico)
        .where(SolicitacaoServico.id == solicitacao_id, SolicitacaoServico.deleted_at.is_(None))
        .options(
            selectinload(SolicitacaoServico.cliente),
            selectinload(SolicitacaoServico.prestador),
            selectinload(SolicitacaoServico.material)
            .selectinload(MaterialServico.empresa_fornecedora)
            .selectinload(EmpresaFornecedora.usuario),
        )
    )
    if solicitacao is None:
        raise BadRequestError("Solicitacao nao encontrada.")
    return solicitacao


def _buscar_usuario_fornecedor(db: Session, solicitacao: SolicitacaoServico) -> UUID | None:
    if not solicitacao.material or not solicitacao.material.empresa_fornecedora_id:
        return None
    empresa = db.get(EmpresaFornecedora, solicitacao.material.empresa_fornecedora_id)
    if empresa is None or empresa.deleted_at is not None:
        return None
    return empresa.usuario_id


def _garantir_cliente_ou_admin(solicitacao: SolicitacaoServico, usuario: Usuario) -> None:
    if usuario.tipo_usuario == "admin":
        return
    if usuario.tipo_usuario == "cliente" and usuario.cliente and solicitacao.cliente_id == usuario.cliente.id:
        return
    raise UnauthorizedError("Apenas o cliente dono da solicitacao pode simular pagamento.")


def _garantir_acesso_pagamento(pagamento: Pagamento, usuario: Usuario) -> None:
    if usuario.tipo_usuario == "admin":
        return
    if usuario.tipo_usuario == "cliente" and usuario.cliente and pagamento.cliente_id == usuario.cliente.id:
        return
    if usuario.tipo_usuario == "prestador" and usuario.prestador and pagamento.prestador_id == usuario.prestador.id:
        return
    raise UnauthorizedError("Usuario nao pode acessar este pagamento.")


def _garantir_admin(usuario: Usuario) -> None:
    if usuario.tipo_usuario != "admin":
        raise ForbiddenError("Acesso permitido apenas para administradores.")


def _resolver_usuario_carteira(usuario: Usuario, usuario_id: str | None) -> UUID:
    if not usuario_id:
        return usuario.id
    parsed_id = _parse_uuid(usuario_id, "Usuario invalido.")
    if usuario.tipo_usuario != "admin" and parsed_id != usuario.id:
        raise ForbiddenError("Usuario nao pode acessar carteira de outro usuario.")
    return parsed_id


def _garantir_carteira(db: Session, usuario_id: UUID, operador_id: UUID) -> CarteiraUsuario:
    carteira = db.scalar(
        select(CarteiraUsuario).where(CarteiraUsuario.usuario_id == usuario_id, CarteiraUsuario.deleted_at.is_(None))
    )
    if carteira is None:
        carteira = CarteiraUsuario(usuario_id=usuario_id, created_by_usuario_id=operador_id)
        db.add(carteira)
        db.flush()
    return carteira


def _movimentar_carteira(
    db: Session,
    carteira: CarteiraUsuario,
    tipo_movimentacao: str,
    valor: Decimal,
    descricao: str,
    operador_id: UUID,
    pagamento_id: UUID | None = None,
    disponivel_delta: Decimal = Decimal("0.00"),
    pendente_delta: Decimal = Decimal("0.00"),
    bloqueado_delta: Decimal = Decimal("0.00"),
    total_recebido_delta: Decimal = Decimal("0.00"),
    total_movimentado_delta: Decimal | None = None,
) -> None:
    if tipo_movimentacao not in TIPOS_MOVIMENTACAO:
        raise BadRequestError("Tipo de movimentacao invalido.")
    valor = _money(valor)
    carteira.saldo_disponivel = _money(_money(carteira.saldo_disponivel) + disponivel_delta)
    carteira.saldo_pendente = _money(_money(carteira.saldo_pendente) + pendente_delta)
    carteira.saldo_bloqueado = _money(_money(carteira.saldo_bloqueado) + bloqueado_delta)
    carteira.total_recebido = _money(_money(carteira.total_recebido) + total_recebido_delta)
    movimentado = valor if total_movimentado_delta is None else total_movimentado_delta
    carteira.total_movimentado = _money(_money(carteira.total_movimentado) + movimentado)
    if min(carteira.saldo_disponivel, carteira.saldo_pendente, carteira.saldo_bloqueado) < 0:
        raise BadRequestError("Saldo da carteira ficaria negativo.")
    carteira.updated_by_usuario_id = operador_id
    db.add(
        MovimentacaoCarteira(
            carteira_id=carteira.id,
            usuario_id=carteira.usuario_id,
            pagamento_id=pagamento_id,
            tipo_movimentacao=tipo_movimentacao,
            valor=valor,
            descricao=descricao,
            saldo_disponivel_apos=carteira.saldo_disponivel,
            saldo_pendente_apos=carteira.saldo_pendente,
            saldo_bloqueado_apos=carteira.saldo_bloqueado,
            created_by_usuario_id=operador_id,
        )
    )


def _notificar_repasse_pendente(db: Session, pagamento: Pagamento, usuario_id: UUID) -> None:
    from services.notification_service import criar_notificacao

    criar_notificacao(
        db,
        usuario_id=pagamento.solicitacao.prestador.usuario_id,
        solicitacao_id=pagamento.solicitacao_id,
        tipo_notificacao="repasse_pendente",
        titulo="Pagamento aprovado",
        mensagem="O pagamento foi aprovado e o repasse ficara disponivel apos a conclusao confirmada.",
        created_by_usuario_id=usuario_id,
    )


def _notificar_repasse_liberado(db: Session, pagamento: Pagamento, usuario_id: UUID) -> None:
    from services.notification_service import criar_notificacao

    criar_notificacao(
        db,
        usuario_id=pagamento.solicitacao.prestador.usuario_id,
        solicitacao_id=pagamento.solicitacao_id,
        tipo_notificacao="repasse_pendente",
        titulo="Repasse liberado",
        mensagem="O repasse do servico foi liberado na carteira interna.",
        created_by_usuario_id=usuario_id,
    )


def _registrar_historico(
    db: Session,
    pagamento_id: UUID,
    usuario_id: UUID,
    changes: list[tuple[str, object, object]],
) -> None:
    for field, old_value, new_value in changes:
        db.add(
            HistoricoEdicao(
                entidade="pagamentos",
                entidade_id=pagamento_id,
                campo=field,
                valor_anterior=str(old_value) if old_value is not None else None,
                valor_novo=str(new_value) if new_value is not None else None,
                alterado_por_usuario_id=usuario_id,
                origem="backend",
            )
        )


def _set_if_changed(target, field: str, new_value, changes: list[tuple[str, object, object]]) -> None:
    old_value = getattr(target, field)
    changed = _money(old_value) != _money(new_value) if isinstance(new_value, Decimal) else old_value != new_value
    if changed:
        setattr(target, field, new_value)
        changes.append((field, old_value, new_value))


def _money(value) -> Decimal:
    if value is None:
        value = 0
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _parse_uuid(value: str, message: str) -> UUID:
    try:
        return UUID(str(value))
    except (TypeError, ValueError) as exc:
        raise BadRequestError(message) from exc
