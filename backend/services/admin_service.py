from datetime import datetime, time
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.pagination import PageParams
from app.services.ai_error_interpreter import build_error_context, interpret_error
from models import (
    Avaliacao,
    CategoriaServico,
    GarantiaServico,
    Cliente,
    MaterialServico,
    Notificacao,
    MonitoramentoSistema,
    PagamentoSimulado,
    Prestador,
    PrestadorValidacao,
    Repasse,
    ServicoTabelado,
    SolicitacaoServico,
    Usuario,
)
from utils.exceptions import BadRequestError


def dashboard_admin(db: Session, admin: Usuario) -> dict:
    total_mao_obra = _scalar_float(
        db,
        select(func.coalesce(func.sum(SolicitacaoServico.preco_mao_obra_snapshot), 0)).where(
            SolicitacaoServico.deleted_at.is_(None)
        ),
    )
    total_materiais = _scalar_float(
        db,
        select(func.coalesce(func.sum(MaterialServico.valor_estimado), 0)).where(
            MaterialServico.deleted_at.is_(None),
            MaterialServico.status_material.in_(("aprovado", "comprado_retirado")),
        ),
    )
    ultimos_servicos = list(
        db.scalars(
            select(SolicitacaoServico)
            .where(SolicitacaoServico.deleted_at.is_(None))
            .order_by(SolicitacaoServico.created_at.desc())
            .limit(5)
        )
    )
    ultimos_usuarios = list(
        db.scalars(
            select(Usuario)
            .where(Usuario.deleted_at.is_(None))
            .order_by(Usuario.created_at.desc())
            .limit(5)
        )
    )
    return {
        "total_clientes": _count(db, Cliente),
        "total_prestadores": _count(db, Prestador),
        "total_solicitacoes": _count(db, SolicitacaoServico),
        "solicitacoes_aguardando_prestador": _count_solicitacoes_status(db, "aguardando_prestador"),
        "solicitacoes_aceitas": _count_solicitacoes_status(db, "aceito"),
        "solicitacoes_em_andamento": _count_solicitacoes_status(db, "em_andamento"),
        "solicitacoes_concluidas": _count_solicitacoes_status(db, "concluido"),
        "solicitacoes_em_analise": _count_solicitacoes_status(db, "em_analise"),
        "total_servicos_tabelados_ativos": db.scalar(
            select(func.count()).select_from(ServicoTabelado).where(
                ServicoTabelado.ativo.is_(True),
                ServicoTabelado.deleted_at.is_(None),
            )
        ) or 0,
        "total_avaliacoes": _count(db, Avaliacao),
        "media_geral_avaliacoes": _scalar_float(
            db,
            select(func.coalesce(func.avg(Avaliacao.nota), 0)).where(Avaliacao.deleted_at.is_(None)),
        ),
        "total_materiais_aprovados": db.scalar(
            select(func.count()).select_from(MaterialServico).where(
                MaterialServico.status_material.in_(("aprovado", "comprado_retirado")),
                MaterialServico.deleted_at.is_(None),
            )
        ) or 0,
        "valor_total_mao_obra": total_mao_obra,
        "valor_total_materiais": total_materiais,
        "valor_total_estimado": round(total_mao_obra + total_materiais, 2),
        "garantias_ativas": _count_garantias_status(db, "ativa"),
        "garantias_acionadas": _count_garantias_status(db, "acionada"),
        "garantias_em_analise": _count_garantias_status(db, "em_analise"),
        "valor_retido_garantia": _scalar_float(
            db,
            select(func.coalesce(func.sum(GarantiaServico.valor_retido), 0)).where(
                GarantiaServico.deleted_at.is_(None),
                GarantiaServico.bloqueio_repasse.is_(True),
            ),
        ),
        "notificacoes_nao_lidas_admin": db.scalar(
            select(func.count()).select_from(Notificacao).where(
                Notificacao.usuario_id == admin.id,
                Notificacao.lida.is_(False),
                Notificacao.deleted_at.is_(None),
            )
        ) or 0,
        "ultimos_servicos_criados": [_solicitacao_dict(item) for item in ultimos_servicos],
        "ultimos_usuarios_cadastrados": [_usuario_dict(item) for item in ultimos_usuarios],
    }


