# BLOCO 1 — VISÃO GERAL DO PROJETO + ARQUITETURA + UX

# AGENTS.md — APP DE PRESTAÇÃO DE SERVIÇOS

## OBJETIVO

Criar um app moderno de prestação de serviços inspirado em:
- Uber
- GetNinjas
- iFood moderno
- Mercado Pago
- Nubank

O app deve ser:
- rápido
- intuitivo
- simples
- escalável
- profissional
- fácil de usar
- preparado para crescimento futuro

O sistema terá:

1. Cliente
2. Prestador
3. Empresa fornecedora
4. Painel admin
5. Machine Learning futuramente integrado

==================================================
TECNOLOGIAS
==================================================

Frontend:
- React Native
- Expo
- JavaScript

Backend:
- Python
- FastAPI

Banco:
- PostgreSQL

Painel Admin:
- React.js

Upload:
- Supabase Storage

Machine Learning:
- Python
- Scikit-learn
- Pandas
- Future AI services

==================================================
OBJETIVO DA PRIMEIRA FASE
==================================================

Criar um MVP funcional contendo:

- cadastro cliente
- cadastro prestador
- serviços tabelados
- solicitação de serviço
- upload de fotos
- escolha de material
- edição segura
- aceite do prestador
- status do serviço
- avaliações
- pagamento simulado
- painel admin
- estrutura pronta para IA futuramente

==================================================
PADRÃO VISUAL
==================================================

O app precisa parecer:
- moderno
- profissional
- premium
- intuitivo

Usar:
- cards
- cantos arredondados
- sombras suaves
- poucos campos por tela
- fluxo guiado
- linguagem simples
- feedback visual

==================================================
PALETA DE CORES
==================================================

Fundo:
#F4F6F8

Azul principal:
#2563EB

Verde:
#22C55E

Laranja:
#F59E0B

Vermelho:
#EF4444

Texto principal:
#111827

Texto secundário:
#6B7280

Cards:
#FFFFFF

==================================================
REGRAS DE UX
==================================================

O app deve:
- orientar o usuário
- mostrar próximo passo
- evitar telas confusas
- evitar muitos campos
- explicar material claramente
- validar tudo antes de salvar
- permitir edição segura
- salvar histórico

==================================================
ESTRUTURA DE PASTAS
==================================================

/frontend
/backend
/admin-panel
/database
/docs
/machine-learning

==================================================
ESTRUTURA BACKEND
==================================================

/backend/app
/backend/routes
/backend/models
/backend/services
/backend/controllers
/backend/auth
/backend/database
/backend/utils

==================================================
ESTRUTURA FRONTEND
==================================================

/frontend/src/screens
/frontend/src/components
/frontend/src/services
/frontend/src/navigation
/frontend/src/hooks
/frontend/src/context
/frontend/src/styles

==================================================
ESTRUTURA MACHINE LEARNING
==================================================

/machine-learning/models
/machine-learning/training
/machine-learning/predictions
/machine-learning/datasets

==================================================
REGRAS IMPORTANTES
==================================================

Nunca:
- misturar frontend e backend
- misturar material e mão de obra
- permitir aceite duplicado
- permitir status inválido
- deixar rota sem proteção
- apagar histórico importante
- criar banco engessado

Sempre:
- validar inputs
- usar JWT
- salvar histórico
- tratar erros
- criar código escalável
- separar responsabilidades
- pensar em futuras expansões

# BLOCO 2 — FLUXOS + SERVIÇOS + MATERIAL + EDIÇÕES + BANCO

==================================================
PERFIS
==================================================

CLIENTE:
- cria conta
- solicita serviço
- envia fotos
- escolhe material
- acompanha status
- aprova material
- confirma conclusão
- avalia prestador
- edita informações permitidas

PRESTADOR:
- cria conta
- vê serviços
- aceita serviço
- informa material
- altera status
- conclui serviço
- avalia cliente

EMPRESA FORNECEDORA:
- fornece materiais
- participa do fluxo de compra

ADMIN:
- controla serviços tabelados
- altera preços
- altera tempo estimado
- acompanha usuários
- acompanha pagamentos
- acompanha avaliações

==================================================
SERVIÇOS TABELADOS
==================================================

Cada serviço deve ter:

- id
- nome
- categoria
- descrição
- preço mão de obra
- tempo estimado
- precisa material
- ativo/inativo
- created_at
- updated_at

Exemplos:

Trocar chuveiro
Instalar suporte TV
Trocar tomada
Instalar ventilador
Trocar resistência
Trocar torneira

==================================================
REGRA DOS SERVIÇOS TABELADOS
==================================================

Admin pode:
- criar
- editar
- alterar preço
- alterar tempo
- ativar/desativar

Nunca apagar definitivamente serviços antigos.

Usar:
ativo = true/false

==================================================
FLUXO CLIENTE
==================================================

Cliente:
↓
abre app
↓
faz login
↓
solicita serviço
↓
escolhe:
- serviço tabelado
ou
- personalizado
↓
descreve problema
↓
envia fotos
↓
escolhe material
↓
confirma resumo
↓
envia solicitação

==================================================
FLUXO MATERIAL
==================================================

Cliente escolhe:

1. Já tenho material
2. Prestador providencia
3. Ainda não sei

==================================================
SE CLIENTE JÁ TEM MATERIAL
==================================================

Campos:
- descrição
- foto opcional
- marca/modelo

