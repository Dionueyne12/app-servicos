from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.pagination import PageParams
from app.schemas import SolicitacaoServicoCreateRequest, SolicitacaoServicoUpdateRequest
from models import (
    CategoriaServico,
    Cliente,
    HistoricoEdicao,
    HistoricoStatus,
    MaterialServico,
    ServicoTabelado,
    SolicitacaoServico,
    Usuario,
)
from utils.exceptions import BadRequestError, UnauthorizedError


STATUS_AGUARDANDO_PRESTADOR = "aguardando_prestador"
STATUS_CANCELADO = "cancelado"
STATUS_ACEITO = "aceito"
STATUS_EM_ANDAMENTO = "em_andamento"
STATUS_AGUARDANDO_CONFIRMACAO_CLIENTE = "aguardando_confirmacao_cliente"
STATUS_CONCLUIDO = "concluido"
STATUS_EM_ANALISE = "em_analise"
STATUS_MATERIAL_AGUARDANDO_APROVACAO = "aguardando_aprovacao_cliente"
STATUS_MATERIAL_APROVADO = "material_aprovado"
STATUS_BLOQUEIA_EDICAO = {
    "aceito",
    "aguardando_avaliacao_material",
    "aguardando_aprovacao_cliente",
    "material_aprovado",
    "em_andamento",
    "aguardando_confirmacao_cliente",
    "concluido",
    "cancelado",
    "em_analise",
}
STATUS_TRANSITIONS = {
    "aceito": {"aguardando_avaliacao_material", "em_andamento", "cancelado"},
    "aguardando_avaliacao_material": {
        "aguardando_aprovacao_cliente",
        "em_andamento",
        "cancelado",
    },
    "aguardando_aprovacao_cliente": {"material_aprovado", "cancelado"},
    "material_aprovado": {"em_andamento", "cancelado"},
    "em_andamento": {"aguardando_confirmacao_cliente", "cancelado", "em_analise"},
    "aguardando_confirmacao_cliente": {"concluido", "em_analise"},
    "em_analise": {"cancelado", "em_andamento"},
}


def criar_solicitacao(
    db: Session,
    payload: SolicitacaoServicoCreateRequest,
    usuario: Usuario,
) -> SolicitacaoServico:
    cliente = _validar_cliente_da_solicitacao(db, payload.cliente_id, usuario)
    categoria_id, servico, valor_mao_obra, tempo_estimado = _resolver_tipo_servico(db, payload)

    solicitacao = SolicitacaoServico(
        cliente_id=cliente.id,
        servico_tabelado_id=servico.id if servico else None,
        categoria_id=categoria_id,
        tipo_servico=payload.tipo_servico,
        titulo=servico.nome if servico else "Servico personalizado",
        descricao=payload.descricao_problema.strip(),
        endereco=payload.endereco.strip(),
        urgencia=payload.urgencia,
        melhor_horario=payload.melhor_horario,
        observacoes=payload.observacoes,
        status_codigo=STATUS_AGUARDANDO_PRESTADOR,
        preco_mao_obra_snapshot=valor_mao_obra,
        tempo_estimado_snapshot_minutos=tempo_estimado,
        created_by_usuario_id=usuario.id,
    )
    db.add(solicitacao)
    db.flush()

    db.add(MaterialServico(solicitacao_id=solicitacao.id, escolha_cliente=payload.tipo_material))
    db.add(
        HistoricoStatus(
            solicitacao_id=solicitacao.id,
            status_anterior=None,
            status_novo=STATUS_AGUARDANDO_PRESTADOR,
            alterado_por_usuario_id=usuario.id,
            observacao="Solicitacao criada pelo cliente.",
        )
    )
    from services.notification_service import criar_notificacao

    criar_notificacao(
        db,
        usuario_id=usuario.id,
        solicitacao_id=solicitacao.id,
        tipo_notificacao="servico_criado",
        titulo="Solicitacao criada",
        mensagem="Sua solicitacao foi criada e esta aguardando um prestador.",
        created_by_usuario_id=usuario.id,
    )

    db.commit()
    return _buscar_solicitacao_por_id(db, solicitacao.id)


