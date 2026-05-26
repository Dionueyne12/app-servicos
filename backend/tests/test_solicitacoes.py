from conftest import auth_headers, criar_solicitacao


def test_cliente_cria_solicitacao(client, cliente_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id)

    assert solicitacao["cliente_id"] == cliente_auth["cliente_id"]
    assert solicitacao["status"] == "aguardando_prestador"
    assert solicitacao["material"]["tipo_material"] == "material_indefinido"


def test_criar_solicitacao_sem_token_retorna_401(client, categoria_id):
    response = client.post(
        "/api/v1/solicitacoes",
        json={
            "cliente_id": "00000000-0000-0000-0000-000000000001",
            "tipo_servico": "personalizado",
            "categoria_id": categoria_id,
            "descricao_problema": "Instalar uma tomada nova na cozinha",
            "endereco": "Rua Teste 123",
            "urgencia": "normal",
            "valor_mao_obra": 300,
            "tempo_estimado": 60,
            "tipo_material": "material_indefinido",
        },
    )

    assert response.status_code == 401


def test_criar_solicitacao_sem_tipo_material_falha(client, cliente_auth, categoria_id):
    payload = {
        "cliente_id": cliente_auth["cliente_id"],
        "tipo_servico": "personalizado",
        "categoria_id": categoria_id,
        "descricao_problema": "Instalar uma tomada nova na cozinha",
        "endereco": "Rua Teste 123",
        "urgencia": "normal",
        "valor_mao_obra": 300,
        "tempo_estimado": 60,
    }

    response = client.post("/api/v1/solicitacoes", headers=auth_headers(cliente_auth["token"]), json=payload)

    assert response.status_code == 422
