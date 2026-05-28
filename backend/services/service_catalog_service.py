from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.pagination import PageParams
from app.schemas import ServicoTabeladoCreateRequest, ServicoTabeladoUpdateRequest
from models import CategoriaServico, ServicoTabelado
from models import Usuario
from utils.exceptions import BadRequestError


def listar_categorias_servico(db: Session, ativo: bool | None = True) -> list[CategoriaServico]:
    filters = [CategoriaServico.deleted_at.is_(None)]
    if ativo is not None:
        filters.append(CategoriaServico.ativo.is_(ativo))

    return list(
        db.scalars(
            select(CategoriaServico)
            .where(*filters)
            .order_by(CategoriaServico.nome)
        )
    )


def listar_servicos_tabelados(
    db: Session,
    pagination: PageParams,
    busca: str | None,
    ativo: bool | None,
) -> tuple[list[ServicoTabelado], int]:
    filters = []
    filters.append(ServicoTabelado.deleted_at.is_(None))
    if ativo is not None:
        filters.append(ServicoTabelado.ativo.is_(ativo))
    if busca:
        filters.append(ServicoTabelado.nome.ilike(f"%{busca.strip()}%"))

    total = db.scalar(select(func.count()).select_from(ServicoTabelado).where(*filters)) or 0
    items = list(
        db.scalars(
            select(ServicoTabelado)
            .where(*filters)
            .order_by(ServicoTabelado.nome)
            .offset(pagination.offset)
            .limit(pagination.per_page)
        )
    )
    return items, total


def criar_servico_tabelado(
    db: Session,
    payload: ServicoTabeladoCreateRequest,
    usuario: Usuario,
) -> ServicoTabelado:
    categoria_id = _parse_uuid(payload.categoria_id, "Categoria invalida.")
    _garantir_categoria_existe(db, categoria_id)

    servico = ServicoTabelado(
        categoria_id=categoria_id,
        nome=payload.nome.strip(),
        descricao=payload.descricao.strip(),
        preco_mao_obra=payload.preco_mao_obra,
        tempo_estimado_minutos=payload.tempo_estimado_minutos,
        precisa_material=payload.precisa_material,
        possui_garantia=payload.possui_garantia,
        dias_garantia=payload.dias_garantia,
        percentual_retencao_garantia=payload.percentual_retencao_garantia,
        dias_liberacao_primeiro_repasse=payload.dias_liberacao_primeiro_repasse,
        descricao_garantia=payload.descricao_garantia.strip() if payload.descricao_garantia else None,
        regras_garantia=payload.regras_garantia.strip() if payload.regras_garantia else None,
        created_by_usuario_id=usuario.id,
    )
    db.add(servico)
    db.commit()
    db.refresh(servico)
    return servico


def editar_servico_tabelado(
    db: Session,
    servico_id: str,
    payload: ServicoTabeladoUpdateRequest,
    usuario: Usuario,
) -> ServicoTabelado:
    servico = _buscar_servico(db, servico_id)

    if payload.categoria_id is not None:
        categoria_id = _parse_uuid(payload.categoria_id, "Categoria invalida.")
        _garantir_categoria_existe(db, categoria_id)
        servico.categoria_id = categoria_id
    if payload.nome is not None:
        servico.nome = payload.nome.strip()
    if payload.descricao is not None:
        servico.descricao = payload.descricao.strip()
    if payload.preco_mao_obra is not None:
        servico.preco_mao_obra = payload.preco_mao_obra
    if payload.tempo_estimado_minutos is not None:
        servico.tempo_estimado_minutos = payload.tempo_estimado_minutos
    if payload.precisa_material is not None:
        servico.precisa_material = payload.precisa_material
    if payload.possui_garantia is not None:
        servico.possui_garantia = payload.possui_garantia
    if payload.dias_garantia is not None:
        servico.dias_garantia = payload.dias_garantia
    if payload.percentual_retencao_garantia is not None:
        servico.percentual_retencao_garantia = payload.percentual_retencao_garantia
    if payload.dias_liberacao_primeiro_repasse is not None:
        servico.dias_liberacao_primeiro_repasse = payload.dias_liberacao_primeiro_repasse
    if payload.descricao_garantia is not None:
        servico.descricao_garantia = payload.descricao_garantia.strip() or None
    if payload.regras_garantia is not None:
        servico.regras_garantia = payload.regras_garantia.strip() or None
    servico.updated_by_usuario_id = usuario.id

    db.commit()
    db.refresh(servico)
    return servico


def ativar_servico_tabelado(
    db: Session,
    servico_id: str,
    ativo: bool,
    usuario: Usuario,
) -> ServicoTabelado:
    servico = _buscar_servico(db, servico_id)
    servico.ativo = ativo
    servico.updated_by_usuario_id = usuario.id
    db.commit()
    db.refresh(servico)
    return servico


def _buscar_servico(db: Session, servico_id: str) -> ServicoTabelado:
    parsed_id = _parse_uuid(servico_id, "Servico invalido.")
    servico = db.get(ServicoTabelado, parsed_id)
    if servico is None or servico.deleted_at is not None:
        raise BadRequestError("Servico tabelado nao encontrado.")
    return servico


def _garantir_categoria_existe(db: Session, categoria_id: UUID) -> None:
    categoria = db.get(CategoriaServico, categoria_id)
    if categoria is None or not categoria.ativo:
        raise BadRequestError("Categoria de servico nao encontrada ou inativa.")


def _parse_uuid(value: str, message: str) -> UUID:
    try:
        return UUID(value)
    except ValueError as exc:
        raise BadRequestError(message) from exc
