# Frontend Mobile + Web de Teste

Aplicativo principal em React Native + Expo.

A versao Android continua sendo o foco principal. A versao web existe apenas
para testes internos rapidos no navegador, sem substituir o app mobile.

## Stack

- React Native
- Expo
- JavaScript
- React Navigation
- Axios
- Context API
- AsyncStorage

## Como iniciar

Instale as dependencias:

```powershell
cd "C:\Users\Sarah\Documents\app-serviços\frontend"
npm install
```

Se o Expo reclamar da camera ou galeria, instale o pacote compativel:

```powershell
npx expo install expo-image-picker
```

Abra o Expo:

```powershell
npm start
```

## Rodar no navegador para teste local

Use a mesma API do backend, sem URL fixa no codigo:

```powershell
cd "C:\Users\Sarah\Documents\app-serviços\frontend"
$env:EXPO_PUBLIC_API_BASE_URL="http://192.168.1.108:8000/api/v1"
npm run web
```

Se trocar a URL da API, reinicie limpando o cache:

```powershell
npx expo start --web -c
```

Para celular fisico, use obrigatoriamente o IP local do computador.

No PowerShell:

```powershell
$env:EXPO_PUBLIC_API_BASE_URL="http://192.168.1.108:8000/api/v1"
npm start
```

No Prompt de Comando:

```cmd
set EXPO_PUBLIC_API_BASE_URL=http://192.168.1.108:8000/api/v1
npm start
```

Se trocar a URL, feche o Expo e reinicie limpando o cache:

```powershell
npx expo start -c
```

O app ja conecta login, cadastro, solicitacoes, servicos disponiveis,
notificacoes e acoes basicas do prestador ao backend FastAPI.

## Deploy de teste no Vercel

Projeto no Vercel:

```text
frontend
```

Build command:

```text
npm run build:web
```

Output directory:

```text
dist
```

Variavel de ambiente:

```text
EXPO_PUBLIC_API_BASE_URL=https://SUA_API/api/v1
```

Observacao: o painel admin usa `VITE_API_BASE_URL`, mas o app Expo usa
`EXPO_PUBLIC_API_BASE_URL`, que e o padrao do Expo para Android e web.
Para evitar erro no deploy de teste, `frontend/app.config.js` tambem aceita
`VITE_API_BASE_URL` e copia para `EXPO_PUBLIC_API_BASE_URL` durante o build.

## Backend local

O app nao usa URL fixa. A URL vem somente da variavel:

```text
EXPO_PUBLIC_API_BASE_URL
```
