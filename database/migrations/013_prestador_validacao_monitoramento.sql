CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS prestador_validacao (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prestador_id UUID NOT NULL UNIQUE REFERENCES prestadores(id),
    status_validacao VARCHAR(40) NOT NULL DEFAULT 'pendente',
    documento_rg TEXT,
    documento_cpf TEXT,
    selfie_validacao TEXT,
    comprovante_endereco TEXT,
    observacao_admin TEXT,
    data_aprovacao TIMESTAMPTZ,
    aprovado_por_admin_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_usuario_id UUID,
    updated_by_usuario_id UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by_usuario_id UUID,
    CONSTRAINT prestador_validacao_status_check CHECK (
        status_validacao IN ('pendente', 'aprovado', 'rejeitado', 'em_analise')
    )
);

CREATE INDEX IF NOT EXISTS idx_prestador_validacao_status
    ON prestador_validacao(status_validacao);

INSERT INTO prestador_validacao (prestador_id, status_validacao, created_at, updated_at)
SELECT p.id, CASE WHEN p.ativo IS TRUE THEN 'aprovado' ELSE 'pendente' END, now(), now()
FROM prestadores p
WHERE NOT EXISTS (
    SELECT 1 FROM prestador_validacao pv WHERE pv.prestador_id = p.id
);

CREATE TABLE IF NOT EXISTS monitoramento_sistema (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tipo_alerta VARCHAR(80) NOT NULL,
    nivel_alerta VARCHAR(20) NOT NULL,
    mensagem TEXT NOT NULL,
    origem VARCHAR(120) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'ativo',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT monitoramento_nivel_check CHECK (nivel_alerta IN ('info', 'alerta', 'critico')),
    CONSTRAINT monitoramento_status_check CHECK (status IN ('ativo', 'resolvido', 'ignorado'))
);

CREATE INDEX IF NOT EXISTS idx_monitoramento_status
    ON monitoramento_sistema(status);

CREATE INDEX IF NOT EXISTS idx_monitoramento_nivel
    ON monitoramento_sistema(nivel_alerta);

CREATE INDEX IF NOT EXISTS idx_monitoramento_created_at
    ON monitoramento_sistema(created_at);
