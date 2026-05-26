ALTER TABLE fotos_servico
    ADD COLUMN IF NOT EXISTS usuario_id UUID REFERENCES usuarios(id),
    ADD COLUMN IF NOT EXISTS caminho_arquivo TEXT,
    ADD COLUMN IF NOT EXISTS nome_original VARCHAR(255),
    ADD COLUMN IF NOT EXISTS descricao TEXT,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS created_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS updated_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by_usuario_id UUID;

UPDATE fotos_servico
SET
    usuario_id = COALESCE(usuario_id, enviado_por_usuario_id),
    caminho_arquivo = COALESCE(caminho_arquivo, url),
    nome_original = COALESCE(nome_original, 'arquivo')
WHERE usuario_id IS NULL OR caminho_arquivo IS NULL OR nome_original IS NULL;

ALTER TABLE fotos_servico
    ALTER COLUMN usuario_id SET NOT NULL,
    ALTER COLUMN caminho_arquivo SET NOT NULL,
    ALTER COLUMN nome_original SET NOT NULL,
    ALTER COLUMN tamanho_bytes SET NOT NULL;

ALTER TABLE fotos_servico
    DROP CONSTRAINT IF EXISTS fotos_tipo_check;

ALTER TABLE fotos_servico
    ADD CONSTRAINT fotos_tipo_check CHECK (
        tipo_foto IN (
            'problema',
            'material_cliente',
            'antes_servico',
            'depois_servico',
            'comprovante_material'
        )
    );

ALTER TABLE fotos_servico
    DROP CONSTRAINT IF EXISTS fotos_mime_check;

ALTER TABLE fotos_servico
    ADD CONSTRAINT fotos_mime_check CHECK (
        mime_type IN ('image/jpeg', 'image/png', 'image/webp')
    );

CREATE INDEX IF NOT EXISTS idx_fotos_servico_solicitacao
    ON fotos_servico(solicitacao_id);

CREATE INDEX IF NOT EXISTS idx_fotos_servico_deleted_at
    ON fotos_servico(deleted_at);
