from sqlalchemy.orm import Session

from app.pagination import PageParams, build_pagination_meta
from app.schemas import (
    PagamentoSimuladoPaginatedResponse,
    PagamentoSimuladoResponse,
    RepassePaginatedResponse,
    RepasseResponse,
)
from models import PagamentoSimulado, Repasse, Usuario
from services.payment_service import (
    buscar_pagamento_solicitacao,
    gerar_pagamento_por_solicitacao,
    listar_pagamentos,
    listar_repasses,
)


def gerar_pagamento_controller(
    solicitacao_id: str,
    usuario: Usuario,
    db: Session,
) -> PagamentoSimuladoResponse:
    return _pagamento_response(gerar_pagamento_por_solicitacao(db, solicitacao_id, usuario))


def buscar_pagamento_controller(
    solicitacao_id: str,
    usuario: Usuario,
    db: Session,
) -> PagamentoSimuladoResponse:
    return _pagamento_response(buscar_pagamento_solicitacao(db, solicitacao_id, usuario))


def listar_pagamentos_controller(
    usuario: Usuario,
    db: Session,
    pagination: PageParams,
    status_pagamento: str | None,
) -> PagamentoSimuladoPaginatedResponse:
    pagamentos, total = listar_pagamentos(db, usuario, pagination, status_pagamento)
    return PagamentoSimuladoPaginatedResponse(
        items=[_pagamento_response(pagamento) for pagamento in pagamentos],
        meta=build_pagination_meta(total, pagination),
    )


def listar_repasses_controller(
    usuario: Usuario,
    db: Session,
    pagination: PageParams,
    status_repasse: str | None,
) -> RepassePaginatedResponse:
    repasses, total = listar_repasses(db, usuario, pagination, status_repasse)
    return RepassePaginatedResponse(
        items=[_repasse_response(repasse) for repasse in repasses],
        meta=build_pagination_meta(total, pagination),
    )


def _pagamento_response(pagamento: PagamentoSimulado) -> PagamentoSimuladoResponse:
    valor_mao_obra = float(pagamento.valor_mao_obra)
    valor_material = float(pagamento.valor_material)
    return PagamentoSimuladoResponse(
        id=str(pagamento.id),
        solicitacao_id=str(pagamento.solicitacao_id),
        valor_mao_obra=valor_mao_obra,
        valor_material=valor_material,
        valor_comissao=float(pagamento.valor_comissao),
        valor_prestador=float(pagamento.valor_prestador),
        valor_empresa=float(pagamento.valor_empresa),
        valor_total=round(valor_mao_obra + valor_material, 2),
        status_pagamento=pagamento.status_pagamento,
        repasses=[_repasse_response(repasse) for repasse in pagamento.repasses if repasse.deleted_at is None],
        created_at=pagamento.created_at.isoformat(),
    )


def _repasse_response(repasse: Repasse) -> RepasseResponse:
    return RepasseResponse(
        id=str(repasse.id),
        pagamento_id=str(repasse.pagamento_id),
        destinatario_usuario_id=str(repasse.destinatario_usuario_id)
        if repasse.destinatario_usuario_id
        else None,
        empresa_fornecedora_id=str(repasse.empresa_fornecedora_id)
        if repasse.empresa_fornecedora_id
        else None,
        tipo_repasse=repasse.tipo_repasse,
        valor=float(repasse.valor),
        status_repasse=repasse.status_repasse,
        created_at=repasse.created_at.isoformat(),
    )
