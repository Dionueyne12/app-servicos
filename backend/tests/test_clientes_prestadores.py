from conftest import cadastrar_perfil, unique_email


def test_cadastro_cliente(client):
    email = unique_email("cliente.cadastro")

    response = cadastrar_perfil(client, "/api/v1/clientes/cadastro", email)

    assert response["tipo_usuario"] == "cliente"
    assert response["email"] == email


def test_cadastro_prestador(client):
    email = unique_email("prestador.cadastro")

    response = cadastrar_perfil(client, "/api/v1/prestadores/cadastro", email)

    assert response["tipo_usuario"] == "prestador"
    assert response["email"] == email


def test_email_duplicado_falha(client):
    email = unique_email("duplicado")
    cadastrar_perfil(client, "/api/v1/clientes/cadastro", email)

    response = client.post(
        "/api/v1/prestadores/cadastro",
        json={
            "nome": "Usuario Teste",
            "email": email,
            "telefone": "11988887777",
            "senha": "Senha123",
            "documento": "12345678900",
            "endereco": "Rua Teste, 123",
            "bairro": "Centro",
            "cidade": "Sao Paulo",
            "estado": "SP",
        },
    )

    assert response.status_code == 409
