from sqlalchemy.orm import Session

from app.pagination import PageParams, build_pagination_meta
from app.schemas import AvaliacaoCreateRequest, AvaliacaoPaginatedResponse, AvaliacaoResponse
from models import Avaliacao, Usuario
from services.review_service import (
    criar_avaliacao,
    listar_avaliacoes_cliente,
    listar_avaliacoes_prestador,
)


def criar_avaliacao_controller(
    solicitacao_id: str,
    payload: AvaliacaoCreateRequest,
    usuario: Usuario,
    db: Session,
) -> AvaliacaoResponse:
    return _to_response(criar_avaliacao(db, solicitacao_id, payload, usuario))


def listar_avaliacoes_prestador_controller(
    prestador_id: str,
    usuario: Usuario,
    db: Session,
    pagination: PageParams,
) -> AvaliacaoPaginatedResponse:
    avaliacoes, total = listar_avaliacoes_prestador(db, prestador_id, usuario, pagination)
    return AvaliacaoPaginatedResponse(
        items=[_to_response(avaliacao) for avaliacao in avaliacoes],
        meta=build_pagination_meta(total, pagination),
    )


def listar_avaliacoes_cliente_controller(
    cliente_id: str,
    usuario: Usuario,
    db: Session,
    pagination: PageParams,
) -> AvaliacaoPaginatedResponse:
    avaliacoes, total = listar_avaliacoes_cliente(db, cliente_id, usuario, pagination)
    return AvaliacaoPaginatedResponse(
        items=[_to_response(avaliacao) for avaliacao in avaliacoes],
        meta=build_pagination_meta(total, pagination),
    )


def _to_response(avaliacao: Avaliacao) -> AvaliacaoResponse:
    return AvaliacaoResponse(
        id=str(avaliacao.id),
        solicitacao_id=str(avaliacao.solicitacao_id),
        avaliador_usuario_id=str(avaliacao.avaliador_usuario_id),
        avaliado_usuario_id=str(avaliacao.avaliado_usuario_id),
        tipo_avaliacao=avaliacao.tipo_avaliacao,
        nota=avaliacao.nota,
        comentario=avaliacao.comentario,
        created_at=avaliacao.created_at.isoformat(),
    )
