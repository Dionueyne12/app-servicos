from conftest import auth_headers


def test_admin_acessa_dashboard_e_relatorios(client, admin_auth):
    headers = auth_headers(admin_auth["token"])

    dashboard = client.get("/api/v1/admin/dashboard", headers=headers)
    financeiro = client.get("/api/v1/admin/relatorios/financeiro", headers=headers)
    repasses = client.get("/api/v1/admin/relatorios/repasses", headers=headers)

    assert dashboard.status_code == 200
    assert financeiro.status_code == 200
    assert repasses.status_code == 200


def test_cliente_e_prestador_sao_bloqueados_em_rotas_admin(client, cliente_auth, prestador_auth):
    cliente = client.get("/api/v1/admin/dashboard", headers=auth_headers(cliente_auth["token"]))
    prestador = client.get("/api/v1/admin/dashboard", headers=auth_headers(prestador_auth["token"]))
    sem_token = client.get("/api/v1/admin/dashboard")

    assert cliente.status_code == 403
    assert prestador.status_code == 403
    assert sem_token.status_code == 401
