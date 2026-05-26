INSERT INTO status_servico (codigo, nome, ordem, finaliza_fluxo) VALUES
    ('rascunho', 'Rascunho', 10, FALSE),
    ('aguardando_prestador', 'Aguardando prestador', 20, FALSE),
    ('aceito', 'Aceito', 30, FALSE),
    ('aguardando_avaliacao_material', 'Aguardando avaliacao de material', 40, FALSE),
    ('aguardando_aprovacao_cliente', 'Aguardando aprovacao do cliente', 50, FALSE),
    ('material_aprovado', 'Material aprovado', 60, FALSE),
    ('em_andamento', 'Em andamento', 70, FALSE),
    ('aguardando_confirmacao_cliente', 'Aguardando confirmacao do cliente', 80, FALSE),
    ('concluido', 'Concluido', 90, TRUE),
    ('cancelado', 'Cancelado', 100, TRUE),
    ('em_analise', 'Em analise', 110, FALSE)
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO categorias_servico (nome, descricao) VALUES
    ('Eletrica', 'Servicos eletricos residenciais simples.'),
    ('Hidraulica', 'Servicos hidraulicos residenciais simples.'),
    ('Instalacao', 'Instalacoes e fixacoes gerais.')
ON CONFLICT (nome) DO NOTHING;

INSERT INTO servicos_tabelados (
    categoria_id,
    nome,
    descricao,
    preco_mao_obra,
    tempo_estimado_minutos,
    precisa_material
)
SELECT id, 'Trocar chuveiro', 'Substituicao de chuveiro residencial.', 120.00, 60, TRUE
FROM categorias_servico WHERE nome = 'Eletrica'
ON CONFLICT DO NOTHING;

INSERT INTO servicos_tabelados (
    categoria_id,
    nome,
    descricao,
    preco_mao_obra,
    tempo_estimado_minutos,
    precisa_material
)
SELECT id, 'Trocar tomada', 'Substituicao de tomada residencial.', 80.00, 45, TRUE
FROM categorias_servico WHERE nome = 'Eletrica'
ON CONFLICT DO NOTHING;

INSERT INTO servicos_tabelados (
    categoria_id,
    nome,
    descricao,
    preco_mao_obra,
    tempo_estimado_minutos,
    precisa_material
)
SELECT id, 'Instalar suporte TV', 'Instalacao de suporte de TV em parede.', 150.00, 90, TRUE
FROM categorias_servico WHERE nome = 'Instalacao'
ON CONFLICT DO NOTHING;

INSERT INTO servicos_tabelados (
    categoria_id,
    nome,
    descricao,
    preco_mao_obra,
    tempo_estimado_minutos,
    precisa_material
)
SELECT id, 'Instalar ventilador', 'Instalacao de ventilador residencial.', 180.00, 120, TRUE
FROM categorias_servico WHERE nome = 'Eletrica'
ON CONFLICT DO NOTHING;

INSERT INTO servicos_tabelados (
    categoria_id,
    nome,
    descricao,
    preco_mao_obra,
    tempo_estimado_minutos,
    precisa_material
)
SELECT id, 'Trocar resistencia', 'Troca de resistencia de chuveiro.', 70.00, 40, TRUE
FROM categorias_servico WHERE nome = 'Eletrica'
ON CONFLICT DO NOTHING;

INSERT INTO servicos_tabelados (
    categoria_id,
    nome,
    descricao,
    preco_mao_obra,
    tempo_estimado_minutos,
    precisa_material
)
SELECT id, 'Trocar torneira', 'Substituicao de torneira residencial.', 100.00, 60, TRUE
FROM categorias_servico WHERE nome = 'Hidraulica'
ON CONFLICT DO NOTHING;
