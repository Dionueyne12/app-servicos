import os
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/app_servicos_test",
)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = PROJECT_ROOT / "database" / "migrations"


def _psycopg_url(sqlalchemy_url: str) -> str:
    return sqlalchemy_url.replace("postgresql+psycopg://", "postgresql://", 1)


def _maintenance_url(sqlalchemy_url: str) -> str:
    url = _psycopg_url(sqlalchemy_url)
    return url.rsplit("/", 1)[0] + "/postgres"


def _database_name(sqlalchemy_url: str) -> str:
    return sqlalchemy_url.rsplit("/", 1)[1]


def _ensure_test_database() -> None:
    database_name = _database_name(TEST_DATABASE_URL)
    with psycopg.connect(_maintenance_url(TEST_DATABASE_URL), autocommit=True) as conn:
        exists = conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (database_name,),
        ).fetchone()
        if not exists:
            conn.execute(f'CREATE DATABASE "{database_name}"')


def _apply_migrations() -> None:
    with psycopg.connect(_psycopg_url(TEST_DATABASE_URL), autocommit=True) as conn:
        conn.execute("DROP SCHEMA IF EXISTS public CASCADE")
        conn.execute("CREATE SCHEMA public")
        conn.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
        for migration in sorted(MIGRATIONS_DIR.glob("*.sql")):
            conn.execute(migration.read_text(encoding="utf-8"))
        conn.execute(
            """
            INSERT INTO status_servico (codigo, nome, ordem, finaliza_fluxo) VALUES
                ('rascunho', 'Rascunho', 10, FALSE),
                ('aguardando_prestador', 'Aguardando prestador', 20, FALSE),
                ('aceito', 'Aceito', 30, FALSE),
                ('aguardando_material', 'Aguardando material', 35, FALSE),
                ('aguardando_avaliacao_material', 'Aguardando avaliacao de material', 40, FALSE),
                ('aguardando_aprovacao_cliente', 'Aguardando aprovacao do cliente', 50, FALSE),
                ('material_aprovado', 'Material aprovado', 60, FALSE),
                ('em_andamento', 'Em andamento', 70, FALSE),
                ('aguardando_confirmacao', 'Aguardando confirmacao', 75, FALSE),
                ('aguardando_confirmacao_cliente', 'Aguardando confirmacao do cliente', 80, FALSE),
                ('concluido', 'Concluido', 90, TRUE),
                ('cancelado', 'Cancelado', 100, TRUE),
                ('em_analise', 'Em analise', 110, FALSE)
            ON CONFLICT (codigo) DO UPDATE SET
                nome = EXCLUDED.nome,
                ordem = EXCLUDED.ordem,
                finaliza_fluxo = EXCLUDED.finaliza_fluxo
            """
        )


_ensure_test_database()
_apply_migrations()

from app.main import app  # noqa: E402
from auth.security import hash_password  # noqa: E402
from database.session import get_db  # noqa: E402
from models import CategoriaServico, Cliente, Prestador, Usuario  # noqa: E402


engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def clean_database():
    tables = [
        "movimentacoes_carteira",
        "carteira_usuario",
        "pagamentos",
        "repasses",
        "pagamentos_simulados",
        "notificacoes",
        "mensagens_solicitacao",
        "avaliacoes",
        "fotos_servico",
        "materiais_servico",
        "historico_status",
        "historico_edicoes",
        "solicitacoes_servico",
        "servicos_tabelados",
        "categorias_servico",
        "empresas_fornecedoras",
        "prestadores",
        "clientes",
        "usuarios",
    ]
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {', '.join(tables)} RESTART IDENTITY CASCADE"))
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def unique_email(prefix: str) -> str:
    return f"{prefix}.{uuid4().hex[:10]}@teste.com"


