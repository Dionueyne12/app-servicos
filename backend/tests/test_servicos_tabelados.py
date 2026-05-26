from conftest import auth_headers


def test_admin_cria_lista_edita_e_desativa_servico_tabelado(client, admin_auth, categoria_id):
    headers = auth_headers(admin_auth["token"])

    criar = client.post(
        "/api/v1/servicos-tabelados",
        headers=headers,
        json={
            "categoria_id": categoria_id,
            "nome": "Trocar tomada",
            "descricao": "Troca segura de tomada eletrica",
            "preco_mao_obra": 120,
            "tempo_estimado_minutos": 45,
            "precisa_material": True,
        },
    )
    assert criar.status_code == 201, criar.text
    servico_id = criar.json()["id"]

    listar = client.get("/api/v1/servicos-tabelados")
    assert listar.status_code == 200
    assert listar.json()["meta"]["total"] == 1

    editar = client.put(
        f"/api/v1/servicos-tabelados/{servico_id}",
        headers=headers,
        json={"preco_mao_obra": 140, "tempo_estimado_minutos": 60},
    )
    assert editar.status_code == 200
    assert editar.json()["preco_mao_obra"] == 140

    desativar = client.patch(f"/api/v1/servicos-tabelados/{servico_id}/desativar", headers=headers)
    assert desativar.status_code == 200
    assert desativar.json()["ativo"] is False


def test_cliente_nao_cria_servico_tabelado(client, cliente_auth, categoria_id):
    response = client.post(
        "/api/v1/servicos-tabelados",
        headers=auth_headers(cliente_auth["token"]),
        json={
            "categoria_id": categoria_id,
            "nome": "Trocar resistencia",
            "descricao": "Troca de resistencia do chuveiro",
            "preco_mao_obra": 100,
            "tempo_estimado_minutos": 40,
            "precisa_material": True,
        },
    )

    assert response.status_code == 403
