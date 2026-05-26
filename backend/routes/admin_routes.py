import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.pagination import PageParams
from app.schemas import AdminPrestadorRejeitarRequest, LoginRequest, TokenResponse
from auth.dependencies import require_admin
from controllers.auth_controller import admin_login_controller
from controllers.admin_controller import (
    aprovar_prestador_admin_controller,
    dashboard_admin_controller,
    documentos_prestador_admin_controller,
    listar_avaliacoes_admin_controller,
    listar_clientes_admin_controller,
    listar_materiais_admin_controller,
    listar_notificacoes_admin_controller,
    listar_prestadores_admin_controller,
    listar_prestadores_pendentes_admin_controller,
    ranking_prestadores_admin_controller,
    relatorio_financeiro_admin_controller,
    relatorio_repasses_admin_controller,
    listar_solicitacoes_admin_controller,
    listar_usuarios_admin_controller,
    metricas_admin_controller,
    monitoramento_admin_controller,
    rejeitar_prestador_admin_controller,
    servicos_mais_pedidos_admin_controller,
)
from database.session import get_db
from models import Usuario


router = APIRouter(prefix="/admin", tags=["admin"])
logger = logging.getLogger("admin.login")


@router.post("/login", response_model=TokenResponse)
def login_admin(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    logger.info("[ADMIN LOGIN] request recebida")
    token = admin_login_controller(payload, db)
    logger.info("[ADMIN LOGIN] admin encontrado")
    logger.info("[ADMIN LOGIN] token gerado")
    return token


@router.get("/dashboard")
def dashboard_admin(
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    return dashboard_admin_controller(db, admin)


@router.get("/metricas")
def metricas_admin(
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    return metricas_admin_controller(db, admin)


@router.get("/monitoramento")
def monitoramento_admin(
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    return monitoramento_admin_controller(db)


@router.get("/usuarios")
def listar_usuarios_admin(
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
    tipo_usuario: str | None = Query(default=None, max_length=30),
    data_inicio: str | None = Query(default=None, max_length=30),
    data_fim: str | None = Query(default=None, max_length=30),
    ativo: bool | None = Query(default=None),
) -> dict:
    return listar_usuarios_admin_controller(
        db,
        pagination,
        _filters(tipo_usuario=tipo_usuario, data_inicio=data_inicio, data_fim=data_fim, ativo=ativo),
    )


@router.get("/clientes")
def listar_clientes_admin(
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
    cliente_id: str | None = Query(default=None, max_length=60),
    data_inicio: str | None = Query(default=None, max_length=30),
    data_fim: str | None = Query(default=None, max_length=30),
) -> dict:
    return listar_clientes_admin_controller(
        db,
        pagination,
        _filters(cliente_id=cliente_id, data_inicio=data_inicio, data_fim=data_fim),
    )


@router.get("/prestadores")
def listar_prestadores_admin(
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
    prestador_id: str | None = Query(default=None, max_length=60),
    status_validacao: str | None = Query(default=None, max_length=40),
    data_inicio: str | None = Query(default=None, max_length=30),
    data_fim: str | None = Query(default=None, max_length=30),
    ativo: bool | None = Query(default=None),
) -> dict:
    return listar_prestadores_admin_controller(
        db,
        pagination,
        _filters(
            prestador_id=prestador_id,
            status_validacao=status_validacao,
            data_inicio=data_inicio,
            data_fim=data_fim,
            ativo=ativo,
        ),
    )


@router.get("/prestadores/pendentes")
def listar_prestadores_pendentes_admin(
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
) -> dict:
    return listar_prestadores_pendentes_admin_controller(db, pagination)


@router.patch("/prestadores/{prestador_id}/aprovar")
def aprovar_prestador_admin(
    prestador_id: str,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    return aprovar_prestador_admin_controller(db, prestador_id, admin)


@router.patch("/prestadores/{prestador_id}/rejeitar")
def rejeitar_prestador_admin(
    prestador_id: str,
    payload: AdminPrestadorRejeitarRequest,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    return rejeitar_prestador_admin_controller(db, prestador_id, payload.observacao_admin, admin)


@router.get("/prestadores/{prestador_id}/documentos")
def documentos_prestador_admin(
    prestador_id: str,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    return documentos_prestador_admin_controller(db, prestador_id)


@router.get("/solicitacoes")
def listar_solicitacoes_admin(
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
    status: str | None = Query(default=None, max_length=60),
    cliente_id: str | None = Query(default=None, max_length=60),
    prestador_id: str | None = Query(default=None, max_length=60),
    categoria: str | None = Query(default=None, max_length=120),
    data_inicio: str | None = Query(default=None, max_length=30),
    data_fim: str | None = Query(default=None, max_length=30),
) -> dict:
    return listar_solicitacoes_admin_controller(
        db,
        pagination,
        _filters(
            status=status,
            cliente_id=cliente_id,
            prestador_id=prestador_id,
            categoria=categoria,
            data_inicio=data_inicio,
            data_fim=data_fim,
        ),
    )


@router.get("/materiais")
def listar_materiais_admin(
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
    status: str | None = Query(default=None, max_length=60),
    prestador_id: str | None = Query(default=None, max_length=60),
    data_inicio: str | None = Query(default=None, max_length=30),
    data_fim: str | None = Query(default=None, max_length=30),
) -> dict:
    return listar_materiais_admin_controller(
        db,
        pagination,
        _filters(status=status, prestador_id=prestador_id, data_inicio=data_inicio, data_fim=data_fim),
    )


@router.get("/avaliacoes")
def listar_avaliacoes_admin(
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
    data_inicio: str | None = Query(default=None, max_length=30),
    data_fim: str | None = Query(default=None, max_length=30),
) -> dict:
    return listar_avaliacoes_admin_controller(
        db,
        pagination,
        _filters(data_inicio=data_inicio, data_fim=data_fim),
    )


@router.get("/notificacoes")
def listar_notificacoes_admin(
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
    status: str | None = Query(default=None, max_length=60),
    tipo_usuario: str | None = Query(default=None, max_length=30),
    data_inicio: str | None = Query(default=None, max_length=30),
    data_fim: str | None = Query(default=None, max_length=30),
) -> dict:
    return listar_notificacoes_admin_controller(
        db,
        pagination,
        _filters(status=status, tipo_usuario=tipo_usuario, data_inicio=data_inicio, data_fim=data_fim),
    )


@router.get("/relatorios/financeiro")
def relatorio_financeiro_admin(
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
    status: str | None = Query(default=None, max_length=40),
    data_inicio: str | None = Query(default=None, max_length=30),
    data_fim: str | None = Query(default=None, max_length=30),
) -> dict:
    return relatorio_financeiro_admin_controller(
        db,
        _filters(status=status, data_inicio=data_inicio, data_fim=data_fim),
    )


@router.get("/relatorios/repasses")
def relatorio_repasses_admin(
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
    status: str | None = Query(default=None, max_length=40),
    tipo_repasse: str | None = Query(default=None, max_length=40),
    data_inicio: str | None = Query(default=None, max_length=30),
    data_fim: str | None = Query(default=None, max_length=30),
) -> dict:
    return relatorio_repasses_admin_controller(
        db,
        pagination,
        _filters(status=status, tipo_repasse=tipo_repasse, data_inicio=data_inicio, data_fim=data_fim),
    )


@router.get("/relatorios/ranking-prestadores")
def ranking_prestadores_admin(
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
    prestador_id: str | None = Query(default=None, max_length=60),
    ativo: bool | None = Query(default=None),
    data_inicio: str | None = Query(default=None, max_length=30),
    data_fim: str | None = Query(default=None, max_length=30),
) -> dict:
    return ranking_prestadores_admin_controller(
        db,
        pagination,
        _filters(prestador_id=prestador_id, ativo=ativo, data_inicio=data_inicio, data_fim=data_fim),
    )


@router.get("/relatorios/servicos-mais-pedidos")
def servicos_mais_pedidos_admin(
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
    pagination: PageParams = Depends(),
    status: str | None = Query(default=None, max_length=60),
    categoria: str | None = Query(default=None, max_length=120),
    data_inicio: str | None = Query(default=None, max_length=30),
    data_fim: str | None = Query(default=None, max_length=30),
) -> dict:
    return servicos_mais_pedidos_admin_controller(
        db,
        pagination,
        _filters(status=status, categoria=categoria, data_inicio=data_inicio, data_fim=data_fim),
    )


def _filters(**kwargs) -> dict:
    return {key: value for key, value in kwargs.items() if value is not None}
