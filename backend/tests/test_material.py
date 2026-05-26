from conftest import aceitar_solicitacao, auth_headers, criar_solicitacao


def test_prestador_cria_material_e_cliente_aprova(client, cliente_auth, prestador_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id)
    aceitar_solicitacao(client, solicitacao["id"], prestador_auth)

    material = client.post(
        f"/api/v1/solicitacoes/{solicitacao['id']}/materiais",
        headers=auth_headers(prestador_auth["token"]),
        json={
            "descricao_material": "Tomada 20A e caixa de acabamento",
            "valor_estimado": 75,
            "necessita_aprovacao_cliente": True,
        },
    )
    assert material.status_code == 200, material.text
    assert material.json()["status_material"] == "aguardando_aprovacao_cliente"

    aprovar = client.patch(
        f"/api/v1/materiais/{material.json()['id']}/aprovar",
        headers=auth_headers(cliente_auth["token"]),
        json={"observacao_cliente": "Aprovado"},
    )
    assert aprovar.status_code == 200, aprovar.text
    assert aprovar.json()["status_material"] == "aprovado"


def test_prestador_nao_aceito_nao_cria_material(client, cliente_auth, outro_prestador_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id)

    response = client.post(
        f"/api/v1/solicitacoes/{solicitacao['id']}/materiais",
        headers=auth_headers(outro_prestador_auth["token"]),
        json={
            "descricao_material": "Tomada 20A",
            "valor_estimado": 75,
            "necessita_aprovacao_cliente": True,
        },
    )

    assert response.status_code == 401
