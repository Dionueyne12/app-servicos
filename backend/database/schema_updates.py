from sqlalchemy import text
from sqlalchemy.engine import Engine


def ensure_schema_updates(engine: Engine) -> None:
    print("[DB] aplicando atualizacoes seguras de schema")
    statements = [
        "ALTER TABLE servicos_tabelados ADD COLUMN IF NOT EXISTS possui_garantia BOOLEAN NOT NULL DEFAULT FALSE",
        "ALTER TABLE servicos_tabelados ADD COLUMN IF NOT EXISTS dias_garantia INTEGER NOT NULL DEFAULT 0",
        (
            "ALTER TABLE servicos_tabelados "
            "ADD COLUMN IF NOT EXISTS percentual_retencao_garantia NUMERIC(5, 2) NOT NULL DEFAULT 0"
        ),
        (
            "ALTER TABLE servicos_tabelados "
            "ADD COLUMN IF NOT EXISTS dias_liberacao_primeiro_repasse INTEGER NOT NULL DEFAULT 0"
        ),
        "ALTER TABLE servicos_tabelados ADD COLUMN IF NOT EXISTS descricao_garantia TEXT",
        "ALTER TABLE servicos_tabelados ADD COLUMN IF NOT EXISTS regras_garantia TEXT",
        "ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS garantias_acionadas INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS garantias_resolvidas INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS garantias_nao_atendidas INTEGER NOT NULL DEFAULT 0",
        (
            "ALTER TABLE prestadores "
            "ADD COLUMN IF NOT EXISTS tempo_medio_resolucao_garantia_horas NUMERIC(10, 2) NOT NULL DEFAULT 0"
        ),
        "ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS reincidencia_garantia INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS aceita_retencao_garantia BOOLEAN NOT NULL DEFAULT FALSE",
        "ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS data_aceite_termos TIMESTAMP WITH TIME ZONE",
        "ALTER TABLE prestadores ADD COLUMN IF NOT EXISTS versao_termos VARCHAR(30)",
        "ALTER TABLE repasses DROP CONSTRAINT IF EXISTS repasses_status_check",
        (
            "ALTER TABLE repasses ADD CONSTRAINT repasses_status_check CHECK "
            "(status_repasse IN ('pendente', 'simulado', 'aprovado', 'cancelado', 'retido_garantia'))"
        ),
        "ALTER TABLE repasses DROP CONSTRAINT IF EXISTS repasses_tipo_check",
        (
            "ALTER TABLE repasses ADD CONSTRAINT repasses_tipo_check CHECK "
            "(tipo_repasse IN ('prestador', 'empresa', 'plataforma', 'garantia'))"
        ),
    ]
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
    print("[DB] atualizacoes seguras de schema aplicadas")
