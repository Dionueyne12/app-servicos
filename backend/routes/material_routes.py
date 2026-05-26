from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas import MaterialClienteAcaoRequest, MaterialServicoCreateRequest, MaterialServicoResponse
from auth.dependencies import get_current_user
from controllers.material_controller import (
    aprovar_material_controller,
    comprado_retirado_material_controller,
    criar_material_controller,
    listar_materiais_controller,
    recusar_material_controller,
    solicitar_alteracao_material_controller,
)
from database.session import get_db
from models import Usuario


router = APIRouter(tags=["materiais"])


@router.post("/solicitacoes/{solicitacao_id}/materiais", response_model=MaterialServicoResponse)
def criar_material(
    solicitacao_id: str,
    payload: MaterialServicoCreateRequest,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MaterialServicoResponse:
    return criar_material_controller(solicitacao_id, payload, usuario, db)


@router.get("/solicitacoes/{solicitacao_id}/materiais", response_model=list[MaterialServicoResponse])
def listar_materiais(
    solicitacao_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MaterialServicoResponse]:
    return listar_materiais_controller(solicitacao_id, usuario, db)


@router.patch("/materiais/{material_id}/aprovar", response_model=MaterialServicoResponse)
def aprovar_material(
    material_id: str,
    payload: MaterialClienteAcaoRequest,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MaterialServicoResponse:
    return aprovar_material_controller(material_id, payload, usuario, db)


@router.patch("/materiais/{material_id}/recusar", response_model=MaterialServicoResponse)
def recusar_material(
    material_id: str,
    payload: MaterialClienteAcaoRequest,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MaterialServicoResponse:
    return recusar_material_controller(material_id, payload, usuario, db)


@router.patch("/materiais/{material_id}/solicitar-alteracao", response_model=MaterialServicoResponse)
def solicitar_alteracao_material(
    material_id: str,
    payload: MaterialClienteAcaoRequest,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MaterialServicoResponse:
    return solicitar_alteracao_material_controller(material_id, payload, usuario, db)


@router.patch("/materiais/{material_id}/comprado-retirado", response_model=MaterialServicoResponse)
def comprado_retirado_material(
    material_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MaterialServicoResponse:
    return comprado_retirado_material_controller(material_id, usuario, db)
