ALTER TABLE usuarios
    ADD COLUMN IF NOT EXISTS created_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS updated_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by_usuario_id UUID;

ALTER TABLE clientes
    ADD COLUMN IF NOT EXISTS created_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS updated_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by_usuario_id UUID;

ALTER TABLE prestadores
    ADD COLUMN IF NOT EXISTS created_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS updated_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by_usuario_id UUID;

ALTER TABLE empresas_fornecedoras
    ADD COLUMN IF NOT EXISTS created_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS updated_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by_usuario_id UUID;

ALTER TABLE categorias_servico
    ADD COLUMN IF NOT EXISTS created_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS updated_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by_usuario_id UUID;

ALTER TABLE servicos_tabelados
    ADD COLUMN IF NOT EXISTS created_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS updated_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by_usuario_id UUID;

ALTER TABLE solicitacoes_servico
    ADD COLUMN IF NOT EXISTS created_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS updated_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by_usuario_id UUID;

ALTER TABLE materiais_servico
    ADD COLUMN IF NOT EXISTS created_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS updated_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by_usuario_id UUID;

ALTER TABLE pagamentos_simulados
    ADD COLUMN IF NOT EXISTS created_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS updated_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by_usuario_id UUID;

ALTER TABLE repasses
    ADD COLUMN IF NOT EXISTS created_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS updated_by_usuario_id UUID,
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by_usuario_id UUID;

CREATE INDEX IF NOT EXISTS idx_usuarios_deleted_at ON usuarios(deleted_at);
CREATE INDEX IF NOT EXISTS idx_servicos_tabelados_deleted_at ON servicos_tabelados(deleted_at);
CREATE INDEX IF NOT EXISTS idx_solicitacoes_deleted_at ON solicitacoes_servico(deleted_at);
