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

Para Vercel + Neon PostgreSQL, configure no painel da Vercel:

```text
DATABASE_URL=postgresql://USUARIO:SENHA@HOST_NEON/NOME_DO_BANCO?sslmode=require
```

O backend nao possui fallback automatico para banco local. Se `DATABASE_URL`
nao existir, a API falha com mensagem clara no startup.

URLs iniciadas com `postgres://` sao normalizadas automaticamente para
PostgreSQL e executadas pelo driver `psycopg`.

## CORS

O backend permite chamadas do painel/app publicados no Vercel usando:

```text
CORS_ORIGIN_REGEX=https://.*\.vercel\.app
```

Para desenvolvimento local:

```text
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,http://localhost:4173,http://127.0.0.1:4173
```

As chamadas usam header `Authorization` com token JWT, sem cookies.
