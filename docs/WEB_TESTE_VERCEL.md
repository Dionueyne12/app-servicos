# Web de teste para validacao interna

Esta camada web e apenas para testes internos. Ela nao substitui o app Android,
nao muda a arquitetura principal e nao remove nenhuma funcionalidade mobile.

## Objetivo

- testar fluxos no navegador
- validar mudancas com outra pessoa por link
- acelerar feedback sem depender sempre do QR Code do Expo Go
- manter Android e futura geracao APK funcionando normalmente

## Estrutura temporaria

- `frontend`: app Expo principal, agora tambem roda no navegador para teste
- `admin-web`: painel administrativo em React/Vite
- `backend`: FastAPI separado, futuramente no Railway
- PostgreSQL: banco separado, futuramente online

## Variaveis de ambiente

App Expo:

```text
EXPO_PUBLIC_API_BASE_URL=https://SUA_API/api/v1
```

Tambem foi deixada uma ponte de seguranca: se o Vercel tiver apenas
`VITE_API_BASE_URL`, o build do Expo copia esse valor para
`EXPO_PUBLIC_API_BASE_URL`.

Painel Admin:

```text
VITE_API_BASE_URL=https://SUA_API/api/v1
```

## Vercel

### App web de teste

Pasta:

```text
frontend
```

Build:

```text
npm run build:web
```

Saida:

```text
dist
```

### Painel Admin

Pasta:

```text
admin-web
```

Build:

```text
npm run build
```

Saida:

```text
dist
```

## Importante

- nao usar localhost em deploy
- configurar a URL real do Railway nas variaveis do Vercel
- testar login, cadastro, solicitacoes e painel antes de compartilhar o link
- manter o Android como versao principal do produto
