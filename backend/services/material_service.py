from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.schemas import MaterialServicoCreateRequest
from models import (
    EmpresaFornecedora,
    HistoricoEdicao,
    HistoricoStatus,
    MaterialServico,
    SolicitacaoServico,
    Usuario,
)
from utils.exceptions import BadRequestError, UnauthorizedError


STATUS_AGUARDANDO_APROVACAO_CLIENTE = "aguardando_aprovacao_cliente"
STATUS_AGUARDANDO_AVALIACAO_MATERIAL = "aguardando_avaliacao_material"
STATUS_MATERIAL_APROVADO = "material_aprovado"


def criar_ou_atualizar_material(
    db: Session,
    solicitacao_id: str,
    payload: MaterialServicoCreateRequest,
    usuario: Usuario,
) -> MaterialServico:
    solicitacao = _buscar_solicitacao(db, solicitacao_id)
    _garantir_prestador_da_solicitacao(solicitacao, usuario)
    _validar_empresa(db, payload.empresa_fornecedora_id)

    material = solicitacao.material
    if material is None:
        material = MaterialServico(
            solicitacao_id=solicitacao.id,
            escolha_cliente="prestador_providencia_material",
            created_by_usuario_id=usuario.id,
        )
        db.add(material)
        db.flush()

    changes = []
    _set_if_changed(material, "prestador_id", usuario.prestador.id, changes)
    _set_if_changed(material, "empresa_fornecedora_id", _parse_uuid_or_none(payload.empresa_fornecedora_id), changes)
    _set_if_changed(material, "descricao", payload.descricao_material.strip(), changes)
    _set_if_changed(material, "descricao_material", payload.descricao_material.strip(), changes)
    _set_if_changed(material, "valor_estimado", payload.valor_estimado, changes)
    _set_if_changed(material, "necessita_aprovacao_cliente", payload.necessita_aprovacao_cliente, changes)
    _set_if_changed(material, "aprovado_cliente", None, changes)
    _set_if_changed(material, "aprovado_pelo_cliente", None, changes)
    _set_if_changed(material, "observacao_cliente", None, changes)

    novo_status_material = (
        "aguardando_aprovacao_cliente"
        if payload.necessita_aprovacao_cliente
        else "aprovado"
    )
    _set_if_changed(material, "status_material", novo_status_material, changes)
    material.updated_by_usuario_id = usuario.id

    if payload.necessita_aprovacao_cliente:
        _alterar_status_solicitacao(
            db,
            solicitacao,
            STATUS_AGUARDANDO_APROVACAO_CLIENTE,
            usuario,
            "Material informado e aguardando aprovacao do cliente.",
        )
    else:
        _alterar_status_solicitacao(
            db,
            solicitacao,
            STATUS_MATERIAL_APROVADO,
            usuario,
            "Material informado sem necessidade de aprovacao.",
        )

    _registrar_historico_edicoes(db, material.id, usuario.id, changes)
    from services.notification_service import notificar_participante_solicitacao

    notificar_participante_solicitacao(
        db,
        solicitacao.id,
        "cliente",
        "material_enviado",
        "Material enviado para aprovacao",
        "O prestador informou o material necessario para o servico.",
        prioridade="alta" if payload.necessita_aprovacao_cliente else "normal",
        created_by_usuario_id=usuario.id,
    )
    db.commit()
    return _buscar_material(db, material.id)


def listar_materiais_solicitacao(db: Session, solicitacao_id: str, usuario: Usuario) -> list[MaterialServico]:
    solicitacao = _buscar_solicitacao(db, solicitacao_id)
    _garantir_acesso_solicitacao(solicitacao, usuario)
    if solicitacao.material is None or solicitacao.material.deleted_at is not None:
        return []
    return [solicitacao.material]


