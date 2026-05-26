from sqlalchemy.orm import Session

from app.pagination import PageParams, build_pagination_meta
from app.schemas import (
    MensagemSolicitacaoCreateRequest,
    MensagemSolicitacaoPaginatedResponse,
    MensagemSolicitacaoResponse,
)
from models import MensagemSolicitacao, Usuario
from services.chat_service import criar_mensagem, excluir_mensagem, listar_mensagens, visualizar_mensagem


def criar_mensagem_controller(
    solicitacao_id: str,
    payload: MensagemSolicitacaoCreateRequest,
    usuario: Usuario,
    db: Session,
) -> MensagemSolicitacaoResponse:
    return _to_response(criar_mensagem(db, solicitacao_id, payload, usuario))


def listar_mensagens_controller(
    solicitacao_id: str,
    usuario: Usuario,
    db: Session,
    pagination: PageParams,
) -> MensagemSolicitacaoPaginatedResponse:
    mensagens, total, nao_lidas = listar_mensagens(db, solicitacao_id, usuario, pagination)
    return MensagemSolicitacaoPaginatedResponse(
        items=[_to_response(mensagem) for mensagem in mensagens],
        meta=build_pagination_meta(total, pagination),
        nao_lidas=nao_lidas,
    )


def visualizar_mensagem_controller(
    mensagem_id: str,
    usuario: Usuario,
    db: Session,
) -> MensagemSolicitacaoResponse:
    return _to_response(visualizar_mensagem(db, mensagem_id, usuario))


def excluir_mensagem_controller(
    mensagem_id: str,
    usuario: Usuario,
    db: Session,
) -> MensagemSolicitacaoResponse:
    return _to_response(excluir_mensagem(db, mensagem_id, usuario))


def _to_response(mensagem: MensagemSolicitacao) -> MensagemSolicitacaoResponse:
    return MensagemSolicitacaoResponse(
        id=str(mensagem.id),
        solicitacao_id=str(mensagem.solicitacao_id),
        remetente_usuario_id=str(mensagem.remetente_usuario_id),
        destinatario_usuario_id=str(mensagem.destinatario_usuario_id),
        tipo_mensagem=mensagem.tipo_mensagem,
        mensagem=mensagem.mensagem,
        arquivo_url=mensagem.arquivo_url,
        visualizada=mensagem.visualizada,
        data_visualizacao=(
            mensagem.data_visualizacao.isoformat() if mensagem.data_visualizacao else None
        ),
        created_at=mensagem.created_at.isoformat(),
    )
