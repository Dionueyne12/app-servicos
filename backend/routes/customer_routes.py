from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas import CadastroPerfilRequest, UsuarioResponse
from controllers.customer_controller import cadastro_cliente_controller
from database.session import get_db


router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.post("/cadastro", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_cliente(
    payload: CadastroPerfilRequest,
    db: Session = Depends(get_db),
) -> UsuarioResponse:
    return cadastro_cliente_controller(payload, db)
