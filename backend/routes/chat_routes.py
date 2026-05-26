from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.pagination import PageParams
from app.schemas import (
    MensagemSolicitacaoCreateRequest,
    MensagemSolicitacaoPaginatedResponse,
    MensagemSolicitacaoResponse,
)
from auth.dependencies import get_current_user
from controllers.chat_controller import (
    criar_mensagem_controller,
    excluir_mensagem_controller,
    listar_mensagens_controller,
    visualizar_mensagem_controller,
)
from database.session import get_db
from models import Usuario


router = APIRouter(tags=["mensagens"])


@router.post(
    "/solicitacoes/{solicitacao_id}/mensagens",
    response_model=MensagemSolicitacaoResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_mensagem(
    solicitacao_id: str,
    payload: MensagemSolicitacaoCreateRequest,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MensagemSolicitacaoResponse:
    return criar_mensagem_controller(solicitacao_id, payload, usuario, db)


@router.get(
    "/solicitacoes/{solicitacao_id}/mensagens",
    response_model=MensagemSolicitacaoPaginatedResponse,
)
def listar_mensagens(
    solicitacao_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
) -> MensagemSolicitacaoPaginatedResponse:
    return listar_mensagens_controller(solicitacao_id, usuario, db, pagination)


@router.patch("/mensagens/{mensagem_id}/visualizar", response_model=MensagemSolicitacaoResponse)
def visualizar_mensagem(
    mensagem_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MensagemSolicitacaoResponse:
    return visualizar_mensagem_controller(mensagem_id, usuario, db)


@router.delete("/mensagens/{mensagem_id}", response_model=MensagemSolicitacaoResponse)
def excluir_mensagem(
    mensagem_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MensagemSolicitacaoResponse:
    return excluir_mensagem_controller(mensagem_id, usuario, db)
