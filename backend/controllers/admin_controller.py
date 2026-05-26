from collections.abc import Callable

from sqlalchemy.orm import Session

from app.pagination import PageParams, build_pagination_meta
from models import Usuario
from services.admin_service import (
    aprovar_prestador_admin,
    dashboard_admin,
    documentos_prestador_admin,
    listar_avaliacoes_admin,
    listar_clientes_admin,
    listar_materiais_admin,
    listar_notificacoes_admin,
    listar_prestadores_admin,
    listar_prestadores_pendentes_admin,
    ranking_prestadores_admin,
    relatorio_financeiro_admin,
    relatorio_repasses_admin,
    listar_solicitacoes_admin,
    listar_usuarios_admin,
    metricas_admin,
    monitoramento_admin,
    rejeitar_prestador_admin,
    servicos_mais_pedidos_admin,
)


def dashboard_admin_controller(db: Session, admin: Usuario) -> dict:
    return dashboard_admin(db, admin)


def metricas_admin_controller(db: Session, admin: Usuario) -> dict:
    return metricas_admin(db, admin)


def monitoramento_admin_controller(db: Session) -> dict:
    return monitoramento_admin(db)


def listar_usuarios_admin_controller(db: Session, pagination: PageParams, filters: dict) -> dict:
    return _paginated(listar_usuarios_admin, db, pagination, filters)


def listar_clientes_admin_controller(db: Session, pagination: PageParams, filters: dict) -> dict:
    return _paginated(listar_clientes_admin, db, pagination, filters)


def listar_prestadores_admin_controller(db: Session, pagination: PageParams, filters: dict) -> dict:
    return _paginated(listar_prestadores_admin, db, pagination, filters)


def listar_prestadores_pendentes_admin_controller(db: Session, pagination: PageParams) -> dict:
    return listar_prestadores_pendentes_admin(db, pagination)


def aprovar_prestador_admin_controller(db: Session, prestador_id: str, admin: Usuario) -> dict:
    return aprovar_prestador_admin(db, prestador_id, admin)


def rejeitar_prestador_admin_controller(db: Session, prestador_id: str, observacao: str, admin: Usuario) -> dict:
    return rejeitar_prestador_admin(db, prestador_id, observacao, admin)


def documentos_prestador_admin_controller(db: Session, prestador_id: str) -> dict:
    return documentos_prestador_admin(db, prestador_id)


def listar_solicitacoes_admin_controller(db: Session, pagination: PageParams, filters: dict) -> dict:
    return _paginated(listar_solicitacoes_admin, db, pagination, filters)


def listar_materiais_admin_controller(db: Session, pagination: PageParams, filters: dict) -> dict:
    return _paginated(listar_materiais_admin, db, pagination, filters)


def listar_avaliacoes_admin_controller(db: Session, pagination: PageParams, filters: dict) -> dict:
    return _paginated(listar_avaliacoes_admin, db, pagination, filters)


def listar_notificacoes_admin_controller(db: Session, pagination: PageParams, filters: dict) -> dict:
    return _paginated(listar_notificacoes_admin, db, pagination, filters)


def relatorio_financeiro_admin_controller(db: Session, filters: dict) -> dict:
    return relatorio_financeiro_admin(db, filters)


def relatorio_repasses_admin_controller(db: Session, pagination: PageParams, filters: dict) -> dict:
    return _paginated(relatorio_repasses_admin, db, pagination, filters)


def ranking_prestadores_admin_controller(db: Session, pagination: PageParams, filters: dict) -> dict:
    return _paginated(ranking_prestadores_admin, db, pagination, filters)


def servicos_mais_pedidos_admin_controller(db: Session, pagination: PageParams, filters: dict) -> dict:
    return _paginated(servicos_mais_pedidos_admin, db, pagination, filters)


def _paginated(fn: Callable, db: Session, pagination: PageParams, filters: dict) -> dict:
    items, total = fn(db, pagination, filters)
    return {
        "items": items,
        "meta": build_pagination_meta(total, pagination).model_dump(),
    }
