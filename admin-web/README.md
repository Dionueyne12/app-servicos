# Painel Admin Web

Painel web do dono do app de prestacao de servicos.

Esta pasta e um projeto separado para o Vercel. Ela nao altera o app Android,
nao mexe no Expo Go e nao substitui o mobile original.

## 1. Rodar localmente

Instale as dependencias:

```powershell
cd "C:\Users\Sarah\Documents\app-serviços\admin-web"
npm install
```

Configure a URL da API local:

```powershell
$env:VITE_API_BASE_URL="http://192.168.1.108:8000/api/v1"
npm run dev
```

Abra:

```text
http://localhost:5173
```

O painel nao usa URL fixa no codigo. A API vem somente de:

```text
VITE_API_BASE_URL
```

## 2. Variavel de ambiente

Local:

```text
VITE_API_BASE_URL=http://192.168.1.108:8000/api/v1
```

Vercel:

```text
VITE_API_BASE_URL=https://SEU_BACKEND.vercel.app/api/v1
```

Nao coloque `localhost` nem `192.168...` no Vercel. Esses enderecos funcionam
apenas dentro da sua maquina ou rede local.

## 3. Subir no Vercel

Crie um novo projeto separado na mesma conta Vercel. Nao use o projeto
existente Sound Church.

Configuracao do projeto:

```text
Root Directory: admin-web
Framework Preset: Vite
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

Adicione a variavel:

```text
VITE_API_BASE_URL=https://SEU_BACKEND.vercel.app/api/v1
```

Depois clique em Deploy.

## 4. Testar login admin

Com o backend online funcionando, acesse o link do Vercel e entre com:

```text
email: admin@app.com
senha: Admin@123
```

Resultado esperado:

- login sem erro 404
- token salvo
- dashboard aberto
- cards principais carregando dados da API

Se aparecer "Nao foi possivel conectar com a API", confira a variavel
`VITE_API_BASE_URL` no Vercel.

## 5. Testar criacao de servico tabelado

No menu lateral, abra `Servicos`.

Para criar um servico:

1. escolha a categoria no select
2. preencha nome do servico
3. informe preco da mao de obra
4. informe tempo estimado em minutos
5. escreva uma descricao com pelo menos 10 caracteres
6. marque se precisa material
7. clique em `Criar servico`

O admin nao precisa digitar `categoria_id`. A categoria aparece como lista
visual carregada pela API.

Tambem valide:

- editar servico
- alterar preco
- alterar tempo estimado
- ativar/desativar servico
- mensagens amigaveis quando faltar algum campo
