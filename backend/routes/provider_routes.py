from fastapi import APIRouter, Depends, status
from fastapi import Query
from sqlalchemy.orm import Session

from app.pagination import PageParams
from app.schemas import CadastroPerfilRequest, UsuarioResponse
from app.schemas import SolicitacaoServicoPaginatedResponse
from auth.dependencies import require_prestador
from controllers.provider_controller import cadastro_prestador_controller
from controllers.request_controller import listar_meus_servicos_prestador_controller
from database.session import get_db
from models import Usuario


router = APIRouter(prefix="/prestadores", tags=["prestadores"])


@router.post("/cadastro", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_prestador(
    payload: CadastroPerfilRequest,
    db: Session = Depends(get_db),
) -> UsuarioResponse:
    return cadastro_prestador_controller(payload, db)


@router.get("/meus-servicos", response_model=SolicitacaoServicoPaginatedResponse)
def listar_meus_servicos(
    usuario: Usuario = Depends(require_prestador),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
    status: str | None = Query(default=None, max_length=60),
) -> SolicitacaoServicoPaginatedResponse:
    return listar_meus_servicos_prestador_controller(usuario, db, pagination, status)
