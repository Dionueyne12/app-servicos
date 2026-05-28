from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.pagination import PageParams
from app.schemas import (
    GarantiaAcionamentoRequest,
    GarantiaAdminAcaoRequest,
    GarantiaServicoPaginatedResponse,
    GarantiaServicoResponse,
)
from auth.dependencies import get_current_user, require_admin
from controllers.warranty_controller import (
    acao_admin_garantia_controller,
    acionar_garantia_controller,
    buscar_garantia_controller,
    listar_garantias_controller,
)
from database.session import get_db
from models import Usuario


router = APIRouter(tags=["garantias"])


@router.post("/solicitacoes/{solicitacao_id}/garantia/acionar", response_model=GarantiaServicoResponse)
def acionar_garantia(
    solicitacao_id: str,
    payload: GarantiaAcionamentoRequest,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GarantiaServicoResponse:
    return acionar_garantia_controller(db, solicitacao_id, payload, usuario)


@router.get("/garantias/{garantia_id}", response_model=GarantiaServicoResponse)
def buscar_garantia(
    garantia_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GarantiaServicoResponse:
    return buscar_garantia_controller(db, garantia_id, usuario)


@router.get("/admin/garantias", response_model=GarantiaServicoPaginatedResponse)
def listar_garantias_admin(
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
    status_garantia: str | None = Query(default=None, max_length=40),
) -> GarantiaServicoPaginatedResponse:
    return listar_garantias_controller(db, admin, pagination, status_garantia)


@router.patch("/admin/garantias/{garantia_id}/bloquear-retencao", response_model=GarantiaServicoResponse)
def bloquear_retencao_garantia(
    garantia_id: str,
    payload: GarantiaAdminAcaoRequest | None = None,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
) -> GarantiaServicoResponse:
    return acao_admin_garantia_controller(db, garantia_id, "bloquear", payload or GarantiaAdminAcaoRequest(), admin)


@router.patch("/admin/garantias/{garantia_id}/liberar-retencao", response_model=GarantiaServicoResponse)
def liberar_retencao_garantia(
    garantia_id: str,
    payload: GarantiaAdminAcaoRequest | None = None,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
) -> GarantiaServicoResponse:
    return acao_admin_garantia_controller(db, garantia_id, "liberar", payload or GarantiaAdminAcaoRequest(), admin)


@router.patch("/admin/garantias/{garantia_id}/resolver", response_model=GarantiaServicoResponse)
def resolver_garantia(
    garantia_id: str,
    payload: GarantiaAdminAcaoRequest | None = None,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
) -> GarantiaServicoResponse:
    return acao_admin_garantia_controller(db, garantia_id, "resolver", payload or GarantiaAdminAcaoRequest(), admin)


@router.patch("/admin/garantias/{garantia_id}/negar", response_model=GarantiaServicoResponse)
def negar_garantia(
    garantia_id: str,
    payload: GarantiaAdminAcaoRequest | None = None,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
) -> GarantiaServicoResponse:
    return acao_admin_garantia_controller(db, garantia_id, "negar", payload or GarantiaAdminAcaoRequest(), admin)
