# App de Prestacao de Servicos

Projeto MVP de prestacao de servicos com app mobile Expo/React Native,
backend FastAPI/PostgreSQL e painel admin web.

Consulte `AGENTS.md` para as regras de arquitetura, UX, banco, backend,
frontend, painel admin e preparacao para Machine Learning.

## Importante

O app Android/Expo Go continua sendo o projeto principal.

A camada web atual existe apenas para teste interno e validacao rapida:

- `frontend`: app mobile principal, tambem preparado para web de teste
- `admin-web`: painel admin web
- `backend`: API FastAPI

Guia de GitHub e Vercel:

```text
docs/GITHUB_VERCEL_DEPLOY.md
```

## Backend

Para iniciar a API local:

```powershell
cd "C:\Users\Sarah\Documents\app-serviços\backend"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Depois acesse:

```text
http://127.0.0.1:8000/docs
```

## Testes automatizados do backend

Os testes ficam em `backend/tests` e cobrem os principais fluxos do MVP:

- saude da API
- cadastro e login
- protecao JWT
- clientes e prestadores
- servicos tabelados
- solicitacoes
- aceite do prestador
- material e aprovacao
- execucao e conclusao
- avaliacoes
- chat
- notificacoes
- pagamentos, carteira e repasses
- dashboard e relatorios admin

Por padrao, os testes usam um banco separado:

```text
app_servicos_test
```

Esse banco e recriado automaticamente pela configuracao de testes antes da suite rodar.
Ele usa a variavel `TEST_DATABASE_URL`, quando informada. Se ela nao existir, usa:

```text
postgresql+psycopg://postgres:postgres@localhost:5432/app_servicos_test
```

Para instalar as dependencias do backend:

```powershell
cd "C:\Users\Sarah\Documents\app-serviços"
python -m pip install -r backend\requirements.txt
```

Para rodar todos os testes:

```powershell
cd "C:\Users\Sarah\Documents\app-serviços"
python -m pytest backend\tests -q
```

## Deploy web de teste

O deploy web deve ser separado em dois projetos no Vercel:

```text
app-servicos-web
app-servicos-painel
```

Leia:

```text
docs/GITHUB_VERCEL_DEPLOY.md
```
