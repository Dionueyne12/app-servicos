import json
import logging
import os
import re
import socket
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any


logger = logging.getLogger("ai.error_interpreter")

DEFAULT_OBSERVACAO = "IA apenas sugeriu, não executou ação"
DEFAULT_TIMEOUT_SECONDS = 2
SENSITIVE_KEYS = {
    "senha",
    "password",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "documento",
    "documento_rg",
    "documento_cpf",
    "cpf",
    "cnpj",
    "cartao",
    "card",
    "pagamento",
    "payment",
    "comprovante_pagamento",
    "valor",
    "valor_total",
    "valor_mao_obra",
    "valor_material",
    "endereco",
    "endereco_principal",
}
ALLOWED_GRAVIDADES = {"baixa", "media", "critica"}


def interpret_error(error_context: dict[str, Any]) -> dict[str, Any]:
    safe_context = sanitize_error_context(error_context)
    fallback = _fallback_interpretation(safe_context)

    if not _ai_enabled():
        return fallback

    if os.getenv("AI_PROVIDER", "ollama").strip().lower() != "ollama":
        logger.warning("ai_error_interpreter_unsupported_provider")
        return fallback

    try:
        ai_response = _call_ollama(safe_context)
        return _normalize_ai_response(ai_response, fallback)
    except Exception as exc:
        logger.warning("ai_error_interpreter_failed: %s", exc)
        return fallback


