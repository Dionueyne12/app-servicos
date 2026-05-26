CREATE TABLE IF NOT EXISTS mensagens_solicitacao (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solicitacao_id UUID NOT NULL REFERENCES solicitacoes_servico(id),
    remetente_usuario_id UUID NOT NULL REFERENCES usuarios(id),
    destinatario_usuario_id UUID NOT NULL REFERENCES usuarios(id),
    tipo_mensagem VARCHAR(40) NOT NULL DEFAULT 'texto',
    mensagem TEXT NOT NULL,
    arquivo_url TEXT,
    visualizada BOOLEAN NOT NULL DEFAULT FALSE,
    data_visualizacao TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by_usuario_id UUID REFERENCES usuarios(id),
    updated_by_usuario_id UUID REFERENCES usuarios(id),
    deleted_by_usuario_id UUID REFERENCES usuarios(id),
    CONSTRAINT mensagens_tipo_check CHECK (
        tipo_mensagem IN ('texto', 'imagem', 'sistema', 'alerta', 'comprovante')
    ),
    CONSTRAINT mensagens_texto_tamanho_check CHECK (
        char_length(trim(mensagem)) BETWEEN 1 AND 2000
    )
);

CREATE INDEX IF NOT EXISTS idx_mensagens_solicitacao_data
    ON mensagens_solicitacao(solicitacao_id, created_at)
    WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_mensagens_destinatario_nao_lidas
    ON mensagens_solicitacao(destinatario_usuario_id, solicitacao_id)
    WHERE visualizada = FALSE AND deleted_at IS NULL;