def aprovar_material(db: Session, material_id: str, usuario: Usuario, observacao: str | None) -> MaterialServico:
    material = _buscar_material(db, _parse_uuid(material_id, "Material invalido."))
    _garantir_cliente_da_solicitacao(material.solicitacao, usuario)
    changes = _atualizar_status_cliente(material, "aprovado", True, observacao, usuario)
    _alterar_status_solicitacao(
        db,
        material.solicitacao,
        STATUS_MATERIAL_APROVADO,
        usuario,
        "Material aprovado pelo cliente.",
    )
    _registrar_historico_edicoes(db, material.id, usuario.id, changes)
    from services.chat_service import registrar_mensagem_sistema

    registrar_mensagem_sistema(
        db,
        material.solicitacao,
        "Material aprovado pelo cliente.",
        usuario.id,
    )
    from services.notification_service import notificar_participante_solicitacao

    notificar_participante_solicitacao(
        db,
        material.solicitacao_id,
        "prestador",
        "material_aprovado",
        "Material aprovado",
        "O cliente aprovou o material do servico.",
        created_by_usuario_id=usuario.id,
    )
    db.commit()
    return _buscar_material(db, material.id)


def recusar_material(db: Session, material_id: str, usuario: Usuario, observacao: str | None) -> MaterialServico:
    material = _buscar_material(db, _parse_uuid(material_id, "Material invalido."))
    _garantir_cliente_da_solicitacao(material.solicitacao, usuario)
    changes = _atualizar_status_cliente(material, "recusado", False, observacao, usuario)
    _alterar_status_solicitacao(
        db,
        material.solicitacao,
        STATUS_AGUARDANDO_AVALIACAO_MATERIAL,
        usuario,
        "Material recusado pelo cliente. Aguardando nova avaliacao do prestador.",
    )
    _registrar_historico_edicoes(db, material.id, usuario.id, changes)
    from services.notification_service import notificar_participante_solicitacao

    notificar_participante_solicitacao(
        db,
        material.solicitacao_id,
        "prestador",
        "material_recusado",
        "Material recusado",
        "O cliente recusou o material informado.",
        prioridade="alta",
        created_by_usuario_id=usuario.id,
    )
    db.commit()
    return _buscar_material(db, material.id)


def solicitar_alteracao_material(
    db: Session,
    material_id: str,
    usuario: Usuario,
    observacao: str | None,
) -> MaterialServico:
    material = _buscar_material(db, _parse_uuid(material_id, "Material invalido."))
    _garantir_cliente_da_solicitacao(material.solicitacao, usuario)
    changes = _atualizar_status_cliente(material, "alteracao_solicitada", False, observacao, usuario)
    _alterar_status_solicitacao(
        db,
        material.solicitacao,
        STATUS_AGUARDANDO_AVALIACAO_MATERIAL,
        usuario,
        "Cliente solicitou alteracao no material.",
    )
    _registrar_historico_edicoes(db, material.id, usuario.id, changes)
    db.commit()
    return _buscar_material(db, material.id)


def marcar_comprado_retirado(db: Session, material_id: str, usuario: Usuario) -> MaterialServico:
    material = _buscar_material(db, _parse_uuid(material_id, "Material invalido."))
    _garantir_prestador_da_solicitacao(material.solicitacao, usuario)
    if material.status_material != "aprovado":
        raise BadRequestError("Material precisa estar aprovado antes de comprado/retirado.")
    changes = []
    _set_if_changed(material, "status_material", "comprado_retirado", changes)
    material.updated_by_usuario_id = usuario.id
    _alterar_status_solicitacao(
        db,
        material.solicitacao,
        STATUS_MATERIAL_APROVADO,
        usuario,
        "Material comprado ou retirado pelo prestador.",
    )
    _registrar_historico_edicoes(db, material.id, usuario.id, changes)
    db.commit()
    return _buscar_material(db, material.id)


