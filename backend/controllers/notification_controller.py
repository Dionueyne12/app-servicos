from sqlalchemy.orm import Session

from app.pagination import PageParams, build_pagination_meta
from app.schemas import NotificacaoPaginatedResponse, NotificacaoResponse
from models import Notificacao, Usuario
from services.notification_service import (
    excluir_notificacao,
    listar_notificacoes,
    marcar_notificacao_lida,
    marcar_todas_lidas,
)


def listar_notificacoes_controller(
    usuario: Usuario,
    db: Session,
    pagination: PageParams,
    apenas_nao_lidas: bool = False,
) -> NotificacaoPaginatedResponse:
    notificacoes, total, nao_lidas = listar_notificacoes(db, usuario, pagination, apenas_nao_lidas)
    return NotificacaoPaginatedResponse(
        items=[_to_response(notificacao) for notificacao in notificacoes],
        meta=build_pagination_meta(total, pagination),
        nao_lidas=nao_lidas,
    )


def marcar_notificacao_lida_controller(
    notificacao_id: str,
    usuario: Usuario,
    db: Session,
) -> NotificacaoResponse:
    return _to_response(marcar_notificacao_lida(db, notificacao_id, usuario))


def marcar_todas_lidas_controller(usuario: Usuario, db: Session) -> dict[str, int]:
    return {"atualizadas": marcar_todas_lidas(db, usuario)}


def excluir_notificacao_controller(
    notificacao_id: str,
    usuario: Usuario,
    db: Session,
) -> NotificacaoResponse:
    return _to_response(excluir_notificacao(db, notificacao_id, usuario))


def _to_response(notificacao: Notificacao) -> NotificacaoResponse:
    return NotificacaoResponse(
        id=str(notificacao.id),
        usuario_id=str(notificacao.usuario_id),
        solicitacao_id=str(notificacao.solicitacao_id) if notificacao.solicitacao_id else None,
        tipo_notificacao=notificacao.tipo_notificacao,
        titulo=notificacao.titulo,
        mensagem=notificacao.mensagem,
        lida=notificacao.lida,
        data_leitura=notificacao.data_leitura.isoformat() if notificacao.data_leitura else None,
        prioridade=notificacao.prioridade,
        canal=notificacao.canal,
        created_at=notificacao.created_at.isoformat(),
    )
