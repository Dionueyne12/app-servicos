from conftest import cadastrar_perfil


def test_cadastro_e_login_funcionando(client):
    email = "cliente.auth@teste.com"
    cadastro = cadastrar_perfil(client, "/api/v1/clientes/cadastro", email)

    assert cadastro["email"] == email

    login = client.post("/api/v1/auth/login", json={"email": email, "senha": "Senha123"})

    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"
    assert login.json()["access_token"]


def test_login_com_senha_errada_falha(client):
    email = "cliente.senha.errada@teste.com"
    cadastrar_perfil(client, "/api/v1/clientes/cadastro", email)

    response = client.post("/api/v1/auth/login", json={"email": email, "senha": "SenhaErrada123"})

    assert response.status_code == 401


def test_jwt_protege_rota_privada(client):
    response = client.get("/api/v1/notificacoes")

    assert response.status_code == 401
