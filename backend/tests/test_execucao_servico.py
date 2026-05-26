from conftest import aceitar_solicitacao, auth_headers, concluir_fluxo_servico, criar_solicitacao


def test_servico_inicia_conclui_e_cliente_confirma(client, cliente_auth, prestador_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id)
    aceitar_solicitacao(client, solicitacao["id"], prestador_auth)

    concluir_fluxo_servico(client, solicitacao["id"], cliente_auth, prestador_auth)

    detalhe = client.get(
        f"/api/v1/solicitacoes/{solicitacao['id']}",
        headers=auth_headers(cliente_auth["token"]),
    )
    assert detalhe.status_code == 200
    assert detalhe.json()["status"] == "concluido"


def test_cliente_nao_inicia_servico(client, cliente_auth, prestador_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id)
    aceitar_solicitacao(client, solicitacao["id"], prestador_auth)

    response = client.patch(
        f"/api/v1/solicitacoes/{solicitacao['id']}/iniciar",
        headers=auth_headers(cliente_auth["token"]),
    )

    assert response.status_code == 401


def test_nao_conclui_sem_iniciar(client, cliente_auth, prestador_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id)
    aceitar_solicitacao(client, solicitacao["id"], prestador_auth)

    response = client.patch(
        f"/api/v1/solicitacoes/{solicitacao['id']}/concluir",
        headers=auth_headers(prestador_auth["token"]),
    )

    assert response.status_code == 400
