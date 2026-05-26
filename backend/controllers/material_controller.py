from sqlalchemy.orm import Session

from app.schemas import MaterialClienteAcaoRequest, MaterialServicoCreateRequest, MaterialServicoResponse
from models import MaterialServico, Usuario
from services.material_service import (
    aprovar_material,
    criar_ou_atualizar_material,
    listar_materiais_solicitacao,
    marcar_comprado_retirado,
    recusar_material,
    solicitar_alteracao_material,
)


def criar_material_controller(
    solicitacao_id: str,
    payload: MaterialServicoCreateRequest,
    usuario: Usuario,
    db: Session,
) -> MaterialServicoResponse:
    return _to_response(criar_ou_atualizar_material(db, solicitacao_id, payload, usuario))


def listar_materiais_controller(
    solicitacao_id: str,
    usuario: Usuario,
    db: Session,
) -> list[MaterialServicoResponse]:
    return [_to_response(material) for material in listar_materiais_solicitacao(db, solicitacao_id, usuario)]


def aprovar_material_controller(
    material_id: str,
    payload: MaterialClienteAcaoRequest,
    usuario: Usuario,
    db: Session,
) -> MaterialServicoResponse:
    return _to_response(aprovar_material(db, material_id, usuario, payload.observacao_cliente))


def recusar_material_controller(
    material_id: str,
    payload: MaterialClienteAcaoRequest,
    usuario: Usuario,
    db: Session,
) -> MaterialServicoResponse:
    return _to_response(recusar_material(db, material_id, usuario, payload.observacao_cliente))


def solicitar_alteracao_material_controller(
    material_id: str,
    payload: MaterialClienteAcaoRequest,
    usuario: Usuario,
    db: Session,
) -> MaterialServicoResponse:
    return _to_response(solicitar_alteracao_material(db, material_id, usuario, payload.observacao_cliente))


def comprado_retirado_material_controller(
    material_id: str,
    usuario: Usuario,
    db: Session,
) -> MaterialServicoResponse:
    return _to_response(marcar_comprado_retirado(db, material_id, usuario))


def _to_response(material: MaterialServico) -> MaterialServicoResponse:
    return MaterialServicoResponse(
        id=str(material.id),
        tipo_material=material.escolha_cliente,
        descricao_material=material.descricao_material,
        valor_material_estimado=(
            float(material.valor_estimado) if material.valor_estimado is not None else None
        ),
        necessita_aprovacao_cliente=material.necessita_aprovacao_cliente,
        aprovado_pelo_cliente=material.aprovado_pelo_cliente,
        status_material=material.status_material,
        observacao_cliente=material.observacao_cliente,
    )