def sanitize_error_context(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            normalized_key = key_text.lower()
            if _is_sensitive_key(normalized_key):
                sanitized[key_text] = "[removido]"
            else:
                sanitized[key_text] = sanitize_error_context(item)
        return sanitized

    if isinstance(value, list):
        return [sanitize_error_context(item) for item in value[:20]]

    if isinstance(value, tuple):
        return [sanitize_error_context(item) for item in value[:20]]

    if isinstance(value, str):
        return _mask_sensitive_text(value)

    return value


def _ai_enabled() -> bool:
    return os.getenv("AI_ERROR_HELPER_ENABLED", "false").strip().lower() in {"1", "true", "sim", "yes", "on"}


def _is_sensitive_key(key: str) -> bool:
    return any(sensitive in key for sensitive in SENSITIVE_KEYS)


def _mask_sensitive_text(value: str) -> str:
    masked = re.sub(r"([A-Za-z0-9._%+-]{2})[A-Za-z0-9._%+-]*(@[A-Za-z0-9.-]+\.[A-Za-z]{2,})", r"\1***\2", value)
    masked = re.sub(r"\b(\d{2})(\d{5})(\d{4})\b", r"(\1) *****-\3", masked)
    masked = re.sub(r"\b(\d{3})\d{3}\d{3}(\d{2})\b", r"\1******\2", masked)
    return masked


def _fallback_interpretation(context: dict[str, Any]) -> dict[str, Any]:
    mensagem = str(context.get("mensagem_tecnica") or context.get("mensagem") or "Erro registrado no sistema.")
    origem = str(context.get("origem") or "origem nao informada")
    rota = str(context.get("rota_acao") or context.get("rota") or origem)
    nivel = str(context.get("nivel_original") or context.get("nivel_alerta") or "").lower()
    gravidade = _gravidade_por_regra(mensagem, nivel)

    if "foto" in mensagem.lower() or "upload" in mensagem.lower():
        causa = "Pode ter ocorrido falha no envio, formato invalido ou arquivo sem vinculo com a solicitacao."
        acao = "Verificar se a solicitacao existe, se o arquivo foi enviado e se o formato e permitido."
    elif "database" in mensagem.lower() or "postgres" in mensagem.lower() or "banco" in mensagem.lower():
        causa = "Pode existir instabilidade de banco de dados ou problema temporario de conexao."
        acao = "Conferir a conexao com o PostgreSQL e os alertas recentes antes de tentar qualquer ajuste manual."
    elif "unauthorized" in mensagem.lower() or "nao autorizado" in mensagem.lower():
        causa = "O usuario pode nao ter permissao para acessar a rota ou executar a acao."
        acao = "Confirmar o perfil do usuario e validar se a rota exige autenticacao ou permissao especifica."
    else:
        causa = "A causa exata precisa ser confirmada nos logs tecnicos e no contexto da rota."
        acao = "Revisar o alerta, checar logs relacionados e acompanhar se o erro se repete."

    return {
        "explicacao_simples": f"O sistema registrou um problema em {rota}. Mensagem: {mensagem}",
        "provavel_causa": causa,
        "gravidade_sugerida": gravidade,
        "acao_recomendada": acao,
        "pode_corrigir_automaticamente": False,
        "observacao": DEFAULT_OBSERVACAO,
    }


def _gravidade_por_regra(mensagem: str, nivel: str) -> str:
    texto = f"{mensagem} {nivel}".lower()
    if "critico" in texto or "500" in texto or "indisponivel" in texto or "postgres" in texto:
        return "critica"
    if "alerta" in texto or "falha" in texto or "erro" in texto or "401" in texto or "403" in texto:
        return "media"
    return "baixa"


def _call_ollama(safe_context: dict[str, Any]) -> dict[str, Any]:
    prompt = _build_prompt(safe_context)
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    payload = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.1},
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    timeout = float(os.getenv("AI_ERROR_HELPER_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)))
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8"))
    raw_response = body.get("response", "{}")
    if isinstance(raw_response, str):
        return json.loads(raw_response)
    if isinstance(raw_response, dict):
        return raw_response
    return {}


def _build_prompt(safe_context: dict[str, Any]) -> str:
    return (
        "Voce e um auxiliar de monitoramento para um app de prestacao de servicos. "
        "Explique o erro em portugues simples para um admin. "
        "Nao decida nada, nao corrija nada, nao recomende alteracao automatica de dados criticos. "
        "Responda somente JSON com as chaves: explicacao_simples, provavel_causa, "
        "gravidade_sugerida, acao_recomendada, pode_corrigir_automaticamente, observacao. "
        "A gravidade deve ser baixa, media ou critica. "
        "pode_corrigir_automaticamente deve ser false. "
        f"Contexto seguro: {json.dumps(safe_context, ensure_ascii=False, default=str)}"
    )


def _normalize_ai_response(response: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        "explicacao_simples": _safe_text(response.get("explicacao_simples"), fallback["explicacao_simples"]),
        "provavel_causa": _safe_text(response.get("provavel_causa"), fallback["provavel_causa"]),
        "gravidade_sugerida": str(response.get("gravidade_sugerida") or fallback["gravidade_sugerida"]).lower(),
        "acao_recomendada": _safe_text(response.get("acao_recomendada"), fallback["acao_recomendada"]),
        "pode_corrigir_automaticamente": False,
        "observacao": DEFAULT_OBSERVACAO,
    }
    if normalized["gravidade_sugerida"] not in ALLOWED_GRAVIDADES:
        normalized["gravidade_sugerida"] = fallback["gravidade_sugerida"]
    return normalized


def _safe_text(value: Any, default: str) -> str:
    if not isinstance(value, str) or not value.strip():
        return default
    return sanitize_error_context(value.strip()[:1000])


def build_error_context(
    mensagem_tecnica: str,
    origem: str,
    rota_acao: str,
    nivel_original: str,
    usuario_id: str | None = None,
    solicitacao_id: str | None = None,
    dados_seguros: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "mensagem_tecnica": mensagem_tecnica,
        "origem": origem,
        "rota_acao": rota_acao,
        "usuario_id": usuario_id,
        "solicitacao_id": solicitacao_id,
        "dados_seguros": dados_seguros or {},
        "data_hora": datetime.now(timezone.utc).isoformat(),
        "nivel_original": nivel_original,
    }
