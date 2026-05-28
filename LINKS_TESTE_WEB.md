# Links da Versao Web de Teste

Esta versao web existe apenas para testes internos com o dono do projeto.
Ela serve para validar fluxos, telas e integracoes mais rapidamente pelo
navegador.

O projeto original Android/APK continua intacto. A versao mobile segue sendo
o produto principal.

## 1. Backend/API

```text
https://app-servicos-4t4l.vercel.app
```

Teste de saude da API:

```text
https://app-servicos-4t4l.vercel.app/api/v1/health
```

Documentacao FastAPI:

```text
https://app-servicos-4t4l.vercel.app/docs
```

## 2. Painel Admin

```text
https://app-servicos-ncpxr0rcc-weyneborges2-6361s-projects.vercel.app
```

Login padrao de teste:

```text
E-mail: admin@app.com
Senha: Admin@123
```

## 3. App Cliente/Prestador

Status:

```text
Aguardando deploy do projeto frontend no Vercel.
```

## 4. Configuracao para publicar o app web

Criar um novo projeto separado no Vercel para o app cliente/prestador.

Configuracao:

```text
Root Directory: frontend
Build Command: npm run build:web
Output Directory: dist
Install Command: npm install
```

Variavel de ambiente:

```text
EXPO_PUBLIC_API_BASE_URL=https://app-servicos-4t4l.vercel.app/api/v1
```

## 5. Observacoes importantes

- Esta versao web e apenas para teste com o dono do projeto.
- Ela nao substitui o app Android.
- Ela nao altera o fluxo APK.
- Ela nao muda a camera, galeria ou recursos nativos do Android.
- Ela facilita testes rapidos enquanto o produto ainda esta em validacao.

Depois que tudo estiver validado, a versao web de teste pode ser desativada e
o APK final pode ser gerado normalmente.
