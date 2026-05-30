from conftest import auth_headers, criar_solicitacao


def test_cliente_faz_upload_e_lista_fotos_da_solicitacao(client, cliente_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id)
    headers = auth_headers(cliente_auth["token"])

    upload = client.post(
        f"/api/v1/solicitacoes/{solicitacao['id']}/fotos",
        headers={**headers, "Content-Type": "application/octet-stream"},
        params={
            "nome_original": "problema.png",
            "mime_type": "image/png",
            "tipo_foto": "problema",
            "descricao": "Foto inicial do problema",
        },
        content=b"conteudo-fake-de-imagem",
    )

    assert upload.status_code == 201, upload.text
    foto = upload.json()
    assert foto["solicitacao_id"] == solicitacao["id"]
    assert foto["nome_original"] == "problema.png"
    assert foto["mime_type"] == "image/png"
    assert foto["tipo_foto"] == "problema"

    listagem = client.get(f"/api/v1/solicitacoes/{solicitacao['id']}/fotos", headers=headers)

    assert listagem.status_code == 200
    assert len(listagem.json()) == 1
    assert listagem.json()[0]["id"] == foto["id"]


def test_upload_foto_rejeita_formato_invalido(client, cliente_auth, categoria_id):
    solicitacao = criar_solicitacao(client, cliente_auth, categoria_id)

    response = client.post(
        f"/api/v1/solicitacoes/{solicitacao['id']}/fotos",
        headers={
            **auth_headers(cliente_auth["token"]),
            "Content-Type": "application/octet-stream",
        },
        params={
            "nome_original": "problema.gif",
            "mime_type": "image/gif",
            "tipo_foto": "problema",
        },
        content=b"gif-fake",
    )

    assert response.status_code == 400
    assert "Formato de arquivo nao permitido" in response.json()["detail"]
