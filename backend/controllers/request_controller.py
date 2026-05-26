from sqlalchemy.orm import Session

from app.pagination import PageParams, build_pagination_meta
from app.schemas import (
    SolicitacaoServicoCreateRequest,
    SolicitacaoServicoPaginatedResponse,
    SolicitacaoProblemaRequest,
    SolicitacaoServicoResponse,
    SolicitacaoStatusUpdateRequest,
    SolicitacaoServicoUpdateRequest,
)
from models import Usuario
from services import (
    buscar_solicitacao,
    cancelar_solicitacao,
    concluir_servico,
    confirmar_conclusao_servico,
    criar_solicitacao,
    editar_solicitacao,
    informar_problema_servico,
    iniciar_servico,
    aceitar_solicitacao,
    atualizar_status_solicitacao,
    listar_solicitacoes_disponiveis,
    listar_servicos_do_prestador,
    listar_solicitacoes,
)


def criar_solicitacao_controller(
    payload: SolicitacaoServicoCreateRequest,
    usuario: Usuario,
    db: Session,
) -> SolicitacaoServicoResponse:
    return _to_response(criar_solicitacao(db, payload, usuario))


def listar_solicitacoes_controller(
    usuario: Usuario,
    db: Session,
    pagination: PageParams,
    status: str | None,
    busca: str | None,
) -> SolicitacaoServicoPaginatedResponse:
    solicitacoes, total = listar_solicitacoes(db, usuario, pagination, status, busca)
    return SolicitacaoServicoPaginatedResponse(
        items=[_to_response(solicitacao) for solicitacao in solicitacoes],
        meta=build_pagination_meta(total, pagination),
    )


def listar_solicitacoes_disponiveis_controller(
    usuario: Usuario,
    db: Session,
    pagination: PageParams,
) -> SolicitacaoServicoPaginatedResponse:
    solicitacoes, total = listar_solicitacoes_disponiveis(db, usuario, pagination)
    return SolicitacaoServicoPaginatedResponse(
        items=[_to_response(solicitacao) for solicitacao in solicitacoes],
        meta=build_pagination_meta(total, pagination),
    )


def listar_meus_servicos_prestador_controller(
    usuario: Usuario,
    db: Session,
    pagination: PageParams,
    status: str | None,
) -> SolicitacaoServicoPaginatedResponse:
    solicitacoes, total = listar_servicos_do_prestador(db, usuario, pagination, status)
    return SolicitacaoServicoPaginatedResponse(
        items=[_to_response(solicitacao) for solicitacao in solicitacoes],
        meta=build_pagination_meta(total, pagination),
    )


def buscar_solicitacao_controller(
    solicitacao_id: str,
    usuario: Usuario,
    db: Session,
) -> SolicitacaoServicoResponse:
    return _to_response(buscar_solicitacao(db, solicitacao_id, usuario))


def editar_solicitacao_controller(
    solicitacao_id: str,
    payload: SolicitacaoServicoUpdateRequest,
    usuario: Usuario,
    db: Session,
) -> SolicitacaoServicoResponse:
    return _to_response(editar_solicitacao(db, solicitacao_id, payload, usuario))


def cancelar_solicitacao_controller(
    solicitacao_id: str,
    usuario: Usuario,
    db: Session,
) -> SolicitacaoServicoResponse:
    return _to_response(cancelar_solicitacao(db, solicitacao_id, usuario))


def aceitar_solicitacao_controller(
    solicitacao_id: str,
    usuario: Usuario,
    db: Session,
) -> SolicitacaoServicoResponse:
    return _to_response(aceitar_solicitacao(db, solicitacao_id, usuario))


def atualizar_status_solicitacao_controller(
    solicitacao_id: str,
    payload: SolicitacaoStatusUpdateRequest,
    usuario: Usuario,
    db: Session,
) -> SolicitacaoServicoResponse:
    return _to_response(atualizar_status_solicitacao(db, solicitacao_id, payload.status, usuario))


def iniciar_servico_controller(
    solicitacao_id: str,
    usuario: Usuario,
    db: Session,
) -> SolicitacaoServicoResponse:
    return _to_response(iniciar_servico(db, solicitacao_id, usuario))


def concluir_servico_controller(
    solicitacao_id: str,
    usuario: Usuario,
    db: Session,
) -> SolicitacaoServicoResponse:
    return _to_response(concluir_servico(db, solicitacao_id, usuario))


def confirmar_conclusao_controller(
    solicitacao_id: str,
    usuario: Usuario,
    db: Session,
) -> SolicitacaoServicoResponse:
    return _to_response(confirmar_conclusao_servico(db, solicitacao_id, usuario))


def informar_problema_controller(
    solicitacao_id: str,
    payload: SolicitacaoProblemaRequest,
    usuario: Usuario,
    db: Session,
) -> SolicitacaoServicoResponse:
    return _to_response(
        informar_problema_servico(db, solicitacao_id, payload.observacao_problema, usuario)
    )


def _to_response(solicitacao) -> SolicitacaoServicoResponse:
    material = None
    if solicitacao.material is not None:
        material = {
            "id": str(solicitacao.material.id),
            "tipo_material": solicitacao.material.escolha_cliente,
            "descricao_material": solicitacao.material.descricao_material,
            "valor_material_estimado": (
                float(solicitacao.material.valor_estimado)
                if solicitacao.material.valor_estimado is not None
                else None
            ),
            "necessita_aprovacao_cliente": solicitacao.material.necessita_aprovacao_cliente,
            "aprovado_pelo_cliente": solicitacao.material.aprovado_pelo_cliente,
            "status_material": solicitacao.material.status_material,
            "observacao_cliente": solicitacao.material.observacao_cliente,
        }
    valor_mao_obra = (
        float(solicitacao.preco_mao_obra_snapshot)
        if solicitacao.preco_mao_obra_snapshot is not None
        else 0
    )
    valor_material_total = 0
    if solicitacao.material is not None and solicitacao.material.valor_estimado is not None:
        valor_material_total = float(solicitacao.material.valor_estimado)

    return SolicitacaoServicoResponse(
        id=str(solicitacao.id),
        cliente_id=str(solicitacao.cliente_id),
        prestador_id=str(solicitacao.prestador_id) if solicitacao.prestador_id else None,
        tipo_servico=solicitacao.tipo_servico,
        servico_tabelado_id=(
            str(solicitacao.servico_tabelado_id) if solicitacao.servico_tabelado_id else None
        ),
        categoria_id=str(solicitacao.categoria_id) if solicitacao.categoria_id else None,
        descricao_problema=solicitacao.descricao,
        endereco=solicitacao.endereco,
        urgencia=solicitacao.urgencia,
        melhor_horario=solicitacao.melhor_horario,
        observacoes=solicitacao.observacoes,
        valor_mao_obra=valor_mao_obra,
        valor_material_total=valor_material_total,
        valor_total_estimado=valor_mao_obra + valor_material_total,
        tempo_estimado=solicitacao.tempo_estimado_snapshot_minutos,
        status=solicitacao.status_codigo,
        material=material,
    )
