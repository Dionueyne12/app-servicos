ALTER TABLE avaliacoes
    ADD COLUMN IF NOT EXISTS tipo_avaliacao VARCHAR(40),
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS created_by_usuario_id UUID REFERENCES usuarios(id),
    ADD COLUMN IF NOT EXISTS updated_by_usuario_id UUID REFERENCES usuarios(id),
    ADD COLUMN IF NOT EXISTS deleted_by_usuario_id UUID REFERENCES usuarios(id);

UPDATE avaliacoes a
SET tipo_avaliacao = CASE
    WHEN avaliador.tipo_usuario = 'cliente' THEN 'cliente_avalia_prestador'
    WHEN avaliador.tipo_usuario = 'prestador' THEN 'prestador_avalia_cliente'
    ELSE 'cliente_avalia_prestador'
END
FROM usuarios avaliador
WHERE avaliador.id = a.avaliador_usuario_id
  AND a.tipo_avaliacao IS NULL;

ALTER TABLE avaliacoes
    ALTER COLUMN tipo_avaliacao SET NOT NULL;

ALTER TABLE avaliacoes
    DROP CONSTRAINT IF EXISTS avaliacoes_tipo_check;

ALTER TABLE avaliacoes
    ADD CONSTRAINT avaliacoes_tipo_check CHECK (
        tipo_avaliacao IN ('cliente_avalia_prestador', 'prestador_avalia_cliente')
    );

ALTER TABLE avaliacoes
    DROP CONSTRAINT IF EXISTS avaliacoes_nota_check;

ALTER TABLE avaliacoes
    ADD CONSTRAINT avaliacoes_nota_check CHECK (nota BETWEEN 1 AND 5);

ALTER TABLE avaliacoes
    DROP CONSTRAINT IF EXISTS avaliacoes_unica_por_avaliador;

CREATE UNIQUE INDEX IF NOT EXISTS ux_avaliacoes_solicitacao_tipo_ativa
    ON avaliacoes(solicitacao_id, tipo_avaliacao)
    WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_avaliacoes_avaliado_tipo
    ON avaliacoes(avaliado_usuario_id, tipo_avaliacao)
    WHERE deleted_at IS NULL;

ALTER TABLE clientes
    ADD COLUMN IF NOT EXISTS media_notas NUMERIC(3, 2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS total_avaliacoes INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS total_servicos_solicitados INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS tempo_medio_conclusao_minutos NUMERIC(10, 2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS quantidade_problemas INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS taxa_cancelamento NUMERIC(5, 2) NOT NULL DEFAULT 0;

ALTER TABLE prestadores
    ADD COLUMN IF NOT EXISTS media_notas NUMERIC(3, 2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS total_avaliacoes INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS total_servicos_concluidos INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS tempo_medio_conclusao_minutos NUMERIC(10, 2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS quantidade_problemas INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS taxa_cancelamento NUMERIC(5, 2) NOT NULL DEFAULT 0;
