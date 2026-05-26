# Database

Arquivos de banco de dados, migracoes, seeds e documentacao do PostgreSQL.

## Ordem inicial

1. Executar `migrations/001_initial_schema.sql`
2. Executar `seeds/001_seed_initial_data.sql`
3. Se o banco ja existir com a primeira versao, executar
   `migrations/002_solicitacoes_servico_mvp.sql`
4. Executar `migrations/003_aceite_prestador_status.sql` para alinhar os
   status do fluxo de aceite do prestador.
5. Executar `migrations/004_auditoria_soft_delete.sql` para adicionar auditoria
   basica e soft delete nas tabelas principais.
6. Executar `migrations/005_fotos_servico_upload.sql` para completar o controle
   de fotos das solicitacoes.
7. Executar `migrations/006_fluxo_material_orcamento.sql` para habilitar o
   fluxo de material e aprovacao de orcamento.

O schema inicial separa usuarios, perfis, servicos tabelados, solicitacoes,
material, fotos, avaliacoes, pagamento simulado, repasses e historicos.
