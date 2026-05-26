from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.pagination import PageParams
from app.schemas import AvaliacaoCreateRequest, AvaliacaoPaginatedResponse, AvaliacaoResponse
from auth.dependencies import get_current_user
from controllers.review_controller import (
    criar_avaliacao_controller,
    listar_avaliacoes_cliente_controller,
    listar_avaliacoes_prestador_controller,
)
from database.session import get_db
from models import Usuario


router = APIRouter(tags=["avaliacoes"])


@router.post(
    "/solicitacoes/{solicitacao_id}/avaliar",
    response_model=AvaliacaoResponse,
    status_code=status.HTTP_201_CREATED,
)
def avaliar_solicitacao(
    solicitacao_id: str,
    payload: AvaliacaoCreateRequest,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AvaliacaoResponse:
    return criar_avaliacao_controller(solicitacao_id, payload, usuario, db)


@router.get("/prestadores/{prestador_id}/avaliacoes", response_model=AvaliacaoPaginatedResponse)
def listar_avaliacoes_prestador(
    prestador_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
) -> AvaliacaoPaginatedResponse:
    return listar_avaliacoes_prestador_controller(prestador_id, usuario, db, pagination)


@router.get("/clientes/{cliente_id}/avaliacoes", response_model=AvaliacaoPaginatedResponse)
def listar_avaliacoes_cliente(
    cliente_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
) -> AvaliacaoPaginatedResponse:
    return listar_avaliacoes_cliente_controller(cliente_id, usuario, db, pagination)
