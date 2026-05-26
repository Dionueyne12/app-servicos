CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(180) NOT NULL UNIQUE,
    telefone VARCHAR(20) NOT NULL,
    senha_hash TEXT NOT NULL,
    tipo_usuario VARCHAR(30) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT usuarios_tipo_check CHECK (
        tipo_usuario IN ('cliente', 'prestador', 'empresa_fornecedora', 'admin')
    )
);

CREATE TABLE clientes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL UNIQUE REFERENCES usuarios(id),
    documento VARCHAR(20),
    endereco_principal TEXT,
    cidade VARCHAR(120),
    estado VARCHAR(2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE prestadores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL UNIQUE REFERENCES usuarios(id),
    documento VARCHAR(20),
    bio TEXT,
    cidade VARCHAR(120),
    estado VARCHAR(2),
    media_avaliacao NUMERIC(3, 2) NOT NULL DEFAULT 0,
    total_servicos INTEGER NOT NULL DEFAULT 0,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE empresas_fornecedoras (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID UNIQUE REFERENCES usuarios(id),
    nome_fantasia VARCHAR(160) NOT NULL,
    cnpj VARCHAR(20),
    telefone VARCHAR(20),
    cidade VARCHAR(120),
    estado VARCHAR(2),
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE categorias_servico (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(120) NOT NULL UNIQUE,
    descricao TEXT,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE servicos_tabelados (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    categoria_id UUID NOT NULL REFERENCES categorias_servico(id),
    nome VARCHAR(160) NOT NULL,
    descricao TEXT NOT NULL,
    preco_mao_obra NUMERIC(10, 2) NOT NULL,
    tempo_estimado_minutos INTEGER NOT NULL,
    precisa_material BOOLEAN NOT NULL DEFAULT FALSE,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT servicos_preco_check CHECK (preco_mao_obra >= 0),
    CONSTRAINT servicos_tempo_check CHECK (tempo_estimado_minutos > 0)
);

CREATE TABLE status_servico (
    codigo VARCHAR(60) PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    ordem INTEGER NOT NULL,
    finaliza_fluxo BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE solicitacoes_servico (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id UUID NOT NULL REFERENCES clientes(id),
    prestador_id UUID REFERENCES prestadores(id),
    servico_tabelado_id UUID REFERENCES servicos_tabelados(id),
    categoria_id UUID REFERENCES categorias_servico(id),
    tipo_servico VARCHAR(30) NOT NULL DEFAULT 'tabelado',
    titulo VARCHAR(160) NOT NULL,
    descricao TEXT NOT NULL,
    endereco TEXT NOT NULL,
    cidade VARCHAR(120),
    estado VARCHAR(2),
    urgencia VARCHAR(30) NOT NULL DEFAULT 'normal',
    melhor_horario VARCHAR(120),
    observacoes TEXT,
    status_codigo VARCHAR(60) NOT NULL REFERENCES status_servico(codigo),
    preco_mao_obra_snapshot NUMERIC(10, 2),
    tempo_estimado_snapshot_minutos INTEGER,
    aceito_em TIMESTAMPTZ,
    iniciado_em TIMESTAMPTZ,
    concluido_em TIMESTAMPTZ,
    cancelado_em TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT solicitacoes_tipo_check CHECK (tipo_servico IN ('tabelado', 'personalizado')),
    CONSTRAINT solicitacoes_urgencia_check CHECK (urgencia IN ('baixa', 'normal', 'alta')),
    CONSTRAINT solicitacoes_descricao_check CHECK (char_length(descricao) BETWEEN 10 AND 1000)
);

CREATE INDEX idx_solicitacoes_disponiveis
    ON solicitacoes_servico (status_codigo, created_at)
    WHERE prestador_id IS NULL;

CREATE TABLE fotos_servico (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solicitacao_id UUID NOT NULL REFERENCES solicitacoes_servico(id),
    enviado_por_usuario_id UUID NOT NULL REFERENCES usuarios(id),
    url TEXT NOT NULL,
    tipo_foto VARCHAR(30) NOT NULL DEFAULT 'cliente',
    mime_type VARCHAR(80) NOT NULL,
    tamanho_bytes INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fotos_tipo_check CHECK (tipo_foto IN ('cliente', 'prestador', 'material')),
    CONSTRAINT fotos_mime_check CHECK (mime_type IN ('image/jpeg', 'image/png', 'image/webp'))
);

CREATE TABLE materiais_servico (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solicitacao_id UUID NOT NULL UNIQUE REFERENCES solicitacoes_servico(id),
    escolha_cliente VARCHAR(40) NOT NULL,
    descricao TEXT,
    marca_modelo VARCHAR(160),
    foto_url TEXT,
    valor_estimado NUMERIC(10, 2),
    limite_valor_cliente NUMERIC(10, 2),
    empresa_fornecedora_id UUID REFERENCES empresas_fornecedoras(id),
    aprovado_pelo_cliente BOOLEAN,
    aprovado_em TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT materiais_escolha_check CHECK (
        escolha_cliente IN ('cliente_fornece_material', 'prestador_providencia_material', 'material_indefinido')
    ),
    CONSTRAINT materiais_valor_estimado_check CHECK (valor_estimado IS NULL OR valor_estimado >= 0),
    CONSTRAINT materiais_limite_check CHECK (limite_valor_cliente IS NULL OR limite_valor_cliente >= 0)
);

CREATE TABLE avaliacoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solicitacao_id UUID NOT NULL REFERENCES solicitacoes_servico(id),
    avaliador_usuario_id UUID NOT NULL REFERENCES usuarios(id),
    avaliado_usuario_id UUID NOT NULL REFERENCES usuarios(id),
    nota INTEGER NOT NULL,
    comentario TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT avaliacoes_nota_check CHECK (nota BETWEEN 1 AND 5),
    CONSTRAINT avaliacoes_unica_por_avaliador UNIQUE (solicitacao_id, avaliador_usuario_id)
);

CREATE TABLE pagamentos_simulados (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solicitacao_id UUID NOT NULL UNIQUE REFERENCES solicitacoes_servico(id),
    valor_mao_obra NUMERIC(10, 2) NOT NULL DEFAULT 0,
    valor_material NUMERIC(10, 2) NOT NULL DEFAULT 0,
    valor_comissao NUMERIC(10, 2) NOT NULL DEFAULT 0,
    valor_prestador NUMERIC(10, 2) NOT NULL DEFAULT 0,
    valor_empresa NUMERIC(10, 2) NOT NULL DEFAULT 0,
    status_pagamento VARCHAR(40) NOT NULL DEFAULT 'simulado',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT pagamentos_valores_check CHECK (
        valor_mao_obra >= 0
        AND valor_material >= 0
        AND valor_comissao >= 0
        AND valor_prestador >= 0
        AND valor_empresa >= 0
    )
);

CREATE TABLE repasses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pagamento_id UUID NOT NULL REFERENCES pagamentos_simulados(id),
    destinatario_usuario_id UUID REFERENCES usuarios(id),
    empresa_fornecedora_id UUID REFERENCES empresas_fornecedoras(id),
    tipo_repasse VARCHAR(40) NOT NULL,
    valor NUMERIC(10, 2) NOT NULL,
    status_repasse VARCHAR(40) NOT NULL DEFAULT 'pendente',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT repasses_valor_check CHECK (valor >= 0),
    CONSTRAINT repasses_tipo_check CHECK (tipo_repasse IN ('prestador', 'empresa', 'plataforma'))
);

CREATE TABLE historico_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solicitacao_id UUID NOT NULL REFERENCES solicitacoes_servico(id),
    status_anterior VARCHAR(60) REFERENCES status_servico(codigo),
    status_novo VARCHAR(60) NOT NULL REFERENCES status_servico(codigo),
    alterado_por_usuario_id UUID NOT NULL REFERENCES usuarios(id),
    observacao TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE historico_edicoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entidade VARCHAR(80) NOT NULL,
    entidade_id UUID NOT NULL,
    campo VARCHAR(120) NOT NULL,
    valor_anterior TEXT,
    valor_novo TEXT,
    alterado_por_usuario_id UUID NOT NULL REFERENCES usuarios(id),
    origem VARCHAR(40) NOT NULL DEFAULT 'backend',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_servicos_tabelados_categoria ON servicos_tabelados(categoria_id);
CREATE INDEX idx_solicitacoes_cliente ON solicitacoes_servico(cliente_id);
CREATE INDEX idx_solicitacoes_prestador ON solicitacoes_servico(prestador_id);
CREATE INDEX idx_solicitacoes_categoria ON solicitacoes_servico(categoria_id);
CREATE INDEX idx_solicitacoes_status ON solicitacoes_servico(status_codigo);
CREATE INDEX idx_historico_status_solicitacao ON historico_status(solicitacao_id);
CREATE INDEX idx_historico_edicoes_entidade ON historico_edicoes(entidade, entidade_id);
