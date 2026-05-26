ALTER TABLE solicitacoes_servico
    ADD COLUMN IF NOT EXISTS data_inicio TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS data_conclusao_prestador TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS data_confirmacao_cliente TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS observacao_problema TEXT;

UPDATE solicitacoes_servico
SET
    data_inicio = COALESCE(data_inicio, iniciado_em),
    data_conclusao_prestador = COALESCE(data_conclusao_prestador, concluido_em)
WHERE data_inicio IS NULL OR data_conclusao_prestador IS NULL;
