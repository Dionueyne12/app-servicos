from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.pagination import PageParams
from app.schemas import (
    CarteiraUsuarioResponse,
    MovimentacaoCarteiraPaginatedResponse,
    PagamentoCreateRequest,
    PagamentoPaginatedResponse,
    PagamentoResponse,
)
from auth.dependencies import get_current_user
from controllers.wallet_payment_controller import (
    aprovar_pagamento_controller,
    buscar_pagamento_controller,
    buscar_saldo_carteira_controller,
    liberar_repasse_controller,
    listar_movimentacoes_carteira_controller,
    listar_pagamentos_controller,
    recusar_pagamento_controller,
    simular_pagamento_controller,
)
from database.session import get_db
from models import Usuario


router = APIRouter(tags=["pagamentos-carteira"])


@router.post("/pagamentos/simular", response_model=PagamentoResponse, status_code=201)
def simular_pagamento(
    payload: PagamentoCreateRequest,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PagamentoResponse:
    return simular_pagamento_controller(payload, usuario, db)


@router.get("/pagamentos", response_model=PagamentoPaginatedResponse)
def listar_pagamentos(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
    status_pagamento: str | None = Query(default=None, max_length=40),
    metodo_pagamento: str | None = Query(default=None, max_length=40),
) -> PagamentoPaginatedResponse:
    return listar_pagamentos_controller(usuario, db, pagination, status_pagamento, metodo_pagamento)


@router.get("/pagamentos/{pagamento_id}", response_model=PagamentoResponse)
def buscar_pagamento(
    pagamento_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PagamentoResponse:
    return buscar_pagamento_controller(pagamento_id, usuario, db)


@router.patch("/pagamentos/{pagamento_id}/aprovar", response_model=PagamentoResponse)
def aprovar_pagamento(
    pagamento_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PagamentoResponse:
    return aprovar_pagamento_controller(pagamento_id, usuario, db)


@router.patch("/pagamentos/{pagamento_id}/recusar", response_model=PagamentoResponse)
def recusar_pagamento(
    pagamento_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PagamentoResponse:
    return recusar_pagamento_controller(pagamento_id, usuario, db)


@router.patch("/pagamentos/{pagamento_id}/liberar-repasse", response_model=PagamentoResponse)
def liberar_repasse(
    pagamento_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PagamentoResponse:
    return liberar_repasse_controller(pagamento_id, usuario, db)


@router.get("/carteira/meu-saldo", response_model=CarteiraUsuarioResponse)
def buscar_meu_saldo(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
    usuario_id: str | None = Query(default=None),
) -> CarteiraUsuarioResponse:
    return buscar_saldo_carteira_controller(usuario, db, usuario_id)


@router.get("/carteira/movimentacoes", response_model=MovimentacaoCarteiraPaginatedResponse)
def listar_minhas_movimentacoes(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
    usuario_id: str | None = Query(default=None),
) -> MovimentacaoCarteiraPaginatedResponse:
    return listar_movimentacoes_carteira_controller(usuario, db, pagination, usuario_id)
