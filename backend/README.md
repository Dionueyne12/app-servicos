# Backend

API principal do projeto, planejada para Python + FastAPI.

## Base inicial

- `app/main.py`: cria a aplicacao FastAPI.
- `app/config.py`: le configuracoes por variaveis de ambiente.
- `app/logging_config.py`: configura logs estruturados em JSON.
- `app/middleware.py`: adiciona middleware global de request com `X-Request-ID`.
- `app/pagination.py`: centraliza paginacao das listagens.
- `app/responses.py`: padroniza respostas de erro.
- `database/session.py`: configura conexao PostgreSQL via SQLAlchemy.
- `routes/`: expoe rotas HTTP.
- `controllers/`: adapta entrada/saida das rotas.
- `services/`: concentra regras de negocio.
- `models/`: modelos SQLAlchemy.
- `auth/`: hash de senha, JWT e usuario autenticado.
- `utils/exceptions.py`: erros de aplicacao.

## API

- Rotas legadas: `/api/...`
- Rotas versionadas: `/api/v1/...`
- Listagens principais usam `page`, `per_page` e filtros de busca/status.
- Erros retornam `success`, `detail`, `code` e `request_id`.

## Variaveis de ambiente

Copie `.env.example` como referencia e configure `DATABASE_URL` e
`JWT_SECRET_KEY` antes de rodar em ambiente real.
