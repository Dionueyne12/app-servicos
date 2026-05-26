CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS pagamentos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solicitacao_id UUID NOT NULL UNIQUE REFERENCES solicitacoes_servico(id),
    cliente_id UUID NOT NULL REFERENCES clientes(id),
    prestador_id UUID NOT NULL REFERENCES prestadores(id),
    valor_mao_obra NUMERIC(10, 2) NOT NULL DEFAULT 0,
    valor_material NUMERIC(10, 2) NOT NULL DEFAULT 0,
    valor_total NUMERIC(10, 2) NOT NULL DEFAULT 0,
    valor_comissao_plataforma NUMERIC(10, 2) NOT NULL DEFAULT 0,
    valor_prestador NUMERIC(10, 2) NOT NULL DEFAULT 0,
    valor_fornecedor NUMERIC(10, 2) NOT NULL DEFAULT 0,
    status_pagamento VARCHAR(40) NOT NULL DEFAULT 'aguardando_pagamento',
    metodo_pagamento VARCHAR(40) NOT NULL,
    data_pagamento TIMESTAMPTZ,
    data_liberacao_repasse TIMESTAMPTZ,
    comprovante_pagamento TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_usuario_id UUID,
    updated_by_usuario_id UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by_usuario_id UUID,
    CONSTRAINT pagamentos_status_check CHECK (
        status_pagamento IN (
            'aguardando_pagamento',
            'pagamento_aprovado',
            'pagamento_recusado',
            'aguardando_repasse',
            'repasse_liberado',
            'cancelado',
            'reembolso',
            'em_analise'
        )
    ),
    CONSTRAINT pagamentos_metodo_check CHECK (
        metodo_pagamento IN (
            'pix',
            'cartao',
            'boleto',
            'carteira_interna',
            'pagamento_futuro'
        )
    ),
    CONSTRAINT pagamentos_valores_check CHECK (
        valor_mao_obra >= 0
        AND valor_material >= 0
        AND valor_total >= 0
        AND valor_comissao_plataforma >= 0
        AND valor_prestador >= 0
        AND valor_fornecedor >= 0
    )
);

CREATE INDEX IF NOT EXISTS idx_pagamentos_cliente ON pagamentos(cliente_id);
CREATE INDEX IF NOT EXISTS idx_pagamentos_prestador ON pagamentos(prestador_id);
CREATE INDEX IF NOT EXISTS idx_pagamentos_status ON pagamentos(status_pagamento);
CREATE INDEX IF NOT EXISTS idx_pagamentos_created_at ON pagamentos(created_at);

CREATE TABLE IF NOT EXISTS carteira_usuario (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL UNIQUE REFERENCES usuarios(id),
    saldo_disponivel NUMERIC(10, 2) NOT NULL DEFAULT 0,
    saldo_pendente NUMERIC(10, 2) NOT NULL DEFAULT 0,
    saldo_bloqueado NUMERIC(10, 2) NOT NULL DEFAULT 0,
    total_recebido NUMERIC(10, 2) NOT NULL DEFAULT 0,
    total_movimentado NUMERIC(10, 2) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_usuario_id UUID,
    updated_by_usuario_id UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by_usuario_id UUID,
    CONSTRAINT carteira_valores_check CHECK (
        saldo_disponivel >= 0
        AND saldo_pendente >= 0
        AND saldo_bloqueado >= 0
        AND total_recebido >= 0
        AND total_movimentado >= 0
    )
);

CREATE INDEX IF NOT EXISTS idx_carteira_usuario_id ON carteira_usuario(usuario_id);

CREATE TABLE IF NOT EXISTS movimentacoes_carteira (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    carteira_id UUID NOT NULL REFERENCES carteira_usuario(id),
    usuario_id UUID NOT NULL REFERENCES usuarios(id),
    pagamento_id UUID REFERENCES pagamentos(id),
    tipo_movimentacao VARCHAR(40) NOT NULL,
    valor NUMERIC(10, 2) NOT NULL,
    descricao TEXT,
    saldo_disponivel_apos NUMERIC(10, 2) NOT NULL DEFAULT 0,
    saldo_pendente_apos NUMERIC(10, 2) NOT NULL DEFAULT 0,
    saldo_bloqueado_apos NUMERIC(10, 2) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_usuario_id UUID,
    updated_by_usuario_id UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by_usuario_id UUID,
    CONSTRAINT movimentacoes_tipo_check CHECK (
        tipo_movimentacao IN (
            'entrada',
            'saida',
            'bloqueio',
            'desbloqueio',
            'repasse',
            'estorno',
            'comissao'
        )
    ),
    CONSTRAINT movimentacoes_valor_check CHECK (valor >= 0)
);

CREATE INDEX IF NOT EXISTS idx_movimentacoes_carteira ON movimentacoes_carteira(carteira_id);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_usuario ON movimentacoes_carteira(usuario_id);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_pagamento ON movimentacoes_carteira(pagamento_id);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_created_at ON movimentacoes_carteira(created_at);
