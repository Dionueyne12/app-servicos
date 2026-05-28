from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.schemas import SolicitacaoServicoCreateRequest  # noqa: E402
from auth.security import hash_password  # noqa: E402
from database.schema_updates import ensure_schema_updates  # noqa: E402
from database.session import SessionLocal, engine  # noqa: E402
from models import (  # noqa: E402
    Base,
    CategoriaServico,
    Cliente,
    Prestador,
    PrestadorValidacao,
    ServicoTabelado,
    SolicitacaoServico,
    StatusServico,
    Usuario,
)
from services.seed_service import ensure_default_admin  # noqa: E402
from services.service_request_service import (  # noqa: E402
    aceitar_solicitacao,
    concluir_servico,
    confirmar_conclusao_servico,
    criar_solicitacao,
    iniciar_servico,
)


DEMO_PASSWORD = "Demo@123"
CLIENTE_EMAIL = "cliente.demo@app.com"
PRESTADOR_EMAIL = "prestador.demo@app.com"
DEMO_MARKER = "SEED_GARANTIA_OPERACIONAL"


def main() -> None:
    print("[SEED DEMO] preparando banco")
    Base.metadata.create_all(bind=engine)
    ensure_schema_updates(engine)

    with SessionLocal() as db:
        ensure_default_admin(db)
        _ensure_status_servico(db)

        admin = _get_admin(db)
        cliente_usuario = _ensure_cliente(db)
        prestador_usuario = _ensure_prestador_aprovado(db, admin)
        categoria = _ensure_categoria(db, admin)
        servico = _ensure_servico_com_garantia(db, categoria, admin)

        solicitacao_existente = _buscar_fluxo_existente(db)
        if solicitacao_existente is not None:
            print("[SEED DEMO] fluxo de garantia ja existe, continuando do ponto atual")
            solicitacao_final = _continuar_fluxo(
                db,
                solicitacao_existente,
                cliente_usuario,
                prestador_usuario,
            )
            _print_resumo(solicitacao_final)
            return

        print("[SEED DEMO] criando solicitacao real pelo fluxo do cliente")
        solicitacao = criar_solicitacao(
            db,
            SolicitacaoServicoCreateRequest(
                cliente_id=str(cliente_usuario.cliente.id),
                tipo_servico="tabelado",
                servico_tabelado_id=str(servico.id),
                categoria_id=None,
                descricao_problema="Troca de chuveiro para validar garantia, retencao e repasse no painel admin.",
                endereco="Rua Demo Operacional, 100",
                urgencia="normal",
                melhor_horario="manha",
                observacoes=DEMO_MARKER,
                valor_mao_obra=None,
                tempo_estimado=None,
                tipo_material="material_indefinido",
            ),
            cliente_usuario,
        )

        print("[SEED DEMO] prestador aceitando servico")
        aceitar_solicitacao(db, str(solicitacao.id), prestador_usuario)

        print("[SEED DEMO] prestador iniciando servico")
        iniciar_servico(db, str(solicitacao.id), prestador_usuario)

        print("[SEED DEMO] prestador concluindo servico")
        concluir_servico(db, str(solicitacao.id), prestador_usuario)

        print("[SEED DEMO] cliente confirmando conclusao e gerando financeiro/garantia")
        solicitacao_final = confirmar_conclusao_servico(db, str(solicitacao.id), cliente_usuario)

        _print_resumo(solicitacao_final)


def _continuar_fluxo(db, solicitacao, cliente_usuario, prestador_usuario):
    if solicitacao.prestador_id is None and solicitacao.status_codigo == "aguardando_prestador":
        solicitacao = aceitar_solicitacao(db, str(solicitacao.id), prestador_usuario)

    if solicitacao.status_codigo in {"aceito", "material_aprovado"}:
        solicitacao = iniciar_servico(db, str(solicitacao.id), prestador_usuario)

    if solicitacao.status_codigo == "em_andamento":
        solicitacao = concluir_servico(db, str(solicitacao.id), prestador_usuario)

    if solicitacao.status_codigo == "aguardando_confirmacao_cliente":
        solicitacao = confirmar_conclusao_servico(db, str(solicitacao.id), cliente_usuario)

    return solicitacao


