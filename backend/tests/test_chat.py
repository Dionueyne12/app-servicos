from conftest import aceitar_solicitacao, auth_headers, criar_solicitacao


def test_cliente_e_prestador_conversam_no_chat(client, cliente_auth, prestador_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id)
    aceitar_solicitacao(client, solicitacao["id"], prestador_auth)

    mensagem_cliente = client.post(
        f"/api/v1/solicitacoes/{solicitacao['id']}/mensagens",
        headers=auth_headers(cliente_auth["token"]),
        json={"tipo_mensagem": "texto", "mensagem": "Pode vir pela manha?"},
    )
    assert mensagem_cliente.status_code == 201, mensagem_cliente.text

    resposta_prestador = client.post(
        f"/api/v1/solicitacoes/{solicitacao['id']}/mensagens",
        headers=auth_headers(prestador_auth["token"]),
        json={"tipo_mensagem": "texto", "mensagem": "Sim, posso chegar as 9h."},
    )
    assert resposta_prestador.status_code == 201, resposta_prestador.text

    listar = client.get(
        f"/api/v1/solicitacoes/{solicitacao['id']}/mensagens",
        headers=auth_headers(cliente_auth["token"]),
    )
    assert listar.status_code == 200
    assert listar.json()["meta"]["total"] >= 2


def test_chat_bloqueia_terceiros(client, cliente_auth, prestador_auth, outro_prestador_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id)
    aceitar_solicitacao(client, solicitacao["id"], prestador_auth)

    response = client.post(
        f"/api/v1/solicitacoes/{solicitacao['id']}/mensagens",
        headers=auth_headers(outro_prestador_auth["token"]),
        json={"tipo_mensagem": "texto", "mensagem": "Mensagem indevida"},
    )

    assert response.status_code == 401
