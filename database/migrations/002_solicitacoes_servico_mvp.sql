ALTER TABLE solicitacoes_servico
    ADD COLUMN IF NOT EXISTS categoria_id UUID REFERENCES categorias_servico(id),
    ADD COLUMN IF NOT EXISTS melhor_horario VARCHAR(120),
    ADD COLUMN IF NOT EXISTS observacoes TEXT;

CREATE INDEX IF NOT EXISTS idx_solicitacoes_categoria
    ON solicitacoes_servico(categoria_id);

ALTER TABLE materiais_servico
    DROP CONSTRAINT IF EXISTS materiais_escolha_check;

ALTER TABLE materiais_servico
    ADD CONSTRAINT materiais_escolha_check CHECK (
        escolha_cliente IN (
            'cliente_fornece_material',
            'prestador_providencia_material',
            'material_indefinido'
        )
    );
