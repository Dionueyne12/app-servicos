export function getApiErrorMessage(error) {
  if (!error?.response) {
    return "Erro de conexao com o servidor. Confira se o backend esta ligado e se a URL da API esta correta.";
  }

  const status = error.response.status;
  const data = error.response.data;

  if (typeof data?.detail === "string") {
    return translateBackendMessage(data.detail);
  }

  if (Array.isArray(data?.detail)) {
    return translateValidationErrors(data.detail);
  }

  if (status === 409) {
    return "E-mail ja cadastrado. Use outro e-mail ou tente entrar.";
  }

  if (status >= 500) {
    return "Servidor indisponivel agora. Tente novamente em instantes.";
  }

  return "Nao foi possivel concluir. Revise os dados e tente novamente.";
}

export function logApiError(context, error, extra = {}) {
  console.log(`[${context}] erro completo`, {
    message: error?.message,
    status: error?.response?.status,
    data: error?.response?.data,
    extra,
  });
}

function translateBackendMessage(message) {
  const normalized = message.toLowerCase();
  if (normalized.includes("e-mail ja cadastrado")) {
    return "E-mail ja cadastrado. Use outro e-mail ou tente entrar.";
  }
  if (normalized.includes("senha deve conter")) {
    return "Senha fraca. Use pelo menos 8 caracteres com letra e numero.";
  }
  if (normalized.includes("telefone")) {
    return "Telefone invalido. Use DDD + numero, por exemplo 11999999999.";
  }
  if (normalized.includes("endereco") || normalized.includes("endereço")) {
    return "Endereco obrigatorio.";
  }
  if (normalized.includes("bairro")) {
    return "Bairro obrigatorio.";
  }
  if (normalized.includes("cidade")) {
    return "Cidade obrigatoria.";
  }
  if (normalized.includes("estado")) {
    return "Estado obrigatorio. Use a UF com 2 letras.";
  }
  if (normalized.includes("nome")) {
    return "Nome invalido. Use pelo menos 3 letras e nao coloque numeros.";
  }
  if (normalized.includes("e-mail invalido")) {
    return "E-mail invalido. Confira se digitou corretamente.";
  }
  return message;
}

function translateValidationErrors(errors) {
  const first = errors[0];
  const field = first?.loc?.[first.loc.length - 1];
  const message = first?.msg || "Campo obrigatorio ou invalido.";

  const labels = {
    nome: "Nome",
    email: "E-mail",
    telefone: "Telefone",
    senha: "Senha",
    endereco: "Endereco",
    bairro: "Bairro",
    documento: "Documento",
    cidade: "Cidade",
    estado: "Estado",
  };

  if (message.toLowerCase().includes("field required")) {
    return `${labels[field] || "Campo"} e obrigatorio.`;
  }
  if (field === "senha") {
    return "Senha invalida. Use pelo menos 8 caracteres com letra e numero.";
  }
  if (field === "telefone") {
    return "Telefone invalido. Use DDD + numero, por exemplo 11999999999.";
  }
  if (field === "email") {
    return "E-mail invalido. Confira se digitou corretamente.";
  }
  if (field === "endereco") {
    return "Endereco obrigatorio.";
  }
  if (field === "bairro") {
    return "Bairro obrigatorio.";
  }
  if (field === "cidade") {
    return "Cidade obrigatoria.";
  }
  if (field === "estado") {
    return "Estado obrigatorio. Use a UF com 2 letras.";
  }
  return `${labels[field] || "Campo"} invalido: ${message}`;
}