==================================================
SE PRESTADOR PROVIDENCIA
==================================================

Campos:
- orçamento
- empresa fornecedora
- limite valor
- aprovação cliente

==================================================
SE CLIENTE NÃO SABE
==================================================

Prestador avalia:
- material necessário
- valor estimado
- empresa sugerida

Cliente aprova depois.

==================================================
EDIÇÃO DE CAMPOS
==================================================

Cliente pode editar antes do aceite:
- descrição
- fotos
- urgência
- endereço
- observações
- material

Depois do aceite:
- somente alterações controladas

Prestador pode editar:
- observações técnicas
- material
- status
- fotos serviço

Admin:
- pode corrigir tudo administrativamente

==================================================
HISTÓRICO
==================================================

Salvar:
- quem alterou
- o que alterou
- antes/depois
- data
- hora

==================================================
STATUS
==================================================

- rascunho
- aguardando_prestador
- aceito
- aguardando_material
- aguardando_aprovacao_cliente
- material_aprovado
- em_andamento
- aguardando_confirmacao
- concluido
- cancelado
- em_analise

==================================================
REGRA CRÍTICA
==================================================

Nunca permitir:
- dois prestadores aceitarem o mesmo serviço

Backend deve:
- validar status
- travar aceite
- usar transação banco

==================================================
BANCO DE DADOS
==================================================

Tabelas:

usuarios
clientes
prestadores
empresas_fornecedoras
categorias_servico
servicos_tabelados
solicitacoes_servico
fotos_servico
materiais_servico
avaliacoes
pagamentos_simulados
repasses
historico_status
historico_edicoes

==================================================
REGRAS DO BANCO
==================================================

- usar IDs únicos
- usar created_at
- usar updated_at
- separar tabelas
- nunca colocar tudo em uma tabela
- preparar para futuras mudanças
- evitar quebra estrutural futura
# BLOCO 3 — MACHINE LEARNING + IA + VALIDAÇÕES + ERROS + FUTURO

==================================================
MACHINE LEARNING
==================================================

O projeto deve nascer preparado para Machine Learning futuro.

==================================================
OBJETIVOS DA IA
==================================================

1. Melhorar recomendação de prestadores
2. Melhorar previsão de tempo
3. Melhorar previsão de preço
4. Detectar prestadores problemáticos
5. Detectar clientes problemáticos
6. Detectar possíveis fraudes
7. Melhorar matching cliente/prestador
8. Melhorar experiência do usuário

==================================================
EXEMPLOS DE MACHINE LEARNING
==================================================

Sistema aprende:

- tempo médio de instalação
- média de valor por região
- tipos de problemas frequentes
- melhores prestadores por categoria
- prestadores que atrasam
- clientes que cancelam muito
- regiões mais movimentadas
- serviços mais pedidos

==================================================
RECOMENDAÇÃO INTELIGENTE
==================================================

Sistema futuramente poderá sugerir:

“Prestador João possui melhor avaliação para troca de chuveiro nesta região.”

==================================================
PREVISÃO DE TEMPO
==================================================

IA aprende:
- tempo médio real
- tipo serviço
- dificuldade
- região
- histórico

Depois prevê:
- duração provável

==================================================
PREVISÃO DE VALOR
==================================================

IA aprende:
- preço médio
- categoria
- região
- urgência
- material

Depois sugere:
- faixa de preço ideal

==================================================
DETECÇÃO DE PROBLEMAS
==================================================

IA detecta:
- prestador com muitas reclamações
- cliente fraudulento
- comportamento suspeito
- cancelamentos excessivos

==================================================
PREPARAÇÃO DO BANCO PARA IA
==================================================

Salvar:
- avaliações
- tempos reais
- valores reais
- cancelamentos
- região
- categoria
- histórico serviços

==================================================
VALIDAÇÕES
==================================================

Nome:
- mínimo 3 caracteres
- sem números

Telefone:
- somente números
- formato BR

E-mail:
- formato válido
- único

Senha:
- mínimo 8 caracteres
- letra + número

Descrição:
- mínimo 10 caracteres
- máximo 1000

Fotos:
- jpg/png/webp
- limitar tamanho

Preço:
- positivo
- monetário BR

==================================================
TRATAMENTO DE ERROS
==================================================

Evitar:
- aceite duplicado
- upload sem vínculo
- status inválido
- alteração sem histórico
- material misturado
- cliente ver dados privados
- valores errados
- edição sem controle
- exclusão destrutiva

==================================================
PAGAMENTO SIMULADO
==================================================

Separar:
- mão obra
- material
- comissão
- valor prestador
- valor empresa

==================================================
FUTURO DO PROJETO
==================================================

Preparar arquitetura para:
- pagamentos reais
- PIX
- cartão
- mapas
- geolocalização
- notificações push
- IA avançada
- ranking inteligente
- chat interno
- assinatura premium
- analytics
- relatórios avançados
- antifraude
- API pública futura

==================================================
REGRAS PARA O CODEX
==================================================

Sempre:
- criar código limpo
- validar tudo
- tratar erros
- criar arquitetura escalável
- pensar em expansão
- criar estrutura pronta para IA
- salvar histórico
- organizar arquivos
- usar boas práticas

Nunca:
- criar código bagunçado
- misturar responsabilidades
- criar telas poluídas
- criar banco rígido
- quebrar histórico
- criar dependência desnecessária
