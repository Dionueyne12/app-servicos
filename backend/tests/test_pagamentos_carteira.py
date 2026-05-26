from conftest import aceitar_solicitacao, auth_headers, concluir_fluxo_servico, criar_solicitacao


def test_pagamento_simulado_carteira_e_repasse(client, cliente_auth, prestador_auth, admin_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id, valor_mao_obra=300)
    aceitar_solicitacao(client, solicitacao["id"], prestador_auth)
    concluir_fluxo_servico(client, solicitacao["id"], cliente_auth, prestador_auth)

    pagamento = client.post(
        "/api/v1/pagamentos/simular",
        headers=auth_headers(cliente_auth["token"]),
        json={
            "solicitacao_id": solicitacao["id"],
            "metodo_pagamento": "pix",
            "comprovante_pagamento": "comprovante-simulado.pdf",
        },
    )
    assert pagamento.status_code == 201, pagamento.text
    data = pagamento.json()
    assert data["valor_total"] == 300
    assert data["valor_comissao_plataforma"] == 45
    assert data["valor_prestador"] == 255

    aprovado = client.patch(
        f"/api/v1/pagamentos/{data['id']}/aprovar",
        headers=auth_headers(admin_auth["token"]),
    )
    assert aprovado.status_code == 200
    assert aprovado.json()["status_pagamento"] == "aguardando_repasse"

    liberado = client.patch(
        f"/api/v1/pagamentos/{data['id']}/liberar-repasse",
        headers=auth_headers(admin_auth["token"]),
    )
    assert liberado.status_code == 200
    assert liberado.json()["status_pagamento"] == "repasse_liberado"

    saldo = client.get("/api/v1/carteira/meu-saldo", headers=auth_headers(prestador_auth["token"]))
    assert saldo.status_code == 200
    assert saldo.json()["saldo_disponivel"] == 255


def test_cliente_nao_acessa_carteira_de_outro(client, cliente_auth, prestador_auth):
    response = client.get(
        "/api/v1/carteira/meu-saldo",
        headers=auth_headers(cliente_auth["token"]),
        params={"usuario_id": prestador_auth["usuario_id"]},
    )

    assert response.status_code == 403


def test_admin_consegue_listar_pagamentos(client, cliente_auth, prestador_auth, admin_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id, valor_mao_obra=200)
    aceitar_solicitacao(client, solicitacao["id"], prestador_auth)

    pagamento = client.post(
        "/api/v1/pagamentos/simular",
        headers=auth_headers(cliente_auth["token"]),
        json={"solicitacao_id": solicitacao["id"], "metodo_pagamento": "pix"},
    )
    assert pagamento.status_code == 201

    response = client.get("/api/v1/pagamentos", headers=auth_headers(admin_auth["token"]))

    assert response.status_code == 200
    assert response.json()["meta"]["total"] == 1
