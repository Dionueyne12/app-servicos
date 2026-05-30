from sqlalchemy import text

from conftest import engine
from database.schema_updates import ensure_schema_updates


def test_autocorrecao_schema_recria_colunas_seguras():
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE servicos_tabelados DROP COLUMN IF EXISTS descricao_garantia"))

    ensure_schema_updates(engine)
    ensure_schema_updates(engine)

    with engine.connect() as connection:
        exists = connection.execute(
            text(
                """
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'servicos_tabelados'
                  AND column_name = 'descricao_garantia'
                """
            )
        ).scalar()

    assert exists == 1
