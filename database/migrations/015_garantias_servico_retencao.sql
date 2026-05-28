ALTER TABLE servicos_tabelados
    ADD COLUMN IF NOT EXISTS possui_garantia BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS dias_garantia INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS percentual_retencao_garantia NUMERIC(5, 2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS dias_liberacao_primeiro_repasse INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS descricao_garantia TEXT,
    ADD COLUMN IF NOT EXISTS regras_garantia TEXT;

ALTER TABLE prestadores
    ADD COLUMN IF NOT EXISTS garantias_acionadas INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS garantias_resolvidas INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS garantias_nao_atendidas INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS tempo_medio_resolucao_garantia_horas NUMERIC(10, 2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS reincidencia_garantia INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS aceita_retencao_garantia BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS data_aceite_termos TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS versao_termos VARCHAR(30);

CREATE TABLE IF NOT EXISTS garantias_servico (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solicitacao_id UUID NOT NULL UNIQUE REFERENCES solicitacoes_servico(id),
    prestador_id UUID NOT NULL REFERENCES prestadores(id),
    cliente_id UUID NOT NULL REFERENCES clientes(id),
    servico_tabelado_id UUID REFERENCES servicos_tabelados(id),
    pagamento_simulado_id UUID REFERENCES pagamentos_simulados(id),
    pagamento_id UUID REFERENCES pagamentos(id),
    data_inicio_garantia TIMESTAMP WITH TIME ZONE NOT NULL,
    data_fim_garantia TIMESTAMP WITH TIME ZONE NOT NULL,
    status_garantia VARCHAR(40) NOT NULL DEFAULT 'ativa',
    valor_retido NUMERIC(10, 2) NOT NULL DEFAULT 0,
    valor_liberado_inicial NUMERIC(10, 2) NOT NULL DEFAULT 0,
    percentual_retencao NUMERIC(5, 2) NOT NULL DEFAULT 0,
    dias_garantia INTEGER NOT NULL DEFAULT 0,
    dias_liberacao_primeiro_repasse INTEGER NOT NULL DEFAULT 0,
    descricao_problema TEXT,
    observacao_cliente TEXT,
    observacao_admin TEXT,
    fotos TEXT,
    bloqueio_repasse BOOLEAN NOT NULL DEFAULT FALSE,
    procedente BOOLEAN,
    data_acionamento TIMESTAMP WITH TIME ZONE,
    data_resolucao TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    created_by_usuario_id UUID,
    updated_by_usuario_id UUID,
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by_usuario_id UUID
);

CREATE INDEX IF NOT EXISTS ix_garantias_servico_status ON garantias_servico(status_garantia);
CREATE INDEX IF NOT EXISTS ix_garantias_servico_prestador ON garantias_servico(prestador_id);
CREATE INDEX IF NOT EXISTS ix_garantias_servico_cliente ON garantias_servico(cliente_id);