def listar_solicitacoes(
    db: Session,
    usuario: Usuario,
    pagination: PageParams,
    status: str | None,
    busca: str | None,
) -> tuple[list[SolicitacaoServico], int]:
    query = select(SolicitacaoServico).options(selectinload(SolicitacaoServico.material))
    count_query = select(func.count()).select_from(SolicitacaoServico)
    filters = [SolicitacaoServico.deleted_at.is_(None)]

    if usuario.tipo_usuario == "cliente":
        if usuario.cliente is None:
            raise UnauthorizedError("Usuario nao possui cadastro de cliente.")
        filters.append(SolicitacaoServico.cliente_id == usuario.cliente.id)
    elif usuario.tipo_usuario != "admin":
        raise UnauthorizedError("Acesso nao permitido para listar solicitacoes.")

    if status:
        filters.append(SolicitacaoServico.status_codigo == status)
    if busca:
        filters.append(SolicitacaoServico.descricao.ilike(f"%{busca.strip()}%"))

    total = db.scalar(count_query.where(*filters)) or 0
    items = list(
        db.scalars(
            query.where(*filters)
            .order_by(SolicitacaoServico.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return items, total


def listar_solicitacoes_disponiveis(
    db: Session,
    usuario: Usuario,
    pagination: PageParams,
) -> tuple[list[SolicitacaoServico], int]:
    if usuario.tipo_usuario != "prestador" or usuario.prestador is None:
        raise UnauthorizedError("Apenas prestadores podem listar solicitacoes disponiveis.")
    _garantir_prestador_aprovado(usuario)

    filters = [
        SolicitacaoServico.deleted_at.is_(None),
        SolicitacaoServico.status_codigo == STATUS_AGUARDANDO_PRESTADOR,
        SolicitacaoServico.prestador_id.is_(None),
    ]
    total = db.scalar(select(func.count()).select_from(SolicitacaoServico).where(*filters)) or 0
    items = list(
        db.scalars(
            select(SolicitacaoServico)
            .where(*filters)
            .options(selectinload(SolicitacaoServico.material))
            .order_by(SolicitacaoServico.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return items, total


def listar_servicos_do_prestador(
    db: Session,
    usuario: Usuario,
    pagination: PageParams,
    status: str | None,
) -> tuple[list[SolicitacaoServico], int]:
    if usuario.tipo_usuario != "prestador" or usuario.prestador is None:
        raise UnauthorizedError("Apenas prestadores podem listar seus servicos.")

    filters = [
        SolicitacaoServico.deleted_at.is_(None),
        SolicitacaoServico.prestador_id == usuario.prestador.id,
    ]
    if status:
        filters.append(SolicitacaoServico.status_codigo == status)

    total = db.scalar(select(func.count()).select_from(SolicitacaoServico).where(*filters)) or 0
    items = list(
        db.scalars(
            select(SolicitacaoServico)
            .where(*filters)
            .options(selectinload(SolicitacaoServico.material))
            .order_by(SolicitacaoServico.updated_at.desc())
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return items, total


def buscar_solicitacao(db: Session, solicitacao_id: str, usuario: Usuario) -> SolicitacaoServico:
    solicitacao = _buscar_solicitacao_por_id(db, _parse_uuid(solicitacao_id, "Solicitacao invalida."))
    _garantir_acesso_solicitacao(solicitacao, usuario)
    return solicitacao


def aceitar_solicitacao(db: Session, solicitacao_id: str, usuario: Usuario) -> SolicitacaoServico:
    if usuario.tipo_usuario != "prestador" or usuario.prestador is None:
        raise UnauthorizedError("Apenas prestadores podem aceitar solicitacoes.")
    _garantir_prestador_aprovado(usuario)

    parsed_id = _parse_uuid(solicitacao_id, "Solicitacao invalida.")
    solicitacao = db.scalar(
        select(SolicitacaoServico)
        .where(SolicitacaoServico.id == parsed_id, SolicitacaoServico.deleted_at.is_(None))
        .with_for_update()
    )
    if solicitacao is None:
        raise BadRequestError("Solicitacao nao encontrada.")

    if solicitacao.prestador_id is not None:
        raise BadRequestError("Solicitacao ja foi aceita por outro prestador.")

    if solicitacao.status_codigo != STATUS_AGUARDANDO_PRESTADOR:
        raise BadRequestError("Somente solicitacoes aguardando prestador podem ser aceitas.")

    status_anterior = solicitacao.status_codigo
    prestador_anterior = solicitacao.prestador_id
    solicitacao.prestador_id = usuario.prestador.id
    solicitacao.status_codigo = "aceito"
    solicitacao.aceito_em = datetime.now(timezone.utc)
    solicitacao.updated_by_usuario_id = usuario.id
    db.add(
        HistoricoStatus(
            solicitacao_id=solicitacao.id,
            status_anterior=status_anterior,
            status_novo="aceito",
            alterado_por_usuario_id=usuario.id,
            observacao="Solicitacao aceita pelo prestador.",
        )
    )
    _registrar_historico_edicoes(
        db,
        solicitacao.id,
        usuario.id,
        [("prestador_id", prestador_anterior, usuario.prestador.id)],
    )
    from services.chat_service import registrar_mensagem_sistema

    registrar_mensagem_sistema(
        db,
        solicitacao,
        "Servico aceito pelo prestador.",
        usuario.id,
    )
    from services.notification_service import notificar_participante_solicitacao

    notificar_participante_solicitacao(
        db,
        solicitacao.id,
        "cliente",
        "servico_aceito",
        "Servico aceito",
        "Um prestador aceitou sua solicitacao.",
        created_by_usuario_id=usuario.id,
    )
    db.commit()
    return _buscar_solicitacao_por_id(db, solicitacao.id)


def atualizar_status_solicitacao(
    db: Session,
    solicitacao_id: str,
    novo_status: str,
    usuario: Usuario,
) -> SolicitacaoServico:
    solicitacao = buscar_solicitacao(db, solicitacao_id, usuario)

    if usuario.tipo_usuario == "prestador":
        if usuario.prestador is None or solicitacao.prestador_id != usuario.prestador.id:
            raise UnauthorizedError("Prestador nao pode alterar servico que nao aceitou.")
    elif usuario.tipo_usuario != "admin":
        raise UnauthorizedError("Apenas prestador ou admin podem alterar status.")

    status_atual = solicitacao.status_codigo
    if novo_status == status_atual:
        return solicitacao

    if usuario.tipo_usuario != "admin":
        permitidos = STATUS_TRANSITIONS.get(status_atual, set())
        if novo_status not in permitidos:
            raise BadRequestError("Transicao de status invalida.")

    solicitacao.status_codigo = novo_status
    solicitacao.updated_by_usuario_id = usuario.id
    _marcar_data_por_status(solicitacao, novo_status)
    db.add(
        HistoricoStatus(
            solicitacao_id=solicitacao.id,
            status_anterior=status_atual,
            status_novo=novo_status,
            alterado_por_usuario_id=usuario.id,
            observacao="Status atualizado.",
        )
    )
    db.commit()
    return _buscar_solicitacao_por_id(db, solicitacao.id)


def iniciar_servico(db: Session, solicitacao_id: str, usuario: Usuario) -> SolicitacaoServico:
    solicitacao = _buscar_solicitacao_para_execucao(db, solicitacao_id)
    _garantir_prestador_aceito(solicitacao, usuario)

    if solicitacao.status_codigo not in {STATUS_ACEITO, STATUS_MATERIAL_APROVADO}:
        raise BadRequestError("Servico so pode ser iniciado apos aceite e material aprovado quando necessario.")
    if _material_aguarda_aprovacao(solicitacao):
        raise BadRequestError("Nao e possivel iniciar sem aprovacao do material.")

    now = datetime.now(timezone.utc)
    changes: list[tuple[str, object, object]] = []
    _set_if_changed(solicitacao, "data_inicio", now, changes)
    _set_if_changed(solicitacao, "iniciado_em", now, changes)
    _alterar_status_com_historico(
        db,
        solicitacao,
        STATUS_EM_ANDAMENTO,
        usuario,
        "Servico iniciado pelo prestador.",
    )
    _registrar_historico_edicoes(db, solicitacao.id, usuario.id, changes)
    from services.chat_service import registrar_mensagem_sistema

    registrar_mensagem_sistema(db, solicitacao, "Servico iniciado pelo prestador.", usuario.id)
    from services.notification_service import notificar_participante_solicitacao

    notificar_participante_solicitacao(
        db,
        solicitacao.id,
        "cliente",
        "servico_iniciado",
        "Servico iniciado",
        "O prestador iniciou o servico.",
        created_by_usuario_id=usuario.id,
    )
    db.commit()
    return _buscar_solicitacao_por_id(db, solicitacao.id)


def concluir_servico(db: Session, solicitacao_id: str, usuario: Usuario) -> SolicitacaoServico:
    solicitacao = _buscar_solicitacao_para_execucao(db, solicitacao_id)
    _garantir_prestador_aceito(solicitacao, usuario)

    if solicitacao.status_codigo != STATUS_EM_ANDAMENTO:
        raise BadRequestError("Servico precisa estar em andamento para ser concluido.")

    now = datetime.now(timezone.utc)
    changes: list[tuple[str, object, object]] = []
    _set_if_changed(solicitacao, "data_conclusao_prestador", now, changes)
    _set_if_changed(solicitacao, "concluido_em", now, changes)
    _alterar_status_com_historico(
        db,
        solicitacao,
        STATUS_AGUARDANDO_CONFIRMACAO_CLIENTE,
        usuario,
        "Servico marcado como concluido pelo prestador.",
    )
    _registrar_historico_edicoes(db, solicitacao.id, usuario.id, changes)
    from services.chat_service import registrar_mensagem_sistema

    registrar_mensagem_sistema(
        db,
        solicitacao,
        "Servico marcado como concluido pelo prestador.",
        usuario.id,
    )
    from services.notification_service import notificar_participante_solicitacao

    notificar_participante_solicitacao(
        db,
        solicitacao.id,
        "cliente",
        "servico_concluido",
        "Servico concluido pelo prestador",
        "O prestador marcou o servico como concluido. Confirme se esta tudo certo.",
        prioridade="alta",
        created_by_usuario_id=usuario.id,
    )
    db.commit()
    return _buscar_solicitacao_por_id(db, solicitacao.id)


def confirmar_conclusao_servico(db: Session, solicitacao_id: str, usuario: Usuario) -> SolicitacaoServico:
    solicitacao = _buscar_solicitacao_para_execucao(db, solicitacao_id)
    _garantir_cliente_dono(solicitacao, usuario)

    if solicitacao.status_codigo != STATUS_AGUARDANDO_CONFIRMACAO_CLIENTE:
        raise BadRequestError("Servico precisa aguardar confirmacao do cliente.")

    now = datetime.now(timezone.utc)
    changes: list[tuple[str, object, object]] = []
    _set_if_changed(solicitacao, "data_confirmacao_cliente", now, changes)
    _alterar_status_com_historico(
        db,
        solicitacao,
        STATUS_CONCLUIDO,
        usuario,
        "Conclusao confirmada pelo cliente.",
    )
    _registrar_historico_edicoes(db, solicitacao.id, usuario.id, changes)
    from services.chat_service import registrar_mensagem_sistema

    registrar_mensagem_sistema(
        db,
        solicitacao,
        "Conclusao confirmada pelo cliente.",
        usuario.id,
    )
    from services.payment_service import gerar_pagamento_simulado
    from services.warranty_service import criar_garantia_apos_conclusao

    pagamento = gerar_pagamento_simulado(db, solicitacao, usuario)
    criar_garantia_apos_conclusao(db, solicitacao, usuario, pagamento)
    db.commit()
    return _buscar_solicitacao_por_id(db, solicitacao.id)


def informar_problema_servico(
    db: Session,
    solicitacao_id: str,
    observacao_problema: str,
    usuario: Usuario,
) -> SolicitacaoServico:
    solicitacao = _buscar_solicitacao_para_execucao(db, solicitacao_id)
    _garantir_cliente_dono(solicitacao, usuario)

    if solicitacao.status_codigo != STATUS_AGUARDANDO_CONFIRMACAO_CLIENTE:
        raise BadRequestError("Problema so pode ser informado quando o servico aguarda confirmacao.")

    changes: list[tuple[str, object, object]] = []
    _set_if_changed(solicitacao, "observacao_problema", observacao_problema.strip(), changes)
    _alterar_status_com_historico(
        db,
        solicitacao,
        STATUS_EM_ANALISE,
        usuario,
        "Cliente informou problema na conclusao do servico.",
    )
    _registrar_historico_edicoes(db, solicitacao.id, usuario.id, changes)
    from services.chat_service import registrar_mensagem_sistema

    registrar_mensagem_sistema(
        db,
        solicitacao,
        "Cliente informou problema na conclusao do servico.",
        usuario.id,
    )
    from services.notification_service import notificar_participante_solicitacao

    notificar_participante_solicitacao(
        db,
        solicitacao.id,
        "prestador",
        "problema_informado",
        "Problema informado",
        "O cliente informou um problema na conclusao do servico.",
        prioridade="alta",
        created_by_usuario_id=usuario.id,
    )
    db.commit()
    return _buscar_solicitacao_por_id(db, solicitacao.id)


def editar_solicitacao(
    db: Session,
    solicitacao_id: str,
    payload: SolicitacaoServicoUpdateRequest,
    usuario: Usuario,
) -> SolicitacaoServico:
    solicitacao = buscar_solicitacao(db, solicitacao_id, usuario)
    _garantir_editavel_antes_aceite(solicitacao)

    changes: list[tuple[str, object, object]] = []

    if payload.tipo_servico is not None:
        _set_if_changed(solicitacao, "tipo_servico", payload.tipo_servico, changes)

    if payload.tipo_servico is not None or payload.servico_tabelado_id is not None or payload.categoria_id is not None:
        merged = SolicitacaoServicoCreateRequest(
            cliente_id=str(solicitacao.cliente_id),
            tipo_servico=payload.tipo_servico or solicitacao.tipo_servico,
            servico_tabelado_id=(
                payload.servico_tabelado_id
                if payload.servico_tabelado_id is not None
                else str(solicitacao.servico_tabelado_id)
                if solicitacao.servico_tabelado_id
                else None
            ),
            categoria_id=(
                payload.categoria_id
                if payload.categoria_id is not None
                else str(solicitacao.categoria_id)
                if solicitacao.categoria_id
                else None
            ),
            descricao_problema=payload.descricao_problema or solicitacao.descricao,
            endereco=payload.endereco or solicitacao.endereco,
            urgencia=payload.urgencia or solicitacao.urgencia,
            melhor_horario=payload.melhor_horario if payload.melhor_horario is not None else solicitacao.melhor_horario,
            observacoes=payload.observacoes if payload.observacoes is not None else solicitacao.observacoes,
            valor_mao_obra=(
                payload.valor_mao_obra
                if payload.valor_mao_obra is not None
                else float(solicitacao.preco_mao_obra_snapshot)
                if solicitacao.preco_mao_obra_snapshot is not None
                else None
            ),
            tempo_estimado=payload.tempo_estimado or solicitacao.tempo_estimado_snapshot_minutos,
            tipo_material=payload.tipo_material or solicitacao.material.escolha_cliente,
        )
        categoria_id, servico, valor_mao_obra, tempo_estimado = _resolver_tipo_servico(db, merged)
        _set_if_changed(solicitacao, "servico_tabelado_id", servico.id if servico else None, changes)
        _set_if_changed(solicitacao, "categoria_id", categoria_id, changes)
        _set_if_changed(solicitacao, "titulo", servico.nome if servico else "Servico personalizado", changes)
        _set_if_changed(solicitacao, "preco_mao_obra_snapshot", valor_mao_obra, changes)
        _set_if_changed(solicitacao, "tempo_estimado_snapshot_minutos", tempo_estimado, changes)

    field_map = {
        "descricao_problema": "descricao",
        "endereco": "endereco",
        "urgencia": "urgencia",
        "melhor_horario": "melhor_horario",
        "observacoes": "observacoes",
    }
    for schema_field, model_field in field_map.items():
        value = getattr(payload, schema_field)
        if value is not None:
            _set_if_changed(solicitacao, model_field, value, changes)

    if solicitacao.tipo_servico == "personalizado":
        if payload.valor_mao_obra is not None:
            _set_if_changed(
                solicitacao,
                "preco_mao_obra_snapshot",
                payload.valor_mao_obra,
                changes,
            )
        if payload.tempo_estimado is not None:
            _set_if_changed(
                solicitacao,
                "tempo_estimado_snapshot_minutos",
                payload.tempo_estimado,
                changes,
            )

    if payload.tipo_material is not None:
        _set_if_changed(solicitacao.material, "escolha_cliente", payload.tipo_material, changes)

    _registrar_historico_edicoes(db, solicitacao.id, usuario.id, changes)
    db.commit()
    return _buscar_solicitacao_por_id(db, solicitacao.id)


def cancelar_solicitacao(db: Session, solicitacao_id: str, usuario: Usuario) -> SolicitacaoServico:
    solicitacao = buscar_solicitacao(db, solicitacao_id, usuario)
    if solicitacao.status_codigo in {"concluido", "cancelado"}:
        raise BadRequestError("Solicitacao ja esta finalizada.")

    status_anterior = solicitacao.status_codigo
    solicitacao.status_codigo = STATUS_CANCELADO
    solicitacao.cancelado_em = datetime.now(timezone.utc)
    solicitacao.updated_by_usuario_id = usuario.id
    db.add(
        HistoricoStatus(
            solicitacao_id=solicitacao.id,
            status_anterior=status_anterior,
            status_novo=STATUS_CANCELADO,
            alterado_por_usuario_id=usuario.id,
            observacao="Solicitacao cancelada.",
        )
    )
    db.commit()
    return _buscar_solicitacao_por_id(db, solicitacao.id)


def _validar_cliente_da_solicitacao(db: Session, cliente_id: str, usuario: Usuario) -> Cliente:
    parsed_id = _parse_uuid(cliente_id, "Cliente invalido.")
    cliente = db.get(Cliente, parsed_id)
    if cliente is None:
        raise BadRequestError("Cliente nao encontrado.")
    if usuario.tipo_usuario != "admin" and (usuario.cliente is None or usuario.cliente.id != cliente.id):
        raise UnauthorizedError("Cliente nao autorizado para esta solicitacao.")
    return cliente


def _resolver_tipo_servico(
    db: Session,
    payload: SolicitacaoServicoCreateRequest,
) -> tuple[UUID, ServicoTabelado | None, float | None, int | None]:
    if payload.tipo_servico == "tabelado":
        if not payload.servico_tabelado_id:
            raise BadRequestError("Servico tabelado e obrigatorio para solicitacao tabelada.")
        servico = db.get(
            ServicoTabelado,
            _parse_uuid(payload.servico_tabelado_id, "Servico tabelado invalido."),
        )
        if servico is None or not servico.ativo:
            raise BadRequestError("Servico tabelado nao encontrado ou inativo.")
        return (
            servico.categoria_id,
            servico,
            float(servico.preco_mao_obra),
            servico.tempo_estimado_minutos,
        )

    if not payload.categoria_id:
        raise BadRequestError("Categoria e obrigatoria para solicitacao personalizada.")

    categoria_id = _parse_uuid(payload.categoria_id, "Categoria invalida.")
    categoria = db.get(CategoriaServico, categoria_id)
    if categoria is None or not categoria.ativo:
        raise BadRequestError("Categoria nao encontrada ou inativa.")

    return categoria_id, None, payload.valor_mao_obra, payload.tempo_estimado


def _buscar_solicitacao_por_id(db: Session, solicitacao_id: UUID) -> SolicitacaoServico:
    solicitacao = db.scalar(
        select(SolicitacaoServico)
        .where(SolicitacaoServico.id == solicitacao_id, SolicitacaoServico.deleted_at.is_(None))
        .options(selectinload(SolicitacaoServico.material), selectinload(SolicitacaoServico.garantia))
    )
    if solicitacao is None:
        raise BadRequestError("Solicitacao nao encontrada.")
    return solicitacao


def _buscar_solicitacao_para_execucao(db: Session, solicitacao_id: str) -> SolicitacaoServico:
    parsed_id = _parse_uuid(solicitacao_id, "Solicitacao invalida.")
    solicitacao = db.scalar(
        select(SolicitacaoServico)
        .where(SolicitacaoServico.id == parsed_id, SolicitacaoServico.deleted_at.is_(None))
        .options(
            selectinload(SolicitacaoServico.material),
            selectinload(SolicitacaoServico.garantia),
            selectinload(SolicitacaoServico.servico_tabelado),
        )
        .with_for_update()
    )
    if solicitacao is None:
        raise BadRequestError("Solicitacao nao encontrada.")
    return solicitacao


def _garantir_acesso_solicitacao(solicitacao: SolicitacaoServico, usuario: Usuario) -> None:
    if usuario.tipo_usuario == "admin":
        return
    if usuario.tipo_usuario == "cliente" and usuario.cliente and solicitacao.cliente_id == usuario.cliente.id:
        return
    if (
        usuario.tipo_usuario == "prestador"
        and usuario.prestador
        and solicitacao.prestador_id == usuario.prestador.id
    ):
        return
    raise UnauthorizedError("Acesso nao permitido para esta solicitacao.")


def _garantir_prestador_aceito(solicitacao: SolicitacaoServico, usuario: Usuario) -> None:
    if usuario.tipo_usuario != "prestador" or usuario.prestador is None:
        raise UnauthorizedError("Apenas o prestador aceito pode executar este servico.")
    if solicitacao.prestador_id != usuario.prestador.id:
        raise UnauthorizedError("Prestador nao aceitou esta solicitacao.")


def _garantir_prestador_aprovado(usuario: Usuario) -> None:
    validacao = usuario.prestador.validacao if usuario.prestador else None
    if not usuario.prestador.ativo or validacao is None or validacao.status_validacao != "aprovado":
        raise UnauthorizedError("Prestador aguardando aprovacao do admin para aceitar servicos.")


def _garantir_cliente_dono(solicitacao: SolicitacaoServico, usuario: Usuario) -> None:
    if usuario.tipo_usuario != "cliente" or usuario.cliente is None:
        raise UnauthorizedError("Apenas o cliente dono pode confirmar este servico.")
    if solicitacao.cliente_id != usuario.cliente.id:
        raise UnauthorizedError("Cliente nao pertence a esta solicitacao.")


def _material_aguarda_aprovacao(solicitacao: SolicitacaoServico) -> bool:
    material = solicitacao.material
    if material is None or material.deleted_at is not None:
        return False
    return material.status_material == "aguardando_aprovacao_cliente" or (
        material.valor_estimado is not None
        and material.necessita_aprovacao_cliente
        and material.status_material not in {"aprovado", "comprado_retirado"}
    )


def _alterar_status_com_historico(
    db: Session,
    solicitacao: SolicitacaoServico,
    novo_status: str,
    usuario: Usuario,
    observacao: str,
) -> None:
    status_anterior = solicitacao.status_codigo
    if status_anterior == novo_status:
        return
    solicitacao.status_codigo = novo_status
    solicitacao.updated_by_usuario_id = usuario.id
    db.add(
        HistoricoStatus(
            solicitacao_id=solicitacao.id,
            status_anterior=status_anterior,
            status_novo=novo_status,
            alterado_por_usuario_id=usuario.id,
            observacao=observacao,
        )
    )


def _garantir_editavel_antes_aceite(solicitacao: SolicitacaoServico) -> None:
    if solicitacao.prestador_id is not None or solicitacao.status_codigo in STATUS_BLOQUEIA_EDICAO:
        raise BadRequestError("Solicitacao nao pode ser editada depois do aceite.")


def _set_if_changed(target, field: str, new_value, changes: list[tuple[str, object, object]]) -> None:
    old_value = getattr(target, field)
    if old_value != new_value:
        setattr(target, field, new_value)
        changes.append((field, old_value, new_value))


def _registrar_historico_edicoes(
    db: Session,
    solicitacao_id: UUID,
    usuario_id: UUID,
    changes: list[tuple[str, object, object]],
) -> None:
    for field, old_value, new_value in changes:
        db.add(
            HistoricoEdicao(
                entidade="solicitacoes_servico",
                entidade_id=solicitacao_id,
                campo=field,
                valor_anterior=str(old_value) if old_value is not None else None,
                valor_novo=str(new_value) if new_value is not None else None,
                alterado_por_usuario_id=usuario_id,
                origem="backend",
            )
        )


def _parse_uuid(value: str, message: str) -> UUID:
    try:
        return UUID(value)
    except (TypeError, ValueError) as exc:
        raise BadRequestError(message) from exc


def _marcar_data_por_status(solicitacao: SolicitacaoServico, status: str) -> None:
    now = datetime.now(timezone.utc)
    if status == "em_andamento" and solicitacao.iniciado_em is None:
        solicitacao.iniciado_em = now
    elif status == "concluido" and solicitacao.concluido_em is None:
        solicitacao.concluido_em = now
    elif status == "cancelado" and solicitacao.cancelado_em is None:
        solicitacao.cancelado_em = now
