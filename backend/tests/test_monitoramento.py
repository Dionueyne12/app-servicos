from conftest import auth_headers
from services.monitoring_service import registrar_alerta_monitoramento


def test_admin_visualiza_monitoramento_de_erros(client, admin_auth, db_session):
    registrar_alerta_monitoramento(
        db_session,
        tipo_alerta="erro_rota",
        nivel_alerta="critico",
        mensagem="POST /api/v1/upload respondeu 500.",
        origem="teste_pytest",
    )

    response = client.get("/api/v1/admin/monitoramento", headers=auth_headers(admin_auth["token"]))

    assert response.status_code == 200
    body = response.json()
    assert body["saude"] == "critica"
    assert body["por_nivel"]["critico"] == 1
    assert body["erros_mais_frequentes"][0]["tipo_alerta"] == "erro_rota"


def test_monitoramento_admin_exige_autenticacao(client):
    response = client.get("/api/v1/admin/monitoramento")

    assert response.status_code == 401
