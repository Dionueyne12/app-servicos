export function money(value) {
  const amount = Number(value || 0);
  return amount.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

export function date(value) {
  if (!value) return "-";
  return new Date(value).toLocaleString("pt-BR");
}

export function statusLabel(value) {
  if (!value) return "-";
  return String(value).replaceAll("_", " ");
}

export function apiErrorMessage(error) {
  if (error?.code === "ERR_ADMIN_API_BASE_URL") {
    return "URL da API nao configurada. Ajuste VITE_API_BASE_URL no Vercel.";
  }
  if (error?.code === "ERR_NETWORK") return "Nao foi possivel conectar com a API. Verifique a URL configurada no painel.";
  if (error?.response?.status === 404) return "Rota inexistente. Verifique se a URL da API esta correta.";
  if (error?.response?.status === 403) return "Acesso negado. Use uma conta de administrador.";
  if (error?.response?.status === 401) return "E-mail ou senha invalidos.";
  if (error?.response?.status === 422) return validationMessage(error) || "Dados invalidos. Confira os campos e tente novamente.";
  if (error?.response?.status >= 500) return "A API encontrou um problema. Tente novamente em alguns instantes.";
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg;
  return "Nao foi possivel carregar os dados agora.";
}

function validationMessage(error) {
  const detail = error?.response?.data?.detail;
  if (!Array.isArray(detail) || detail.length === 0) return "";
  const first = detail[0];
  const field = Array.isArray(first.loc) ? first.loc[first.loc.length - 1] : "";
  const fieldLabels = {
    categoria_id: "categoria",
    nome: "nome",
    descricao: "descricao",
    preco_mao_obra: "preco",
    tempo_estimado_minutos: "tempo estimado",
    email: "e-mail",
    senha: "senha",
  };
  if (first.msg) {
    return `${fieldLabels[field] || "Campo"}: ${first.msg}`;
  }
  return "";
}
