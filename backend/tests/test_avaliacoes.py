from conftest import aceitar_solicitacao, auth_headers, concluir_fluxo_servico, criar_solicitacao


def test_avaliacao_funciona_apos_conclusao(client, cliente_auth, prestador_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id)
    aceitar_solicitacao(client, solicitacao["id"], prestador_auth)
    concluir_fluxo_servico(client, solicitacao["id"], cliente_auth, prestador_auth)

    response = client.post(
        f"/api/v1/solicitacoes/{solicitacao['id']}/avaliar",
        headers=auth_headers(cliente_auth["token"]),
        json={"nota": 5, "comentario": "Servico excelente"},
    )

    assert response.status_code == 201, response.text
    assert response.json()["nota"] == 5


def test_avaliacao_antes_da_conclusao_falha(client, cliente_auth, prestador_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id)
    aceitar_solicitacao(client, solicitacao["id"], prestador_auth)

    response = client.post(
        f"/api/v1/solicitacoes/{solicitacao['id']}/avaliar",
        headers=auth_headers(cliente_auth["token"]),
        json={"nota": 5, "comentario": "Ainda nao concluiu"},
    )

    assert response.status_code == 400


def test_avaliacao_duplicada_falha(client, cliente_auth, prestador_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id)
    aceitar_solicitacao(client, solicitacao["id"], prestador_auth)
    concluir_fluxo_servico(client, solicitacao["id"], cliente_auth, prestador_auth)

    payload = {"nota": 5, "comentario": "Servico excelente"}
    primeira = client.post(
        f"/api/v1/solicitacoes/{solicitacao['id']}/avaliar",
        headers=auth_headers(cliente_auth["token"]),
        json=payload,
    )
    segunda = client.post(
        f"/api/v1/solicitacoes/{solicitacao['id']}/avaliar",
        headers=auth_headers(cliente_auth["token"]),
        json=payload,
    )

    assert primeira.status_code == 201
    assert segunda.status_code == 409