def _get_admin(db):
    admin = db.query(Usuario).filter(Usuario.email == "admin@app.com", Usuario.deleted_at.is_(None)).first()
    if admin is None:
        raise RuntimeError("Admin padrao nao foi criado.")
    return admin


def _ensure_cliente(db):
    usuario = db.query(Usuario).filter(Usuario.email == CLIENTE_EMAIL, Usuario.deleted_at.is_(None)).first()
    if usuario is None:
        usuario = Usuario(
            nome="Cliente Demo Garantia",
            email=CLIENTE_EMAIL,
            telefone="11977776666",
            senha_hash=hash_password(DEMO_PASSWORD),
            tipo_usuario="cliente",
            ativo=True,
        )
        db.add(usuario)
        db.flush()
        db.add(
            Cliente(
                usuario_id=usuario.id,
                documento="11122233344",
                endereco_principal="Rua Demo Operacional, 100",
                bairro="Centro",
                cidade="Sao Paulo",
                estado="SP",
                created_by_usuario_id=usuario.id,
            )
        )
        db.commit()
        db.refresh(usuario)
    return db.query(Usuario).filter(Usuario.id == usuario.id).first()


def _ensure_prestador_aprovado(db, admin):
    usuario = db.query(Usuario).filter(Usuario.email == PRESTADOR_EMAIL, Usuario.deleted_at.is_(None)).first()
    if usuario is None:
        usuario = Usuario(
            nome="Prestador Demo Garantia",
            email=PRESTADOR_EMAIL,
            telefone="11966665555",
            senha_hash=hash_password(DEMO_PASSWORD),
            tipo_usuario="prestador",
            ativo=True,
        )
        db.add(usuario)
        db.flush()
        prestador = Prestador(
            usuario_id=usuario.id,
            documento="55566677788",
            endereco_principal="Rua do Prestador Demo, 50",
            bairro="Centro",
            cidade="Sao Paulo",
            estado="SP",
            ativo=True,
            aceita_retencao_garantia=True,
            data_aceite_termos=datetime.now(timezone.utc),
            versao_termos="demo-1.0",
            created_by_usuario_id=admin.id,
        )
        db.add(prestador)
        db.flush()
        db.add(
            PrestadorValidacao(
                prestador_id=prestador.id,
                status_validacao="aprovado",
                data_aprovacao=datetime.now(timezone.utc),
                aprovado_por_admin_id=admin.id,
                created_by_usuario_id=admin.id,
            )
        )
        db.commit()
        db.refresh(usuario)
    else:
        usuario.ativo = True
        if usuario.prestador:
            usuario.prestador.ativo = True
            usuario.prestador.aceita_retencao_garantia = True
            usuario.prestador.versao_termos = usuario.prestador.versao_termos or "demo-1.0"
            if usuario.prestador.data_aceite_termos is None:
                usuario.prestador.data_aceite_termos = datetime.now(timezone.utc)
            if usuario.prestador.validacao is None:
                db.add(
                    PrestadorValidacao(
                        prestador_id=usuario.prestador.id,
                        status_validacao="aprovado",
                        data_aprovacao=datetime.now(timezone.utc),
                        aprovado_por_admin_id=admin.id,
                        created_by_usuario_id=admin.id,
                    )
                )
            else:
                usuario.prestador.validacao.status_validacao = "aprovado"
                usuario.prestador.validacao.data_aprovacao = datetime.now(timezone.utc)
                usuario.prestador.validacao.aprovado_por_admin_id = admin.id
        db.commit()
    return db.query(Usuario).filter(Usuario.id == usuario.id).first()


def _ensure_categoria(db, admin):
    categoria = db.query(CategoriaServico).filter(CategoriaServico.nome == "Demo Garantia").first()
    if categoria is None:
        categoria = CategoriaServico(
            nome="Demo Garantia",
            descricao="Categoria para validacao operacional de garantias e repasses.",
            ativo=True,
            created_by_usuario_id=admin.id,
        )
        db.add(categoria)
        db.commit()
        db.refresh(categoria)
    return categoria


