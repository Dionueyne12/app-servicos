INSERT INTO status_servico (codigo, nome, ordem, finaliza_fluxo) VALUES
    ('aguardando_avaliacao_material', 'Aguardando avaliacao de material', 40, FALSE),
    ('aguardando_confirmacao_cliente', 'Aguardando confirmacao do cliente', 80, FALSE)
ON CONFLICT (codigo) DO UPDATE SET
    nome = EXCLUDED.nome,
    ordem = EXCLUDED.ordem,
    finaliza_fluxo = EXCLUDED.finaliza_fluxo;

UPDATE status_servico
SET nome = 'Aguardando aprovacao do cliente', ordem = 50, finaliza_fluxo = FALSE
WHERE codigo = 'aguardando_aprovacao_cliente';

UPDATE status_servico
SET nome = 'Material aprovado', ordem = 60, finaliza_fluxo = FALSE
WHERE codigo = 'material_aprovado';

UPDATE status_servico
SET nome = 'Em andamento', ordem = 70, finaliza_fluxo = FALSE
WHERE codigo = 'em_andamento';

UPDATE status_servico
SET nome = 'Concluido', ordem = 90, finaliza_fluxo = TRUE
WHERE codigo = 'concluido';

UPDATE status_servico
SET nome = 'Cancelado', ordem = 100, finaliza_fluxo = TRUE
WHERE codigo = 'cancelado';

UPDATE status_servico
SET nome = 'Em analise', ordem = 110, finaliza_fluxo = FALSE
WHERE codigo = 'em_analise';
