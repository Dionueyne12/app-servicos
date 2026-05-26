CREATE TABLE IF NOT EXISTS notificacoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL REFERENCES usuarios(id),
    solicitacao_id UUID REFERENCES solicitacoes_servico(id),
    tipo_notificacao VARCHAR(60) NOT NULL,
    titulo VARCHAR(160) NOT NULL,
    mensagem TEXT NOT NULL,
    lida BOOLEAN NOT NULL DEFAULT FALSE,
    data_leitura TIMESTAMPTZ,
    prioridade VARCHAR(20) NOT NULL DEFAULT 'normal',
    canal VARCHAR(40) NOT NULL DEFAULT 'interna',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by_usuario_id UUID REFERENCES usuarios(id),
    updated_by_usuario_id UUID REFERENCES usuarios(id),
    deleted_by_usuario_id UUID REFERENCES usuarios(id),
    CONSTRAINT notificacoes_tipo_check CHECK (
        tipo_notificacao IN (
            'servico_criado',
            'servico_aceito',
            'material_enviado',
            'material_aprovado',
            'material_recusado',
            'servico_iniciado',
            'servico_concluido',
            'problema_informado',
            'nova_mensagem',
            'avaliacao_recebida',
            'repasse_pendente',
            'alerta_admin'
        )
    ),
    CONSTRAINT notificacoes_prioridade_check CHECK (
        prioridade IN ('baixa', 'normal', 'alta', 'critica')
    ),
    CONSTRAINT notificacoes_canal_check CHECK (
        canal IN ('interna', 'push_futura', 'email_futuro', 'whatsapp_futuro')
    )
);

CREATE INDEX IF NOT EXISTS idx_notificacoes_usuario_data
    ON notificacoes(usuario_id, created_at DESC)
    WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_notificacoes_usuario_nao_lidas
    ON notificacoes(usuario_id)
    WHERE lida = FALSE AND deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_notificacoes_solicitacao
    ON notificacoes(solicitacao_id)
    WHERE deleted_at IS NULL;