def _atualizar_status_cliente(
    material: MaterialServico,
    status_material: str,
    aprovado: bool,
    observacao: str | None,
    usuario: Usuario,
) -> list[tuple[str, object, object]]:
    changes = []
    now = datetime.now(timezone.utc)
    _set_if_changed(material, "status_material", status_material, changes)
    _set_if_changed(material, "aprovado_cliente", aprovado, changes)
    _set_if_changed(material, "aprovado_pelo_cliente", aprovado, changes)
    _set_if_changed(material, "data_aprovacao", now, changes)
    _set_if_changed(material, "aprovado_em", now, changes)
    if observacao is not None:
        _set_if_changed(material, "observacao_cliente", observacao, changes)
    material.updated_by_usuario_id = usuario.id
    return changes


def _alterar_status_solicitacao(
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


def _buscar_solicitacao(db: Session, solicitacao_id: str) -> SolicitacaoServico:
    solicitacao = db.scalar(
        select(SolicitacaoServico)
        .where(
            SolicitacaoServico.id == _parse_uuid(solicitacao_id, "Solicitacao invalida."),
            SolicitacaoServico.deleted_at.is_(None),
        )
        .options(selectinload(SolicitacaoServico.material))
    )
    if solicitacao is None:
        raise BadRequestError("Solicitacao nao encontrada.")
    return solicitacao


def _buscar_material(db: Session, material_id: UUID) -> MaterialServico:
    material = db.scalar(
        select(MaterialServico)
        .where(MaterialServico.id == material_id, MaterialServico.deleted_at.is_(None))
        .options(selectinload(MaterialServico.solicitacao))
    )
    if material is None:
        raise BadRequestError("Material nao encontrado.")
    return material


def _garantir_prestador_da_solicitacao(solicitacao: SolicitacaoServico, usuario: Usuario) -> None:
    if usuario.tipo_usuario != "prestador" or usuario.prestador is None:
        raise UnauthorizedError("Apenas o prestador pode informar material.")
    if solicitacao.prestador_id != usuario.prestador.id:
        raise UnauthorizedError("Prestador nao aceitou esta solicitacao.")


def _garantir_cliente_da_solicitacao(solicitacao: SolicitacaoServico, usuario: Usuario) -> None:
    if usuario.tipo_usuario != "cliente" or usuario.cliente is None:
        raise UnauthorizedError("Apenas o cliente pode aprovar ou recusar material.")
    if solicitacao.cliente_id != usuario.cliente.id:
        raise UnauthorizedError("Cliente nao pertence a esta solicitacao.")


def _garantir_acesso_solicitacao(solicitacao: SolicitacaoServico, usuario: Usuario) -> None:
    if usuario.tipo_usuario == "admin":
        return
    if usuario.tipo_usuario == "cliente" and usuario.cliente and solicitacao.cliente_id == usuario.cliente.id:
        return
    if usuario.tipo_usuario == "prestador" and usuario.prestador and solicitacao.prestador_id == usuario.prestador.id:
        return
    raise UnauthorizedError("Usuario nao pode visualizar material desta solicitacao.")


def _validar_empresa(db: Session, empresa_id: str | None) -> None:
    if not empresa_id:
        return
    empresa = db.get(EmpresaFornecedora, _parse_uuid(empresa_id, "Empresa fornecedora invalida."))
    if empresa is None or not empresa.ativo:
        raise BadRequestError("Empresa fornecedora nao encontrada ou inativa.")


def _set_if_changed(target, field: str, new_value, changes: list[tuple[str, object, object]]) -> None:
    old_value = getattr(target, field)
    if old_value != new_value:
        setattr(target, field, new_value)
        changes.append((field, old_value, new_value))


def _registrar_historico_edicoes(
    db: Session,
    material_id: UUID,
    usuario_id: UUID,
    changes: list[tuple[str, object, object]],
) -> None:
    for field, old_value, new_value in changes:
        db.add(
            HistoricoEdicao(
                entidade="materiais_servico",
                entidade_id=material_id,
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


def _parse_uuid_or_none(value: str | None) -> UUID | None:
    if not value:
        return None
    return _parse_uuid(value, "Identificador invalido.")