def _ensure_servico_com_garantia(db, categoria, admin):
    servico = db.query(ServicoTabelado).filter(ServicoTabelado.nome == "Troca de chuveiro Demo Garantia").first()
    if servico is None:
        servico = ServicoTabelado(
            categoria_id=categoria.id,
            nome="Troca de chuveiro Demo Garantia",
            descricao="Servico de demonstracao com garantia, retencao e repasse para validar o painel.",
            preco_mao_obra=100,
            tempo_estimado_minutos=60,
            precisa_material=True,
            ativo=True,
            possui_garantia=True,
            dias_garantia=30,
            percentual_retencao_garantia=30,
            dias_liberacao_primeiro_repasse=7,
            descricao_garantia="Garantia demo de 30 dias vinculada ao prestador que executou o servico.",
            regras_garantia="Valida apenas para servicos realizados e confirmados dentro da plataforma.",
            created_by_usuario_id=admin.id,
        )
        db.add(servico)
    else:
        servico.ativo = True
        servico.possui_garantia = True
        servico.dias_garantia = 30
        servico.percentual_retencao_garantia = 30
        servico.dias_liberacao_primeiro_repasse = 7
        servico.preco_mao_obra = 100
        servico.updated_by_usuario_id = admin.id
    db.commit()
    db.refresh(servico)
    return servico


def _buscar_fluxo_existente(db):
    return (
        db.query(SolicitacaoServico)
        .filter(
            SolicitacaoServico.observacoes == DEMO_MARKER,
            SolicitacaoServico.deleted_at.is_(None),
        )
        .order_by(SolicitacaoServico.created_at.desc())
        .first()
    )


def _ensure_status_servico(db) -> None:
    statuses = [
        ("rascunho", "Rascunho", 10, False),
        ("aguardando_prestador", "Aguardando prestador", 20, False),
        ("aceito", "Aceito", 30, False),
        ("aguardando_material", "Aguardando material", 35, False),
        ("aguardando_avaliacao_material", "Aguardando avaliacao de material", 40, False),
        ("aguardando_aprovacao_cliente", "Aguardando aprovacao do cliente", 50, False),
        ("material_aprovado", "Material aprovado", 60, False),
        ("em_andamento", "Em andamento", 70, False),
        ("aguardando_confirmacao", "Aguardando confirmacao", 75, False),
        ("aguardando_confirmacao_cliente", "Aguardando confirmacao do cliente", 80, False),
        ("concluido", "Concluido", 90, True),
        ("cancelado", "Cancelado", 100, True),
        ("em_analise", "Em analise", 110, False),
    ]
    for codigo, nome, ordem, finaliza in statuses:
        status = db.get(StatusServico, codigo)
        if status is None:
            db.add(StatusServico(codigo=codigo, nome=nome, ordem=ordem, finaliza_fluxo=finaliza))
        else:
            status.nome = nome
            status.ordem = ordem
            status.finaliza_fluxo = finaliza
    db.commit()


def _print_resumo(solicitacao) -> None:
    print("[SEED DEMO] fluxo pronto")
    print(f"  Cliente: {CLIENTE_EMAIL} / senha {DEMO_PASSWORD}")
    print(f"  Prestador: {PRESTADOR_EMAIL} / senha {DEMO_PASSWORD}")
    print(f"  Solicitacao: {solicitacao.id}")
    print(f"  Status: {solicitacao.status_codigo}")
    if solicitacao.pagamento:
        print(f"  Pagamento simulado: {solicitacao.pagamento.id}")
        print(f"  Mao de obra: R$ {float(solicitacao.pagamento.valor_mao_obra):.2f}")
        print(f"  Comissao plataforma: R$ {float(solicitacao.pagamento.valor_comissao):.2f}")
        print(f"  Valor prestador liquido: R$ {float(solicitacao.pagamento.valor_prestador):.2f}")
        for repasse in solicitacao.pagamento.repasses:
            print(f"  Repasse {repasse.tipo_repasse}: R$ {float(repasse.valor):.2f} ({repasse.status_repasse})")
    if solicitacao.garantia:
        print(f"  Garantia: {solicitacao.garantia.id}")
        print(f"  Status garantia: {solicitacao.garantia.status_garantia}")
        print(f"  Valor retido: R$ {float(solicitacao.garantia.valor_retido):.2f}")
        print(f"  Valor liberado inicial: R$ {float(solicitacao.garantia.valor_liberado_inicial):.2f}")


if __name__ == "__main__":
    main()
