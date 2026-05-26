from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.pagination import PageParams
from app.schemas import NotificacaoPaginatedResponse, NotificacaoResponse
from auth.dependencies import get_current_user
from controllers.notification_controller import (
    excluir_notificacao_controller,
    listar_notificacoes_controller,
    marcar_notificacao_lida_controller,
    marcar_todas_lidas_controller,
)
from database.session import get_db
from models import Usuario


router = APIRouter(prefix="/notificacoes", tags=["notificacoes"])


@router.get("", response_model=NotificacaoPaginatedResponse)
def listar_notificacoes(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
) -> NotificacaoPaginatedResponse:
    return listar_notificacoes_controller(usuario, db, pagination)


@router.get("/nao-lidas", response_model=NotificacaoPaginatedResponse)
def listar_notificacoes_nao_lidas(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
) -> NotificacaoPaginatedResponse:
    return listar_notificacoes_controller(usuario, db, pagination, apenas_nao_lidas=True)


@router.patch("/{notificacao_id}/marcar-lida", response_model=NotificacaoResponse)
def marcar_notificacao_lida(
    notificacao_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificacaoResponse:
    return marcar_notificacao_lida_controller(notificacao_id, usuario, db)


@router.patch("/marcar-todas-lidas")
def marcar_todas_lidas(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    return marcar_todas_lidas_controller(usuario, db)


@router.delete("/{notificacao_id}", response_model=NotificacaoResponse)
def excluir_notificacao(
    notificacao_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificacaoResponse:
    return excluir_notificacao_controller(notificacao_id, usuario, db)
