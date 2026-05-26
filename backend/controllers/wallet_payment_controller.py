from app.pagination import PageParams, build_pagination_meta
from app.schemas import (
    CarteiraUsuarioResponse,
    MovimentacaoCarteiraPaginatedResponse,
    MovimentacaoCarteiraResponse,
    PagamentoCreateRequest,
    PagamentoPaginatedResponse,
    PagamentoResponse,
)
from models import CarteiraUsuario, MovimentacaoCarteira, Pagamento, Usuario
from services.wallet_payment_service import (
    aprovar_pagamento,
    buscar_pagamento,
    buscar_saldo_carteira,
    liberar_repasse,
    listar_movimentacoes_carteira,
    listar_pagamentos,
    recusar_pagamento,
    simular_pagamento,
)


def simular_pagamento_controller(payload: PagamentoCreateRequest, usuario: Usuario, db) -> PagamentoResponse:
    return _pagamento_response(simular_pagamento(db, payload, usuario))


def listar_pagamentos_controller(
    usuario: Usuario,
    db,
    pagination: PageParams,
    status_pagamento: str | None,
    metodo_pagamento: str | None,
) -> PagamentoPaginatedResponse:
    pagamentos, total = listar_pagamentos(db, usuario, pagination, status_pagamento, metodo_pagamento)
    return PagamentoPaginatedResponse(
        items=[_pagamento_response(pagamento) for pagamento in pagamentos],
        meta=build_pagination_meta(total, pagination),
    )


def buscar_pagamento_controller(pagamento_id: str, usuario: Usuario, db) -> PagamentoResponse:
    return _pagamento_response(buscar_pagamento(db, pagamento_id, usuario))


def aprovar_pagamento_controller(pagamento_id: str, usuario: Usuario, db) -> PagamentoResponse:
    return _pagamento_response(aprovar_pagamento(db, pagamento_id, usuario))


def recusar_pagamento_controller(pagamento_id: str, usuario: Usuario, db) -> PagamentoResponse:
    return _pagamento_response(recusar_pagamento(db, pagamento_id, usuario))


def liberar_repasse_controller(pagamento_id: str, usuario: Usuario, db) -> PagamentoResponse:
    return _pagamento_response(liberar_repasse(db, pagamento_id, usuario))


def buscar_saldo_carteira_controller(usuario: Usuario, db, usuario_id: str | None) -> CarteiraUsuarioResponse:
    return _carteira_response(buscar_saldo_carteira(db, usuario, usuario_id))


def listar_movimentacoes_carteira_controller(
    usuario: Usuario,
    db,
    pagination: PageParams,
    usuario_id: str | None,
) -> MovimentacaoCarteiraPaginatedResponse:
    movimentacoes, total = listar_movimentacoes_carteira(db, usuario, pagination, usuario_id)
    return MovimentacaoCarteiraPaginatedResponse(
        items=[_movimentacao_response(movimentacao) for movimentacao in movimentacoes],
        meta=build_pagination_meta(total, pagination),
    )


def _pagamento_response(pagamento: Pagamento) -> PagamentoResponse:
    return PagamentoResponse(
        id=str(pagamento.id),
        solicitacao_id=str(pagamento.solicitacao_id),
        cliente_id=str(pagamento.cliente_id),
        prestador_id=str(pagamento.prestador_id),
        valor_mao_obra=float(pagamento.valor_mao_obra),
        valor_material=float(pagamento.valor_material),
        valor_total=float(pagamento.valor_total),
        valor_comissao_plataforma=float(pagamento.valor_comissao_plataforma),
        valor_prestador=float(pagamento.valor_prestador),
        valor_fornecedor=float(pagamento.valor_fornecedor),
        status_pagamento=pagamento.status_pagamento,
        metodo_pagamento=pagamento.metodo_pagamento,
        data_pagamento=pagamento.data_pagamento.isoformat() if pagamento.data_pagamento else None,
        data_liberacao_repasse=(
            pagamento.data_liberacao_repasse.isoformat() if pagamento.data_liberacao_repasse else None
        ),
        comprovante_pagamento=pagamento.comprovante_pagamento,
        created_at=pagamento.created_at.isoformat(),
    )


def _carteira_response(carteira: CarteiraUsuario) -> CarteiraUsuarioResponse:
    return CarteiraUsuarioResponse(
        usuario_id=str(carteira.usuario_id),
        saldo_disponivel=float(carteira.saldo_disponivel),
        saldo_pendente=float(carteira.saldo_pendente),
        saldo_bloqueado=float(carteira.saldo_bloqueado),
        total_recebido=float(carteira.total_recebido),
        total_movimentado=float(carteira.total_movimentado),
    )


def _movimentacao_response(movimentacao: MovimentacaoCarteira) -> MovimentacaoCarteiraResponse:
    return MovimentacaoCarteiraResponse(
        id=str(movimentacao.id),
        usuario_id=str(movimentacao.usuario_id),
        pagamento_id=str(movimentacao.pagamento_id) if movimentacao.pagamento_id else None,
        tipo_movimentacao=movimentacao.tipo_movimentacao,
        valor=float(movimentacao.valor),
        descricao=movimentacao.descricao,
        saldo_disponivel_apos=float(movimentacao.saldo_disponivel_apos),
        saldo_pendente_apos=float(movimentacao.saldo_pendente_apos),
        saldo_bloqueado_apos=float(movimentacao.saldo_bloqueado_apos),
        created_at=movimentacao.created_at.isoformat(),
    )