def metricas_admin(db: Session, admin: Usuario) -> dict:
    dashboard = dashboard_admin(db, admin)
    total_canceladas = _count_solicitacoes_status(db, "cancelado")
    total_problemas = _count_solicitacoes_status(db, "em_analise")
    total_solicitacoes = dashboard["total_solicitacoes"]
    return {
        **dashboard,
        "total_canceladas": total_canceladas,
        "taxa_cancelamento": _percentual(total_canceladas, total_solicitacoes),
        "taxa_problemas": _percentual(total_problemas, total_solicitacoes),
        "media_avaliacoes_prestadores": _scalar_float(
            db,
            select(func.coalesce(func.avg(Prestador.media_notas), 0)).where(
                Prestador.deleted_at.is_(None),
                Prestador.total_avaliacoes > 0,
            ),
        ),
    }


def listar_prestadores_pendentes_admin(db: Session, pagination: PageParams) -> dict:
    filters = [
        Prestador.deleted_at.is_(None),
        PrestadorValidacao.deleted_at.is_(None),
        PrestadorValidacao.status_validacao.in_(("pendente", "em_analise")),
    ]
    total = db.scalar(
        select(func.count())
        .select_from(Prestador)
        .join(PrestadorValidacao, PrestadorValidacao.prestador_id == Prestador.id)
        .where(*filters)
    ) or 0
    items = list(
        db.scalars(
            select(Prestador)
            .join(PrestadorValidacao, PrestadorValidacao.prestador_id == Prestador.id)
            .where(*filters)
            .options(selectinload(Prestador.usuario), selectinload(Prestador.validacao))
            .order_by(Prestador.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return {
        "items": [_prestador_validacao_dict(item) for item in items],
        "meta": _meta(total, pagination),
    }


def aprovar_prestador_admin(db: Session, prestador_id: str, admin: Usuario) -> dict:
    prestador = _buscar_prestador_validacao(db, prestador_id)
    before = prestador.validacao.status_validacao
    prestador.validacao.status_validacao = "aprovado"
    prestador.validacao.data_aprovacao = datetime.now()
    prestador.validacao.aprovado_por_admin_id = admin.id
    prestador.validacao.observacao_admin = None
    prestador.validacao.updated_by_usuario_id = admin.id
    prestador.ativo = True
    prestador.updated_by_usuario_id = admin.id
    _historico_admin(db, "prestador_validacao", prestador.validacao.id, "status_validacao", before, "aprovado", admin.id)
    db.commit()
    return _prestador_validacao_dict(prestador)


def rejeitar_prestador_admin(db: Session, prestador_id: str, observacao: str, admin: Usuario) -> dict:
    prestador = _buscar_prestador_validacao(db, prestador_id)
    before = prestador.validacao.status_validacao
    prestador.validacao.status_validacao = "rejeitado"
    prestador.validacao.observacao_admin = observacao.strip()
    prestador.validacao.updated_by_usuario_id = admin.id
    prestador.ativo = False
    prestador.updated_by_usuario_id = admin.id
    _historico_admin(db, "prestador_validacao", prestador.validacao.id, "status_validacao", before, "rejeitado", admin.id)
    db.commit()
    return _prestador_validacao_dict(prestador)


def documentos_prestador_admin(db: Session, prestador_id: str) -> dict:
    return _prestador_validacao_dict(_buscar_prestador_validacao(db, prestador_id))


def monitoramento_admin(db: Session) -> dict:
    ativos = list(
        db.scalars(
            select(MonitoramentoSistema)
            .where(MonitoramentoSistema.status == "ativo")
            .order_by(MonitoramentoSistema.created_at.desc())
            .limit(50)
        )
    )
    por_nivel = dict(
        db.execute(
            select(MonitoramentoSistema.nivel_alerta, func.count(MonitoramentoSistema.id))
            .where(MonitoramentoSistema.status == "ativo")
            .group_by(MonitoramentoSistema.nivel_alerta)
        ).all()
    )
    rotas_lentas = [
        item
        for item in ativos
        if item.tipo_alerta in {"rota_lenta", "api_lenta"}
    ][:10]
    erros = [
        item
        for item in ativos
        if "erro" in item.tipo_alerta or "falha" in item.tipo_alerta
    ][:10]
    alerta_para_analise = erros[0] if erros else ativos[0] if ativos else None
    return {
        "saude": "critica" if por_nivel.get("critico") else "atencao" if por_nivel.get("alerta") else "ok",
        "alertas_ativos": [_monitoramento_dict(item) for item in ativos],
        "por_nivel": por_nivel,
        "rotas_mais_lentas": [_monitoramento_dict(item) for item in rotas_lentas],
        "erros_mais_frequentes": [_monitoramento_dict(item) for item in erros],
        "analise_portugues_simples": _analise_monitoramento(alerta_para_analise),
        "possiveis_problemas_futuros": [
            "Acompanhar aumento de erros repetidos.",
            "Verificar rotas lentas antes de afetar usuarios.",
            "Monitorar falhas de pagamento e upload.",
        ],
    }


def relatorio_financeiro_admin(db: Session, filters: dict) -> dict:
    conditions = [PagamentoSimulado.deleted_at.is_(None)]
    if filters.get("status"):
        conditions.append(PagamentoSimulado.status_pagamento == filters["status"])
    _aplicar_periodo(conditions, PagamentoSimulado.created_at, filters)

    row = db.execute(
        select(
            func.count(PagamentoSimulado.id),
            func.coalesce(func.sum(PagamentoSimulado.valor_mao_obra), 0),
            func.coalesce(func.sum(PagamentoSimulado.valor_material), 0),
            func.coalesce(func.sum(PagamentoSimulado.valor_comissao), 0),
            func.coalesce(func.sum(PagamentoSimulado.valor_prestador), 0),
            func.coalesce(func.sum(PagamentoSimulado.valor_empresa), 0),
        ).where(*conditions)
    ).one()
    total_pagamentos = int(row[0])
    total_mao_obra = round(float(row[1]), 2)
    total_material = round(float(row[2]), 2)
    total_comissao = round(float(row[3]), 2)
    total_prestador = round(float(row[4]), 2)
    total_empresa = round(float(row[5]), 2)
    total_estimado = round(total_mao_obra + total_material, 2)

    return {
        "total_pagamentos": total_pagamentos,
        "valor_total_mao_obra": total_mao_obra,
        "valor_total_materiais": total_material,
        "valor_total_comissao_plataforma": total_comissao,
        "valor_total_prestadores": total_prestador,
        "valor_total_empresas": total_empresa,
        "valor_total_estimado": total_estimado,
        "ticket_medio": round(total_estimado / total_pagamentos, 2) if total_pagamentos else 0,
        "por_status_pagamento": _agrupar_pagamentos_por_status(db, filters),
        "repasses_pendentes": _resumo_repasses(db, "pendente", filters),
        "garantias": _resumo_garantias(db, filters),
        "repasses_por_tipo": _agrupar_repasses_por_tipo(db, filters),
    }


def relatorio_repasses_admin(db: Session, pagination: PageParams, filters: dict) -> tuple[list[dict], int]:
    conditions = [Repasse.deleted_at.is_(None)]
    if filters.get("status"):
        conditions.append(Repasse.status_repasse == filters["status"])
    if filters.get("tipo_repasse"):
        conditions.append(Repasse.tipo_repasse == filters["tipo_repasse"])
    _aplicar_periodo(conditions, Repasse.created_at, filters)
    total = db.scalar(select(func.count()).select_from(Repasse).where(*conditions)) or 0
    items = list(
        db.scalars(
            select(Repasse)
            .where(*conditions)
            .order_by(Repasse.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return [_repasse_dict(item) for item in items], total


def ranking_prestadores_admin(db: Session, pagination: PageParams, filters: dict) -> tuple[list[dict], int]:
    conditions = [Prestador.deleted_at.is_(None)]
    if filters.get("ativo") is not None:
        conditions.append(Prestador.ativo.is_(filters["ativo"]))
    if filters.get("prestador_id"):
        conditions.append(Prestador.id == _parse_uuid(filters["prestador_id"], "Prestador invalido."))

    total = db.scalar(select(func.count()).select_from(Prestador).where(*conditions)) or 0
    prestadores = list(
        db.scalars(
            select(Prestador)
            .where(*conditions)
            .options(selectinload(Prestador.usuario))
            .order_by(
                Prestador.media_notas.desc(),
                Prestador.total_servicos_concluidos.desc(),
                Prestador.total_avaliacoes.desc(),
            )
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )

    return [_ranking_prestador_dict(db, prestador, filters) for prestador in prestadores], total


def servicos_mais_pedidos_admin(db: Session, pagination: PageParams, filters: dict) -> tuple[list[dict], int]:
    conditions = [SolicitacaoServico.deleted_at.is_(None)]
    if filters.get("status"):
        conditions.append(SolicitacaoServico.status_codigo == filters["status"])
    if filters.get("categoria"):
        categoria = filters["categoria"]
        try:
            conditions.append(SolicitacaoServico.categoria_id == UUID(categoria))
        except ValueError:
            conditions.append(CategoriaServico.nome.ilike(f"%{categoria}%"))
    _aplicar_periodo(conditions, SolicitacaoServico.created_at, filters)

    nome_expr = func.coalesce(ServicoTabelado.nome, SolicitacaoServico.titulo, "Servico personalizado")
    categoria_expr = func.coalesce(CategoriaServico.nome, "Sem categoria")
    query = (
        select(
            nome_expr.label("nome"),
            categoria_expr.label("categoria"),
            func.count(SolicitacaoServico.id).label("total_solicitacoes"),
            func.coalesce(func.sum(SolicitacaoServico.preco_mao_obra_snapshot), 0).label("valor_mao_obra"),
        )
        .select_from(SolicitacaoServico)
        .outerjoin(ServicoTabelado, ServicoTabelado.id == SolicitacaoServico.servico_tabelado_id)
        .outerjoin(CategoriaServico, CategoriaServico.id == SolicitacaoServico.categoria_id)
        .where(*conditions)
        .group_by(nome_expr, categoria_expr)
    )
    rows_total = list(db.execute(query))
    rows = db.execute(
        query.order_by(func.count(SolicitacaoServico.id).desc())
        .offset(pagination.offset)
        .limit(pagination.per_page)
    ).all()
    items = [
        {
            "nome": row.nome,
            "categoria": row.categoria,
            "total_solicitacoes": int(row.total_solicitacoes),
            "valor_mao_obra": round(float(row.valor_mao_obra), 2),
        }
        for row in rows
    ]
    return items, len(rows_total)


def listar_usuarios_admin(db: Session, pagination: PageParams, filters: dict) -> tuple[list[dict], int]:
    conditions = [Usuario.deleted_at.is_(None)]
    if filters.get("tipo_usuario"):
        conditions.append(Usuario.tipo_usuario == filters["tipo_usuario"])
    if filters.get("ativo") is not None:
        conditions.append(Usuario.ativo.is_(filters["ativo"]))
    _aplicar_periodo(conditions, Usuario.created_at, filters)
    total = db.scalar(select(func.count()).select_from(Usuario).where(*conditions)) or 0
    items = list(
        db.scalars(
            select(Usuario)
            .where(*conditions)
            .order_by(Usuario.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return [_usuario_dict(item) for item in items], total


def listar_clientes_admin(db: Session, pagination: PageParams, filters: dict) -> tuple[list[dict], int]:
    conditions = [Cliente.deleted_at.is_(None)]
    if filters.get("cliente_id"):
        conditions.append(Cliente.id == _parse_uuid(filters["cliente_id"], "Cliente invalido."))
    _aplicar_periodo(conditions, Cliente.created_at, filters)
    total = db.scalar(select(func.count()).select_from(Cliente).where(*conditions)) or 0
    items = list(
        db.scalars(
            select(Cliente)
            .where(*conditions)
            .options(selectinload(Cliente.usuario))
            .order_by(Cliente.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return [_cliente_dict(item) for item in items], total


def listar_prestadores_admin(db: Session, pagination: PageParams, filters: dict) -> tuple[list[dict], int]:
    conditions = [Prestador.deleted_at.is_(None)]
    query = select(Prestador)
    count_query = select(func.count()).select_from(Prestador)
    if filters.get("prestador_id"):
        conditions.append(Prestador.id == _parse_uuid(filters["prestador_id"], "Prestador invalido."))
    if filters.get("ativo") is not None:
        conditions.append(Prestador.ativo.is_(filters["ativo"]))
    if filters.get("status_validacao"):
        query = query.join(PrestadorValidacao, PrestadorValidacao.prestador_id == Prestador.id)
        count_query = count_query.join(PrestadorValidacao, PrestadorValidacao.prestador_id == Prestador.id)
        conditions.append(PrestadorValidacao.status_validacao == filters["status_validacao"])
    _aplicar_periodo(conditions, Prestador.created_at, filters)
    total = db.scalar(count_query.where(*conditions)) or 0
    items = list(
        db.scalars(
            query.where(*conditions)
            .options(selectinload(Prestador.usuario), selectinload(Prestador.validacao))
            .order_by(Prestador.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return [_prestador_dict(item) for item in items], total


def listar_solicitacoes_admin(db: Session, pagination: PageParams, filters: dict) -> tuple[list[dict], int]:
    query = select(SolicitacaoServico)
    count_query = select(func.count()).select_from(SolicitacaoServico)
    conditions = [SolicitacaoServico.deleted_at.is_(None)]
    if filters.get("status"):
        conditions.append(SolicitacaoServico.status_codigo == filters["status"])
    if filters.get("cliente_id"):
        conditions.append(SolicitacaoServico.cliente_id == _parse_uuid(filters["cliente_id"], "Cliente invalido."))
    if filters.get("prestador_id"):
        conditions.append(
            SolicitacaoServico.prestador_id == _parse_uuid(filters["prestador_id"], "Prestador invalido.")
        )
    if filters.get("categoria"):
        categoria = filters["categoria"]
        try:
            conditions.append(SolicitacaoServico.categoria_id == UUID(categoria))
        except ValueError:
            query = query.join(CategoriaServico, CategoriaServico.id == SolicitacaoServico.categoria_id)
            count_query = count_query.join(CategoriaServico, CategoriaServico.id == SolicitacaoServico.categoria_id)
            conditions.append(CategoriaServico.nome.ilike(f"%{categoria}%"))
    _aplicar_periodo(conditions, SolicitacaoServico.created_at, filters)
    total = db.scalar(count_query.where(*conditions)) or 0
    items = list(
        db.scalars(
            query.where(*conditions)
            .options(selectinload(SolicitacaoServico.material), selectinload(SolicitacaoServico.garantia))
            .order_by(SolicitacaoServico.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return [_solicitacao_dict(item) for item in items], total


def listar_materiais_admin(db: Session, pagination: PageParams, filters: dict) -> tuple[list[dict], int]:
    conditions = [MaterialServico.deleted_at.is_(None)]
    if filters.get("status"):
        conditions.append(MaterialServico.status_material == filters["status"])
    if filters.get("prestador_id"):
        conditions.append(MaterialServico.prestador_id == _parse_uuid(filters["prestador_id"], "Prestador invalido."))
    _aplicar_periodo(conditions, MaterialServico.created_at, filters)
    total = db.scalar(select(func.count()).select_from(MaterialServico).where(*conditions)) or 0
    items = list(
        db.scalars(
            select(MaterialServico)
            .where(*conditions)
            .order_by(MaterialServico.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return [_material_dict(item) for item in items], total


def listar_avaliacoes_admin(db: Session, pagination: PageParams, filters: dict) -> tuple[list[dict], int]:
    conditions = [Avaliacao.deleted_at.is_(None)]
    _aplicar_periodo(conditions, Avaliacao.created_at, filters)
    total = db.scalar(select(func.count()).select_from(Avaliacao).where(*conditions)) or 0
    items = list(
        db.scalars(
            select(Avaliacao)
            .where(*conditions)
            .order_by(Avaliacao.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return [_avaliacao_dict(item) for item in items], total


def listar_notificacoes_admin(db: Session, pagination: PageParams, filters: dict) -> tuple[list[dict], int]:
    conditions = [Notificacao.deleted_at.is_(None)]
    if filters.get("status") == "nao_lidas":
        conditions.append(Notificacao.lida.is_(False))
    if filters.get("tipo_usuario"):
        conditions.append(Notificacao.usuario.has(Usuario.tipo_usuario == filters["tipo_usuario"]))
    _aplicar_periodo(conditions, Notificacao.created_at, filters)
    total = db.scalar(select(func.count()).select_from(Notificacao).where(*conditions)) or 0
    items = list(
        db.scalars(
            select(Notificacao)
            .where(*conditions)
            .order_by(Notificacao.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return [_notificacao_dict(item) for item in items], total


def _count(db: Session, model) -> int:
    return db.scalar(select(func.count()).select_from(model).where(model.deleted_at.is_(None))) or 0


def _count_solicitacoes_status(db: Session, status: str) -> int:
    return db.scalar(
        select(func.count()).select_from(SolicitacaoServico).where(
            SolicitacaoServico.status_codigo == status,
            SolicitacaoServico.deleted_at.is_(None),
        )
    ) or 0


def _count_garantias_status(db: Session, status: str) -> int:
    return db.scalar(
        select(func.count()).select_from(GarantiaServico).where(
            GarantiaServico.status_garantia == status,
            GarantiaServico.deleted_at.is_(None),
        )
    ) or 0


def _scalar_float(db: Session, query) -> float:
    return round(float(db.scalar(query) or 0), 2)


def _percentual(parte: int, total: int) -> float:
    return round((parte / total) * 100, 2) if total else 0


def _agrupar_pagamentos_por_status(db: Session, filters: dict) -> list[dict]:
    conditions = [PagamentoSimulado.deleted_at.is_(None)]
    if filters.get("status"):
        conditions.append(PagamentoSimulado.status_pagamento == filters["status"])
    _aplicar_periodo(conditions, PagamentoSimulado.created_at, filters)
    rows = db.execute(
        select(
            PagamentoSimulado.status_pagamento,
            func.count(PagamentoSimulado.id),
            func.coalesce(func.sum(PagamentoSimulado.valor_mao_obra + PagamentoSimulado.valor_material), 0),
        )
        .where(*conditions)
        .group_by(PagamentoSimulado.status_pagamento)
    ).all()
    return [
        {"status": row[0], "total": int(row[1]), "valor_total": round(float(row[2]), 2)}
        for row in rows
    ]


def _resumo_repasses(db: Session, status: str, filters: dict) -> dict:
    conditions = [Repasse.deleted_at.is_(None), Repasse.status_repasse == status]
    _aplicar_periodo(conditions, Repasse.created_at, filters)
    row = db.execute(
        select(func.count(Repasse.id), func.coalesce(func.sum(Repasse.valor), 0)).where(*conditions)
    ).one()
    return {"total": int(row[0]), "valor_total": round(float(row[1]), 2)}


def _resumo_garantias(db: Session, filters: dict) -> dict:
    conditions = [GarantiaServico.deleted_at.is_(None)]
    _aplicar_periodo(conditions, GarantiaServico.created_at, filters)
    row = db.execute(
        select(
            func.count(GarantiaServico.id),
            func.coalesce(func.sum(GarantiaServico.valor_retido), 0),
        ).where(*conditions)
    ).one()
    acionadas = db.scalar(
        select(func.count()).select_from(GarantiaServico).where(
            *conditions,
            GarantiaServico.status_garantia.in_(("acionada", "em_analise")),
        )
    ) or 0
    return {
        "total": int(row[0]),
        "valor_retido_total": round(float(row[1]), 2),
        "acionadas_em_analise": int(acionadas),
    }


def _agrupar_repasses_por_tipo(db: Session, filters: dict) -> list[dict]:
    conditions = [Repasse.deleted_at.is_(None)]
    _aplicar_periodo(conditions, Repasse.created_at, filters)
    rows = db.execute(
        select(Repasse.tipo_repasse, func.count(Repasse.id), func.coalesce(func.sum(Repasse.valor), 0))
        .where(*conditions)
        .group_by(Repasse.tipo_repasse)
    ).all()
    return [
        {"tipo_repasse": row[0], "total": int(row[1]), "valor_total": round(float(row[2]), 2)}
        for row in rows
    ]


def _aplicar_periodo(conditions: list, column, filters: dict) -> None:
    if filters.get("data_inicio"):
        conditions.append(column >= _parse_date(filters["data_inicio"], end=False))
    if filters.get("data_fim"):
        conditions.append(column <= _parse_date(filters["data_fim"], end=True))


def _parse_date(value: str, end: bool) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise BadRequestError("Data invalida. Use YYYY-MM-DD.") from exc
    if len(value) == 10:
        parsed = datetime.combine(parsed.date(), time.max if end else time.min)
    return parsed


def _parse_uuid(value: str, message: str) -> UUID:
    try:
        return UUID(value)
    except (TypeError, ValueError) as exc:
        raise BadRequestError(message) from exc


def _meta(total: int, pagination: PageParams) -> dict:
    total_pages = (total + pagination.per_page - 1) // pagination.per_page if total else 0
    return {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": total,
        "total_pages": total_pages,
    }


def _buscar_prestador_validacao(db: Session, prestador_id: str) -> Prestador:
    prestador = db.scalar(
        select(Prestador)
        .where(Prestador.id == _parse_uuid(prestador_id, "Prestador invalido."), Prestador.deleted_at.is_(None))
        .options(selectinload(Prestador.usuario), selectinload(Prestador.validacao))
    )
    if prestador is None or prestador.validacao is None:
        raise BadRequestError("Prestador ou validacao nao encontrada.")
    return prestador


def _historico_admin(
    db: Session,
    entidade: str,
    entidade_id: UUID,
    campo: str,
    anterior,
    novo,
    admin_id: UUID,
) -> None:
    from models import HistoricoEdicao

    db.add(
        HistoricoEdicao(
            entidade=entidade,
            entidade_id=entidade_id,
            campo=campo,
            valor_anterior=str(anterior) if anterior is not None else None,
            valor_novo=str(novo) if novo is not None else None,
            alterado_por_usuario_id=admin_id,
            origem="admin",
        )
    )


def _usuario_dict(usuario: Usuario) -> dict:
    return {
        "id": str(usuario.id),
        "nome": usuario.nome,
        "email": usuario.email,
        "telefone": usuario.telefone,
        "tipo_usuario": usuario.tipo_usuario,
        "ativo": usuario.ativo,
        "created_at": usuario.created_at.isoformat(),
    }


def _cliente_dict(cliente: Cliente) -> dict:
    return {
        "id": str(cliente.id),
        "usuario_id": str(cliente.usuario_id),
        "nome": cliente.usuario.nome if cliente.usuario else None,
        "email": cliente.usuario.email if cliente.usuario else None,
        "telefone": cliente.usuario.telefone if cliente.usuario else None,
        "documento": cliente.documento,
        "endereco": cliente.endereco_principal,
        "bairro": cliente.bairro,
        "cidade": cliente.cidade,
        "estado": cliente.estado,
        "media_notas": float(cliente.media_notas),
        "total_avaliacoes": cliente.total_avaliacoes,
        "total_servicos_solicitados": cliente.total_servicos_solicitados,
        "created_at": cliente.created_at.isoformat(),
    }


def _prestador_dict(prestador: Prestador) -> dict:
    return {
        "id": str(prestador.id),
        "usuario_id": str(prestador.usuario_id),
        "nome": prestador.usuario.nome if prestador.usuario else None,
        "email": prestador.usuario.email if prestador.usuario else None,
        "telefone": prestador.usuario.telefone if prestador.usuario else None,
        "documento": prestador.documento,
        "endereco": prestador.endereco_principal,
        "bairro": prestador.bairro,
        "cidade": prestador.cidade,
        "estado": prestador.estado,
        "ativo": prestador.ativo,
        "status_validacao": prestador.validacao.status_validacao if prestador.validacao else None,
        "media_notas": float(prestador.media_notas),
        "total_avaliacoes": prestador.total_avaliacoes,
        "total_servicos_concluidos": prestador.total_servicos_concluidos,
        "created_at": prestador.created_at.isoformat(),
    }


def _prestador_validacao_dict(prestador: Prestador) -> dict:
    validacao = prestador.validacao
    return {
        **_prestador_dict(prestador),
        "status_validacao": validacao.status_validacao if validacao else None,
        "documento_rg": validacao.documento_rg if validacao else None,
        "documento_cpf": validacao.documento_cpf if validacao else None,
        "selfie_validacao": validacao.selfie_validacao if validacao else None,
        "comprovante_endereco": validacao.comprovante_endereco if validacao else None,
        "observacao_admin": validacao.observacao_admin if validacao else None,
        "data_aprovacao": validacao.data_aprovacao.isoformat() if validacao and validacao.data_aprovacao else None,
        "aprovado_por_admin_id": (
            str(validacao.aprovado_por_admin_id) if validacao and validacao.aprovado_por_admin_id else None
        ),
    }


def _monitoramento_dict(alerta: MonitoramentoSistema) -> dict:
    return {
        "id": str(alerta.id),
        "tipo_alerta": alerta.tipo_alerta,
        "nivel_alerta": alerta.nivel_alerta,
        "mensagem": alerta.mensagem,
        "origem": alerta.origem,
        "status": alerta.status,
        "created_at": alerta.created_at.isoformat(),
    }


def _analise_monitoramento(alerta: MonitoramentoSistema | None) -> dict:
    if alerta is None:
        return {
            "explicacao_simples": "Nenhum alerta ativo foi encontrado no monitoramento.",
            "provavel_causa": "O sistema nao registrou erro ou falha ativa ate o momento.",
            "gravidade_sugerida": "baixa",
            "acao_recomendada": "Continuar acompanhando os indicadores preventivos.",
            "pode_corrigir_automaticamente": False,
            "observacao": "IA apenas sugeriu, não executou ação",
        }
    return interpret_error(
        build_error_context(
            mensagem_tecnica=alerta.mensagem,
            origem=alerta.origem,
            rota_acao=alerta.origem,
            nivel_original=alerta.nivel_alerta,
            dados_seguros={
                "tipo_alerta": alerta.tipo_alerta,
                "status": alerta.status,
                "created_at": alerta.created_at.isoformat(),
            },
        )
    )


def _solicitacao_dict(solicitacao: SolicitacaoServico) -> dict:
    material_total = (
        float(solicitacao.material.valor_estimado)
        if solicitacao.material is not None and solicitacao.material.valor_estimado is not None
        else 0
    )
    mao_obra = float(solicitacao.preco_mao_obra_snapshot or 0)
    return {
        "id": str(solicitacao.id),
        "cliente_id": str(solicitacao.cliente_id),
        "prestador_id": str(solicitacao.prestador_id) if solicitacao.prestador_id else None,
        "categoria_id": str(solicitacao.categoria_id) if solicitacao.categoria_id else None,
        "status": solicitacao.status_codigo,
        "descricao": solicitacao.descricao,
        "valor_mao_obra": mao_obra,
        "valor_material": material_total,
        "valor_total_estimado": round(mao_obra + material_total, 2),
        "garantia_status": solicitacao.garantia.status_garantia
        if solicitacao.garantia and solicitacao.garantia.deleted_at is None
        else None,
        "garantia_data_fim": solicitacao.garantia.data_fim_garantia.isoformat()
        if solicitacao.garantia and solicitacao.garantia.deleted_at is None
        else None,
        "garantia_valor_retido": float(solicitacao.garantia.valor_retido)
        if solicitacao.garantia and solicitacao.garantia.deleted_at is None
        else 0,
        "created_at": solicitacao.created_at.isoformat(),
    }


def _material_dict(material: MaterialServico) -> dict:
    return {
        "id": str(material.id),
        "solicitacao_id": str(material.solicitacao_id),
        "prestador_id": str(material.prestador_id) if material.prestador_id else None,
        "descricao_material": material.descricao_material,
        "valor_estimado": float(material.valor_estimado) if material.valor_estimado is not None else None,
        "status_material": material.status_material,
        "created_at": material.created_at.isoformat(),
    }


def _avaliacao_dict(avaliacao: Avaliacao) -> dict:
    return {
        "id": str(avaliacao.id),
        "solicitacao_id": str(avaliacao.solicitacao_id),
        "avaliador_usuario_id": str(avaliacao.avaliador_usuario_id),
        "avaliado_usuario_id": str(avaliacao.avaliado_usuario_id),
        "tipo_avaliacao": avaliacao.tipo_avaliacao,
        "nota": avaliacao.nota,
        "comentario": avaliacao.comentario,
        "created_at": avaliacao.created_at.isoformat(),
    }


def _notificacao_dict(notificacao: Notificacao) -> dict:
    return {
        "id": str(notificacao.id),
        "usuario_id": str(notificacao.usuario_id),
        "solicitacao_id": str(notificacao.solicitacao_id) if notificacao.solicitacao_id else None,
        "tipo_notificacao": notificacao.tipo_notificacao,
        "titulo": notificacao.titulo,
        "lida": notificacao.lida,
        "prioridade": notificacao.prioridade,
        "canal": notificacao.canal,
        "created_at": notificacao.created_at.isoformat(),
    }


def _repasse_dict(repasse: Repasse) -> dict:
    return {
        "id": str(repasse.id),
        "pagamento_id": str(repasse.pagamento_id),
        "destinatario_usuario_id": str(repasse.destinatario_usuario_id)
        if repasse.destinatario_usuario_id
        else None,
        "empresa_fornecedora_id": str(repasse.empresa_fornecedora_id)
        if repasse.empresa_fornecedora_id
        else None,
        "tipo_repasse": repasse.tipo_repasse,
        "valor": float(repasse.valor),
        "status_repasse": repasse.status_repasse,
        "created_at": repasse.created_at.isoformat(),
    }


def _ranking_prestador_dict(db: Session, prestador: Prestador, filters: dict) -> dict:
    payment_conditions = [
        Repasse.destinatario_usuario_id == prestador.usuario_id,
        Repasse.tipo_repasse == "prestador",
        Repasse.deleted_at.is_(None),
    ]
    _aplicar_periodo(payment_conditions, Repasse.created_at, filters)
    valor_repasses = _scalar_float(
        db,
        select(func.coalesce(func.sum(Repasse.valor), 0)).where(*payment_conditions),
    )
    return {
        "prestador_id": str(prestador.id),
        "usuario_id": str(prestador.usuario_id),
        "nome": prestador.usuario.nome if prestador.usuario else None,
        "media_notas": float(prestador.media_notas),
        "total_avaliacoes": prestador.total_avaliacoes,
        "total_servicos_concluidos": prestador.total_servicos_concluidos,
        "quantidade_problemas": prestador.quantidade_problemas,
        "taxa_cancelamento": float(prestador.taxa_cancelamento),
        "garantias_acionadas": prestador.garantias_acionadas,
        "garantias_resolvidas": prestador.garantias_resolvidas,
        "garantias_nao_atendidas": prestador.garantias_nao_atendidas,
        "reincidencia_garantia": prestador.reincidencia_garantia,
        "valor_repasses": valor_repasses,
    }
