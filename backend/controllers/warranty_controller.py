from sqlalchemy.orm import Session

from app.pagination import PageParams, build_pagination_meta
from app.schemas import (
    GarantiaAcionamentoRequest,
    GarantiaAdminAcaoRequest,
    GarantiaServicoPaginatedResponse,
    GarantiaServicoResponse,
)
from models import Usuario
from services.warranty_service import (
    acionar_garantia,
    alterar_status_garantia_admin,
    buscar_garantia,
    listar_garantias,
)


def listar_garantias_controller(
    db: Session,
    usuario: Usuario,
    pagination: PageParams,
    status_garantia: str | None,
) -> GarantiaServicoPaginatedResponse:
    garantias, total = listar_garantias(db, usuario, pagination, status_garantia)
    return GarantiaServicoPaginatedResponse(
        items=[_to_response(garantia) for garantia in garantias],
        meta=build_pagination_meta(total, pagination),
    )


def buscar_garantia_controller(db: Session, garantia_id: str, usuario: Usuario) -> GarantiaServicoResponse:
    return _to_response(buscar_garantia(db, garantia_id, usuario))


def acionar_garantia_controller(
    db: Session,
    solicitacao_id: str,
    payload: GarantiaAcionamentoRequest,
    usuario: Usuario,
) -> GarantiaServicoResponse:
    return _to_response(
        acionar_garantia(
            db,
            solicitacao_id,
            payload.descricao_problema,
            payload.observacao_cliente,
            payload.fotos,
            usuario,
        )
    )


def acao_admin_garantia_controller(
    db: Session,
    garantia_id: str,
    acao: str,
    payload: GarantiaAdminAcaoRequest,
    usuario: Usuario,
) -> GarantiaServicoResponse:
    return _to_response(
        alterar_status_garantia_admin(
            db,
            garantia_id,
            acao,
            payload.observacao_admin,
            payload.procedente,
            usuario,
        )
    )


def _to_response(garantia) -> GarantiaServicoResponse:
    return GarantiaServicoResponse(
        id=str(garantia.id),
        solicitacao_id=str(garantia.solicitacao_id),
        prestador_id=str(garantia.prestador_id),
        cliente_id=str(garantia.cliente_id),
        servico_tabelado_id=str(garantia.servico_tabelado_id) if garantia.servico_tabelado_id else None,
        pagamento_simulado_id=str(garantia.pagamento_simulado_id) if garantia.pagamento_simulado_id else None,
        pagamento_id=str(garantia.pagamento_id) if garantia.pagamento_id else None,
        data_inicio_garantia=garantia.data_inicio_garantia.isoformat(),
        data_fim_garantia=garantia.data_fim_garantia.isoformat(),
        status_garantia=garantia.status_garantia,
        valor_retido=float(garantia.valor_retido),
        valor_liberado_inicial=float(garantia.valor_liberado_inicial),
        percentual_retencao=float(garantia.percentual_retencao),
        dias_garantia=garantia.dias_garantia,
        dias_liberacao_primeiro_repasse=garantia.dias_liberacao_primeiro_repasse,
        descricao_problema=garantia.descricao_problema,
        observacao_cliente=garantia.observacao_cliente,
        observacao_admin=garantia.observacao_admin,
        bloqueio_repasse=garantia.bloqueio_repasse,
        procedente=garantia.procedente,
        data_acionamento=garantia.data_acionamento.isoformat() if garantia.data_acionamento else None,
        data_resolucao=garantia.data_resolucao.isoformat() if garantia.data_resolucao else None,
        created_at=garantia.created_at.isoformat(),
    )