def login(client: TestClient, email: str, senha: str = "Senha123") -> str:
    response = client.post("/api/v1/auth/login", json={"email": email, "senha": senha})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def cadastrar_perfil(client: TestClient, rota: str, email: str, senha: str = "Senha123") -> dict:
    response = client.post(
        rota,
        json={
            "nome": "Usuario Teste",
            "email": email,
            "telefone": "11988887777",
            "senha": senha,
            "documento": "12345678900",
            "endereco": "Rua Teste, 123",
            "bairro": "Centro",
            "cidade": "Sao Paulo",
            "estado": "SP",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def cliente_auth(client, db_session):
    email = unique_email("cliente")
    cadastrar_perfil(client, "/api/v1/clientes/cadastro", email)
    token = login(client, email)
    cliente = db_session.scalar(select(Cliente).join(Usuario).where(Usuario.email == email))
    return {"email": email, "token": token, "cliente_id": str(cliente.id), "usuario_id": str(cliente.usuario_id)}


@pytest.fixture
def prestador_auth(client, db_session):
    email = unique_email("prestador")
    cadastrar_perfil(client, "/api/v1/prestadores/cadastro", email)
    token = login(client, email)
    prestador = db_session.scalar(select(Prestador).join(Usuario).where(Usuario.email == email))
    return {
        "email": email,
        "token": token,
        "prestador_id": str(prestador.id),
        "usuario_id": str(prestador.usuario_id),
    }


@pytest.fixture
def outro_prestador_auth(client, db_session):
    email = unique_email("prestador.outro")
    cadastrar_perfil(client, "/api/v1/prestadores/cadastro", email)
    token = login(client, email)
    prestador = db_session.scalar(select(Prestador).join(Usuario).where(Usuario.email == email))
    return {
        "email": email,
        "token": token,
        "prestador_id": str(prestador.id),
        "usuario_id": str(prestador.usuario_id),
    }


@pytest.fixture
def admin_auth(client, db_session):
    email = unique_email("admin")
    usuario = Usuario(
        nome="Admin Teste",
        email=email,
        telefone="11999999999",
        senha_hash=hash_password("Senha123"),
        tipo_usuario="admin",
        ativo=True,
    )
    db_session.add(usuario)
    db_session.commit()
    return {"email": email, "token": login(client, email), "usuario_id": str(usuario.id)}


@pytest.fixture
def categoria_id(db_session):
    categoria = CategoriaServico(nome=f"Eletrica {uuid4().hex[:6]}", descricao="Servicos eletricos", ativo=True)
    db_session.add(categoria)
    db_session.commit()
    return str(categoria.id)


@pytest.fixture
def servico_tabelado_id(client, admin_auth, categoria_id):
    response = client.post(
        "/api/v1/servicos-tabelados",
        headers=auth_headers(admin_auth["token"]),
        json={
            "categoria_id": categoria_id,
            "nome": "Trocar chuveiro",
            "descricao": "Troca completa de chuveiro eletrico",
            "preco_mao_obra": 180,
            "tempo_estimado_minutos": 90,
            "precisa_material": True,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def criar_solicitacao(client, cliente_auth, categoria_id, valor_mao_obra: float = 300) -> dict:
    response = client.post(
        "/api/v1/solicitacoes",
        headers=auth_headers(cliente_auth["token"]),
        json={
            "cliente_id": cliente_auth["cliente_id"],
            "tipo_servico": "personalizado",
            "categoria_id": categoria_id,
            "descricao_problema": "Instalar uma tomada nova na cozinha",
            "endereco": "Rua Teste 123",
            "urgencia": "normal",
            "melhor_horario": "manha",
            "observacoes": "Teste automatizado",
            "valor_mao_obra": valor_mao_obra,
            "tempo_estimado": 60,
            "tipo_material": "material_indefinido",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def aceitar_solicitacao(client, solicitacao_id: str, prestador_auth) -> dict:
    response = client.post(
        f"/api/v1/solicitacoes/{solicitacao_id}/aceitar",
        headers=auth_headers(prestador_auth["token"]),
    )
    assert response.status_code == 200, response.text
    return response.json()


def concluir_fluxo_servico(client, solicitacao_id: str, cliente_auth, prestador_auth) -> None:
    response = client.patch(
        f"/api/v1/solicitacoes/{solicitacao_id}/iniciar",
        headers=auth_headers(prestador_auth["token"]),
    )
    assert response.status_code == 200, response.text
    response = client.patch(
        f"/api/v1/solicitacoes/{solicitacao_id}/concluir",
        headers=auth_headers(prestador_auth["token"]),
    )
    assert response.status_code == 200, response.text
    response = client.patch(
        f"/api/v1/solicitacoes/{solicitacao_id}/confirmar-conclusao",
        headers=auth_headers(cliente_auth["token"]),
    )
    assert response.status_code == 200, response.text
