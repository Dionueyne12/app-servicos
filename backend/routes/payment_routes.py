from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.pagination import PageParams
from app.schemas import (
    PagamentoSimuladoPaginatedResponse,
    PagamentoSimuladoResponse,
    RepassePaginatedResponse,
)
from auth.dependencies import get_current_user
from controllers.payment_controller import (
    buscar_pagamento_controller,
    gerar_pagamento_controller,
    listar_pagamentos_controller,
    listar_repasses_controller,
)
from database.session import get_db
from models import Usuario


router = APIRouter(tags=["pagamentos"])


@router.post("/solicitacoes/{solicitacao_id}/pagamento-simulado", response_model=PagamentoSimuladoResponse)
def gerar_pagamento_simulado(
    solicitacao_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PagamentoSimuladoResponse:
    return gerar_pagamento_controller(solicitacao_id, usuario, db)


@router.get("/solicitacoes/{solicitacao_id}/pagamento-simulado", response_model=PagamentoSimuladoResponse)
def buscar_pagamento_simulado(
    solicitacao_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PagamentoSimuladoResponse:
    return buscar_pagamento_controller(solicitacao_id, usuario, db)


@router.get("/pagamentos-simulados", response_model=PagamentoSimuladoPaginatedResponse)
def listar_pagamentos_simulados(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
    status_pagamento: str | None = Query(default=None, max_length=40),
) -> PagamentoSimuladoPaginatedResponse:
    return listar_pagamentos_controller(usuario, db, pagination, status_pagamento)


@router.get("/repasses", response_model=RepassePaginatedResponse)
def listar_repasses_pagamento(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
    status_repasse: str | None = Query(default=None, max_length=40),
) -> RepassePaginatedResponse:
    return listar_repasses_controller(usuario, db, pagination, status_repasse)
