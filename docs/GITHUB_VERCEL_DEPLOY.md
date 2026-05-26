# GitHub e Vercel para web de teste

Este guia prepara apenas a versao web de teste. O app Android/Expo Go continua
sendo o projeto principal e nao deve ser alterado por este processo.

## Objetivo

Ter dois deploys de teste no Vercel:

- `app-servicos-web`: app Expo rodando no navegador para validacao interna
- `app-servicos-painel`: painel administrativo web

O backend FastAPI continua separado. Em teste local, pode rodar na sua maquina.
No futuro, a API ira para Railway com PostgreSQL online.

## 1. Criar repositorio GitHub

Crie um repositorio novo no GitHub:

```text
app-servicos
```

Nao use o projeto Sound Church. Este app precisa ficar separado.

## 2. Inicializar Git local

Na pasta raiz:

```powershell
cd "C:\Users\Sarah\Documents\app-serviços"
git init
git branch -M main
git add .
git commit -m "Preparar app servicos para web teste"
git remote add origin https://github.com/SEU_USUARIO/app-servicos.git
git push -u origin main
```

Se o Windows disser que `git` nao existe, instale o Git for Windows e abra o
PowerShell de novo.

## 3. Conferir arquivos ignorados

O `.gitignore` deve impedir envio de:

- `node_modules`
- `.expo`
- `dist`
- `build`
- `venv`
- `__pycache__`
- `.env`
- logs e arquivos temporarios
- uploads locais

Nunca envie senhas, tokens ou URLs privadas dentro de `.env`.

## 4. Deploy do painel no Vercel

Crie um projeto novo no Vercel:

```text
app-servicos-painel
```

Configuracao:

```text
Repository: app-servicos
Root Directory: admin-web
Framework Preset: Vite
Install Command: npm install
Build Command: npm run build
Output Directory: dist
```

Variavel de ambiente:

```text
VITE_API_BASE_URL=https://URL_DA_API_ONLINE/api/v1
```

Teste esperado:

- abrir link do Vercel
- login admin com `admin@app.com`
- dashboard carregar
- menu `Servicos` abrir
- criacao de servico usar categoria em select visual

## 5. Deploy do app web de teste no Vercel

Crie outro projeto novo no Vercel:

```text
app-servicos-web
```

Configuracao:

```text
Repository: app-servicos
Root Directory: frontend
Framework Preset: Other
Install Command: npm install
Build Command: npm run build:web
Output Directory: dist
```

Variavel de ambiente:

```text
EXPO_PUBLIC_API_BASE_URL=https://URL_DA_API_ONLINE/api/v1
```

Se necessario, tambem pode configurar:

```text
VITE_API_BASE_URL=https://URL_DA_API_ONLINE/api/v1
```

O `frontend/app.config.js` copia `VITE_API_BASE_URL` para
`EXPO_PUBLIC_API_BASE_URL` durante o build, caso alguem configure a variavel
errada por engano.

## 6. Backend local agora

Enquanto o backend nao estiver no Railway, rode local:

```powershell
cd "C:\Users\Sarah\Documents\app-serviços\backend"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Para testes no celular ou navegador em rede local, use o IP da maquina:

```text
http://192.168.1.108:8000/api/v1
```

Nao use esse IP no Vercel. No Vercel, use a URL publica do Railway.

## 7. Futuro Railway

Quando subir o backend no Railway:

1. criar projeto Railway para FastAPI
2. configurar PostgreSQL online
3. configurar `DATABASE_URL`
4. aplicar migrations
5. validar `/api/v1/health`
6. atualizar variaveis do Vercel:
   - painel: `VITE_API_BASE_URL=https://SUA_API_RAILWAY/api/v1`
   - app web: `EXPO_PUBLIC_API_BASE_URL=https://SUA_API_RAILWAY/api/v1`

## 8. Cuidados importantes

- nao alterar camera/galeria Android por causa do deploy web
- nao trocar JavaScript por outra linguagem
- nao remover Expo Go
- nao mudar fluxo APK
- nao enviar `.env`
- nao enviar `node_modules`
- manter backend, frontend e painel separados
