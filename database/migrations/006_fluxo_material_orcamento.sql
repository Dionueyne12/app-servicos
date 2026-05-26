ALTER TABLE materiais_servico
    ADD COLUMN IF NOT EXISTS prestador_id UUID REFERENCES prestadores(id),
    ADD COLUMN IF NOT EXISTS descricao_material TEXT,
    ADD COLUMN IF NOT EXISTS necessita_aprovacao_cliente BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS aprovado_cliente BOOLEAN,
    ADD COLUMN IF NOT EXISTS data_aprovacao TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS observacao_cliente TEXT,
    ADD COLUMN IF NOT EXISTS status_material VARCHAR(40) NOT NULL DEFAULT 'pendente_avaliacao';

UPDATE materiais_servico
SET
    descricao_material = COALESCE(descricao_material, descricao),
    aprovado_cliente = COALESCE(aprovado_cliente, aprovado_pelo_cliente),
    data_aprovacao = COALESCE(data_aprovacao, aprovado_em)
WHERE descricao_material IS NULL OR aprovado_cliente IS NULL OR data_aprovacao IS NULL;

ALTER TABLE materiais_servico
    DROP CONSTRAINT IF EXISTS materiais_status_check;

ALTER TABLE materiais_servico
    ADD CONSTRAINT materiais_status_check CHECK (
        status_material IN (
            'pendente_avaliacao',
            'aguardando_aprovacao_cliente',
            'aprovado',
            'recusado',
            'alteracao_solicitada',
            'comprado_retirado',
            'cancelado'
        )
    );

CREATE INDEX IF NOT EXISTS idx_materiais_status
    ON materiais_servico(status_material);

CREATE INDEX IF NOT EXISTS idx_materiais_prestador
    ON materiais_servico(prestador_id);
