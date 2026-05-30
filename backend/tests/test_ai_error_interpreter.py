from sqlalchemy import func, select

from app.services import ai_error_interpreter
from conftest import auth_headers
from models import MonitoramentoSistema
from services.monitoring_service import registrar_alerta_monitoramento


def test_ia_desligada_nao_quebra_monitoramento(client, admin_auth, db_session, monkeypatch):
    monkeypatch.setenv("AI_ERROR_HELPER_ENABLED", "false")
    registrar_alerta_monitoramento(
        db_session,
        "erro_rota",
        "alerta",
        "GET /api/v1/solicitacoes respondeu 500.",
        "teste_ia_desligada",
    )

    response = client.get("/api/v1/admin/monitoramento", headers=auth_headers(admin_auth["token"]))

    assert response.status_code == 200
    analise = response.json()["analise_portugues_simples"]
    assert analise["pode_corrigir_automaticamente"] is False
    assert analise["observacao"] == "IA apenas sugeriu, não executou ação"


def test_ia_ligada_com_ollama_indisponivel_usa_fallback(monkeypatch):
    monkeypatch.setenv("AI_ERROR_HELPER_ENABLED", "true")

    def falhar_ollama(_context):
        raise TimeoutError("Ollama indisponivel")

    monkeypatch.setattr(ai_error_interpreter, "_call_ollama", falhar_ollama)

    result = ai_error_interpreter.interpret_error(
        {
            "mensagem_tecnica": "Falha ao listar fotos da solicitacao.",
            "origem": "/api/v1/solicitacoes/fotos",
            "rota_acao": "listar_fotos",
            "nivel_original": "alerta",
        }
    )

    assert result["gravidade_sugerida"] == "media"
    assert result["pode_corrigir_automaticamente"] is False
    assert "formato" in result["provavel_causa"].lower() or "upload" in result["provavel_causa"].lower()


def test_ia_nao_recebe_dados_sensiveis_completos(monkeypatch):
    monkeypatch.setenv("AI_ERROR_HELPER_ENABLED", "true")
    captured = {}

    def capturar_contexto(context):
        captured["context"] = context
        return {
            "explicacao_simples": "Erro explicado.",
            "provavel_causa": "Causa sugerida.",
            "gravidade_sugerida": "baixa",
            "acao_recomendada": "Verificar o caso manualmente.",
            "pode_corrigir_automaticamente": True,
            "observacao": "corrigir",
        }

    monkeypatch.setattr(ai_error_interpreter, "_call_ollama", capturar_contexto)

    result = ai_error_interpreter.interpret_error(
        {
            "mensagem_tecnica": "Usuario joao.silva@gmail.com telefone 62999991234 informou erro.",
            "origem": "cadastro",
            "rota_acao": "/api/v1/clientes/cadastro",
            "nivel_original": "alerta",
            "dados_seguros": {
                "senha": "Senha123",
                "token": "abc.def.ghi",
                "documento": "12345678900",
                "pagamento": {"cartao": "4111111111111111", "valor_total": 900},
                "email": "joao.silva@gmail.com",
                "telefone": "62999991234",
            },
        }
    )

    safe_context = str(captured["context"])
    assert "Senha123" not in safe_context
    assert "abc.def.ghi" not in safe_context
    assert "12345678900" not in safe_context
    assert "4111111111111111" not in safe_context
    assert "joao.silva@gmail.com" not in safe_context
    assert "62999991234" not in safe_context
    assert "jo***@gmail.com" in safe_context
    assert "(62) *****-1234" in safe_context
    assert result["pode_corrigir_automaticamente"] is False
    assert result["observacao"] == "IA apenas sugeriu, não executou ação"


def test_ia_nao_altera_banco_nem_executa_autocorrecao(client, admin_auth, db_session, monkeypatch):
    monkeypatch.setenv("AI_ERROR_HELPER_ENABLED", "true")
    registrar_alerta_monitoramento(
        db_session,
        "falha_postgresql",
        "critico",
        "Banco de dados indisponivel.",
        "teste_sem_autocorrecao",
    )
    total_antes = db_session.scalar(select(func.count()).select_from(MonitoramentoSistema))

    def resposta_perigosa(_context):
        return {
            "explicacao_simples": "Erro critico.",
            "provavel_causa": "Falha de banco.",
            "gravidade_sugerida": "critica",
            "acao_recomendada": "Apenas verificar manualmente.",
            "pode_corrigir_automaticamente": True,
            "observacao": "pode corrigir",
        }

    monkeypatch.setattr(ai_error_interpreter, "_call_ollama", resposta_perigosa)

    response = client.get("/api/v1/admin/monitoramento", headers=auth_headers(admin_auth["token"]))
    total_depois = db_session.scalar(select(func.count()).select_from(MonitoramentoSistema))

    assert response.status_code == 200
    assert total_depois == total_antes
    analise = response.json()["analise_portugues_simples"]
    assert analise["pode_corrigir_automaticamente"] is False
    assert analise["observacao"] == "IA apenas sugeriu, não executou ação"


def test_erro_da_ia_nao_quebra_rota_principal(client, admin_auth, db_session, monkeypatch):
    monkeypatch.setenv("AI_ERROR_HELPER_ENABLED", "true")
    registrar_alerta_monitoramento(
        db_session,
        "erro_rota",
        "critico",
        "POST /api/v1/upload respondeu 500.",
        "teste_ia_falha",
    )
    monkeypatch.setattr(ai_error_interpreter, "_call_ollama", lambda _context: (_ for _ in ()).throw(RuntimeError("boom")))

    response = client.get("/api/v1/admin/monitoramento", headers=auth_headers(admin_auth["token"]))

    assert response.status_code == 200
    assert response.json()["analise_portugues_simples"]["pode_corrigir_automaticamente"] is False


def test_monitoramento_funciona_com_ia_ligada(client, admin_auth, db_session, monkeypatch):
    monkeypatch.setenv("AI_ERROR_HELPER_ENABLED", "true")
    registrar_alerta_monitoramento(
        db_session,
        "erro_rota",
        "alerta",
        "Cliente tentou abrir fotos, mas nenhuma imagem foi encontrada.",
        "teste_ia_ligada",
    )
    monkeypatch.setattr(
        ai_error_interpreter,
        "_call_ollama",
        lambda _context: {
            "explicacao_simples": "O cliente tentou abrir fotos da solicitacao, mas nao havia imagens cadastradas.",
            "provavel_causa": "A solicitacao pode nao ter recebido fotos ou o upload falhou.",
            "gravidade_sugerida": "baixa",
            "acao_recomendada": "Verificar se o cliente realmente enviou foto.",
            "pode_corrigir_automaticamente": False,
            "observacao": "somente sugestao",
        },
    )

    response = client.get("/api/v1/admin/monitoramento", headers=auth_headers(admin_auth["token"]))

    assert response.status_code == 200
    analise = response.json()["analise_portugues_simples"]
    assert "fotos" in analise["explicacao_simples"]
    assert analise["gravidade_sugerida"] == "baixa"
    assert analise["pode_corrigir_automaticamente"] is False
