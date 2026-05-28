from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.pagination import PageParams
from app.schemas import (
    CategoriaServicoCreateRequest,
    CategoriaServicoResponse,
    CategoriaServicoUpdateRequest,
    ServicoTabeladoCreateRequest,
    ServicoTabeladoPaginatedResponse,
    ServicoTabeladoResponse,
    ServicoTabeladoUpdateRequest,
)
from auth.dependencies import require_admin
from controllers.service_controller import (
    ativar_categoria_controller,
    ativar_servico_controller,
    criar_categoria_controller,
    criar_servico_controller,
    editar_categoria_controller,
    editar_servico_controller,
    listar_categorias_controller,
    listar_servicos_controller,
)
from database.session import get_db
from models import Usuario


router = APIRouter(prefix="/servicos-tabelados", tags=["servicos-tabelados"])
categorias_router = APIRouter(prefix="/categorias-servico", tags=["categorias-servico"])


@categorias_router.get("", response_model=list[CategoriaServicoResponse])
def listar_categorias(
    db: Session = Depends(get_db),
    ativo: bool | None = Query(default=True),
) -> list[CategoriaServicoResponse]:
    return listar_categorias_controller(db, ativo)


@categorias_router.post("", response_model=CategoriaServicoResponse, status_code=status.HTTP_201_CREATED)
def criar_categoria(
    payload: CategoriaServicoCreateRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_admin),
) -> CategoriaServicoResponse:
    return criar_categoria_controller(payload, db, usuario)


@categorias_router.patch("/{categoria_id}/ativar", response_model=CategoriaServicoResponse)
def ativar_categoria(
    categoria_id: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_admin),
) -> CategoriaServicoResponse:
    return ativar_categoria_controller(categoria_id, True, db, usuario)


@categorias_router.put("/{categoria_id}", response_model=CategoriaServicoResponse)
def editar_categoria(
    categoria_id: str,
    payload: CategoriaServicoUpdateRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_admin),
) -> CategoriaServicoResponse:
    return editar_categoria_controller(categoria_id, payload, db, usuario)


@categorias_router.patch("/{categoria_id}/desativar", response_model=CategoriaServicoResponse)
def desativar_categoria(
    categoria_id: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_admin),
) -> CategoriaServicoResponse:
    return ativar_categoria_controller(categoria_id, False, db, usuario)


@router.get("", response_model=ServicoTabeladoPaginatedResponse)
def listar_servicos(
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
    busca: str | None = Query(default=None, min_length=2, max_length=120),
    ativo: bool | None = Query(default=True),
) -> ServicoTabeladoPaginatedResponse:
    return listar_servicos_controller(db, pagination, busca, ativo)


@router.post("", response_model=ServicoTabeladoResponse, status_code=status.HTTP_201_CREATED)
def criar_servico(
    payload: ServicoTabeladoCreateRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_admin),
) -> ServicoTabeladoResponse:
    return criar_servico_controller(payload, db, usuario)


@router.put("/{servico_id}", response_model=ServicoTabeladoResponse)
def editar_servico(
    servico_id: str,
    payload: ServicoTabeladoUpdateRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_admin),
) -> ServicoTabeladoResponse:
    return editar_servico_controller(servico_id, payload, db, usuario)


@router.patch("/{servico_id}/ativar", response_model=ServicoTabeladoResponse)
def ativar_servico(
    servico_id: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_admin),
) -> ServicoTabeladoResponse:
    return ativar_servico_controller(servico_id, True, db, usuario)


@router.patch("/{servico_id}/desativar", response_model=ServicoTabeladoResponse)
def desativar_servico(
    servico_id: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_admin),
) -> ServicoTabeladoResponse:
    return ativar_servico_controller(servico_id, False, db, usuario)
