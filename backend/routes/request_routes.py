from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.pagination import PageParams
from app.schemas import (
    SolicitacaoServicoCreateRequest,
    SolicitacaoServicoPaginatedResponse,
    SolicitacaoProblemaRequest,
    SolicitacaoServicoResponse,
    SolicitacaoStatusUpdateRequest,
    SolicitacaoServicoUpdateRequest,
)
from auth.dependencies import get_current_user, require_prestador
from controllers.request_controller import (
    buscar_solicitacao_controller,
    cancelar_solicitacao_controller,
    aceitar_solicitacao_controller,
    atualizar_status_solicitacao_controller,
    concluir_servico_controller,
    confirmar_conclusao_controller,
    criar_solicitacao_controller,
    editar_solicitacao_controller,
    informar_problema_controller,
    iniciar_servico_controller,
    listar_solicitacoes_disponiveis_controller,
    listar_solicitacoes_controller,
)
from database.session import get_db
from models import Usuario


router = APIRouter(prefix="/solicitacoes", tags=["solicitacoes"])


@router.post("", response_model=SolicitacaoServicoResponse, status_code=status.HTTP_201_CREATED)
def criar_solicitacao(
    payload: SolicitacaoServicoCreateRequest,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SolicitacaoServicoResponse:
    return criar_solicitacao_controller(payload, usuario, db)


@router.get("", response_model=SolicitacaoServicoPaginatedResponse)
def listar_solicitacoes(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
    status: str | None = Query(default=None, max_length=60),
    busca: str | None = Query(default=None, min_length=2, max_length=120),
) -> SolicitacaoServicoPaginatedResponse:
    return listar_solicitacoes_controller(usuario, db, pagination, status, busca)


@router.get("/disponiveis", response_model=SolicitacaoServicoPaginatedResponse)
def listar_solicitacoes_disponiveis(
    usuario: Usuario = Depends(require_prestador),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
) -> SolicitacaoServicoPaginatedResponse:
    return listar_solicitacoes_disponiveis_controller(usuario, db, pagination)


@router.get("/{solicitacao_id}", response_model=SolicitacaoServicoResponse)
def buscar_solicitacao(
    solicitacao_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SolicitacaoServicoResponse:
    return buscar_solicitacao_controller(solicitacao_id, usuario, db)


@router.post("/{solicitacao_id}/aceitar", response_model=SolicitacaoServicoResponse)
def aceitar_solicitacao(
    solicitacao_id: str,
    usuario: Usuario = Depends(require_prestador),
    db: Session = Depends(get_db),
) -> SolicitacaoServicoResponse:
    return aceitar_solicitacao_controller(solicitacao_id, usuario, db)


@router.put("/{solicitacao_id}", response_model=SolicitacaoServicoResponse)
def editar_solicitacao(
    solicitacao_id: str,
    payload: SolicitacaoServicoUpdateRequest,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SolicitacaoServicoResponse:
    return editar_solicitacao_controller(solicitacao_id, payload, usuario, db)


@router.patch("/{solicitacao_id}/status", response_model=SolicitacaoServicoResponse)
def atualizar_status_solicitacao(
    solicitacao_id: str,
    payload: SolicitacaoStatusUpdateRequest,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SolicitacaoServicoResponse:
    return atualizar_status_solicitacao_controller(solicitacao_id, payload, usuario, db)


@router.patch("/{solicitacao_id}/iniciar", response_model=SolicitacaoServicoResponse)
def iniciar_servico(
    solicitacao_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SolicitacaoServicoResponse:
    return iniciar_servico_controller(solicitacao_id, usuario, db)


@router.patch("/{solicitacao_id}/concluir", response_model=SolicitacaoServicoResponse)
def concluir_servico(
    solicitacao_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SolicitacaoServicoResponse:
    return concluir_servico_controller(solicitacao_id, usuario, db)


@router.patch("/{solicitacao_id}/confirmar-conclusao", response_model=SolicitacaoServicoResponse)
def confirmar_conclusao(
    solicitacao_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SolicitacaoServicoResponse:
    return confirmar_conclusao_controller(solicitacao_id, usuario, db)


@router.patch("/{solicitacao_id}/informar-problema", response_model=SolicitacaoServicoResponse)
def informar_problema(
    solicitacao_id: str,
    payload: SolicitacaoProblemaRequest,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SolicitacaoServicoResponse:
    return informar_problema_controller(solicitacao_id, payload, usuario, db)


@router.patch("/{solicitacao_id}/cancelar", response_model=SolicitacaoServicoResponse)
def cancelar_solicitacao(
    solicitacao_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SolicitacaoServicoResponse:
    return cancelar_solicitacao_controller(solicitacao_id, usuario, db)
