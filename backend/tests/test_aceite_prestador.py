from conftest import aceitar_solicitacao, auth_headers, criar_solicitacao


def test_prestador_aceita_solicitacao(client, cliente_auth, prestador_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id)

    aceita = aceitar_solicitacao(client, solicitacao["id"], prestador_auth)

    assert aceita["status"] == "aceito"
    assert aceita["prestador_id"] == prestador_auth["prestador_id"]


def test_aceite_sem_token_falha(client, cliente_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id)

    response = client.post(f"/api/v1/solicitacoes/{solicitacao['id']}/aceitar")

    assert response.status_code == 401


def test_cliente_nao_aceita_solicitacao(client, cliente_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id)

    response = client.post(
        f"/api/v1/solicitacoes/{solicitacao['id']}/aceitar",
        headers=auth_headers(cliente_auth["token"]),
    )

    assert response.status_code == 401


def test_aceite_duplicado_falha(client, cliente_auth, prestador_auth, outro_prestador_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id)
    aceitar_solicitacao(client, solicitacao["id"], prestador_auth)

    response = client.post(
        f"/api/v1/solicitacoes/{solicitacao['id']}/aceitar",
        headers=auth_headers(outro_prestador_auth["token"]),
    )

    assert response.status_code == 400


def test_prestador_lista_meus_servicos(client, cliente_auth, prestador_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id)
    aceitar_solicitacao(client, solicitacao["id"], prestador_auth)

    response = client.get("/api/v1/prestadores/meus-servicos", headers=auth_headers(prestador_auth["token"]))

    assert response.status_code == 200
    assert response.json()["meta"]["total"] == 1
