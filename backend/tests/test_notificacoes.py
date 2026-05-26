from conftest import aceitar_solicitacao, auth_headers, criar_solicitacao


def test_notificacao_criada_quando_servico_e_aceito(client, cliente_auth, prestador_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id)
    aceitar_solicitacao(client, solicitacao["id"], prestador_auth)

    response = client.get("/api/v1/notificacoes", headers=auth_headers(cliente_auth["token"]))

    assert response.status_code == 200
    assert response.json()["meta"]["total"] >= 1
    tipos = [item["tipo_notificacao"] for item in response.json()["items"]]
    assert "servico_aceito" in tipos


def test_marcar_notificacao_como_lida(client, cliente_auth, prestador_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id)
    aceitar_solicitacao(client, solicitacao["id"], prestador_auth)
    notificacoes = client.get("/api/v1/notificacoes", headers=auth_headers(cliente_auth["token"])).json()
    notificacao_id = notificacoes["items"][0]["id"]

    response = client.patch(
        f"/api/v1/notificacoes/{notificacao_id}/marcar-lida",
        headers=auth_headers(cliente_auth["token"]),
    )

    assert response.status_code == 200
    assert response.json()["lida"] is True


def test_rota_notificacoes_exige_token(client):
    response = client.get("/api/v1/notificacoes")

    assert response.status_code == 401
