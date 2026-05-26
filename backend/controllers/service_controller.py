from sqlalchemy.orm import Session

from app.schemas import (
    CategoriaServicoResponse,
    ServicoTabeladoCreateRequest,
    ServicoTabeladoPaginatedResponse,
    ServicoTabeladoResponse,
    ServicoTabeladoUpdateRequest,
)
from app.pagination import PageParams, build_pagination_meta
from models import Usuario
from services.service_catalog_service import (
    ativar_servico_tabelado,
    criar_servico_tabelado,
    editar_servico_tabelado,
    listar_categorias_servico,
    listar_servicos_tabelados,
)


def listar_categorias_controller(
    db: Session,
    ativo: bool | None,
) -> list[CategoriaServicoResponse]:
    return [
        CategoriaServicoResponse(
            id=str(categoria.id),
            nome=categoria.nome,
            descricao=categoria.descricao,
            ativo=categoria.ativo,
        )
        for categoria in listar_categorias_servico(db, ativo)
    ]


def listar_servicos_controller(
    db: Session,
    pagination: PageParams,
    busca: str | None,
    ativo: bool | None,
) -> ServicoTabeladoPaginatedResponse:
    servicos, total = listar_servicos_tabelados(db, pagination, busca, ativo)
    return ServicoTabeladoPaginatedResponse(
        items=[_to_response(servico) for servico in servicos],
        meta=build_pagination_meta(total, pagination),
    )


def criar_servico_controller(
    payload: ServicoTabeladoCreateRequest,
    db: Session,
    usuario: Usuario,
) -> ServicoTabeladoResponse:
    return _to_response(criar_servico_tabelado(db, payload, usuario))


def editar_servico_controller(
    servico_id: str,
    payload: ServicoTabeladoUpdateRequest,
    db: Session,
    usuario: Usuario,
) -> ServicoTabeladoResponse:
    return _to_response(editar_servico_tabelado(db, servico_id, payload, usuario))


def ativar_servico_controller(
    servico_id: str,
    ativo: bool,
    db: Session,
    usuario: Usuario,
) -> ServicoTabeladoResponse:
    return _to_response(ativar_servico_tabelado(db, servico_id, ativo, usuario))


def _to_response(servico) -> ServicoTabeladoResponse:
    return ServicoTabeladoResponse(
        id=str(servico.id),
        categoria_id=str(servico.categoria_id),
        nome=servico.nome,
        descricao=servico.descricao,
        preco_mao_obra=float(servico.preco_mao_obra),
        tempo_estimado_minutos=servico.tempo_estimado_minutos,
        precisa_material=servico.precisa_material,
        ativo=servico.ativo,
    )
