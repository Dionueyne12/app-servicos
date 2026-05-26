from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.orm import Session

from app.schemas import FotoServicoResponse
from auth.dependencies import get_current_user
from controllers.photo_controller import (
    excluir_foto_controller,
    listar_fotos_controller,
    upload_foto_controller,
)
from database.session import get_db
from models import Usuario


router = APIRouter(tags=["fotos-servico"])


@router.post(
    "/solicitacoes/{solicitacao_id}/fotos",
    response_model=FotoServicoResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_foto_solicitacao(
    solicitacao_id: str,
    arquivo: bytes = Body(..., media_type="application/octet-stream"),
    nome_original: str = Query(..., min_length=1, max_length=255),
    mime_type: str = Query(..., max_length=80),
    tipo_foto: str = Query(..., max_length=40),
    descricao: str | None = Query(default=None, max_length=500),
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FotoServicoResponse:
    return upload_foto_controller(
        solicitacao_id,
        usuario,
        db,
        arquivo,
        nome_original,
        mime_type,
        tipo_foto,
        descricao,
    )


@router.get("/solicitacoes/{solicitacao_id}/fotos", response_model=list[FotoServicoResponse])
def listar_fotos_solicitacao(
    solicitacao_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[FotoServicoResponse]:
    return listar_fotos_controller(solicitacao_id, usuario, db)


@router.delete("/fotos-servico/{foto_id}", response_model=FotoServicoResponse)
def excluir_foto_servico(
    foto_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FotoServicoResponse:
    return excluir_foto_controller(foto_id, usuario, db)
