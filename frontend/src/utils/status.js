export const statusLabels = {
  aguardando_prestador: "Aguardando prestador",
  aceito: "Aceito",
  aguardando_aprovacao_cliente: "Aguardando aprovacao",
  material_aprovado: "Material aprovado",
  em_andamento: "Em andamento",
  aguardando_confirmacao_cliente: "Aguardando confirmacao",
  concluido: "Concluido",
  cancelado: "Cancelado",
  em_analise: "Em analise",
};

export function getStatusLabel(status) {
  return statusLabels[status] || "Em andamento";
}

export function getNextStep(status, userType = "cliente") {
  if (userType === "prestador") {
    const providerSteps = {
      aguardando_prestador: "Abra os detalhes e aceite apenas se puder atender.",
      aceito: "Informe o material ou inicie o servico quando estiver pronto.",
      aguardando_aprovacao_cliente: "Aguarde o cliente aprovar o material.",
      material_aprovado: "Material aprovado. Proximo passo: iniciar.",
      em_andamento: "Finalize quando o servico estiver pronto.",
      aguardando_confirmacao_cliente: "Aguarde a confirmacao do cliente.",
      concluido: "Servico concluido.",
    };
    return providerSteps[status] || "Acompanhe o andamento do servico.";
  }

  const clientSteps = {
    aguardando_prestador: "Aguardando um prestador aceitar.",
    aceito: "Prestador aceitou. Agora combine material e horario.",
    aguardando_aprovacao_cliente: "Revise e aprove o material informado.",
    material_aprovado: "Material aprovado. Aguarde o inicio.",
    em_andamento: "Servico em andamento.",
    aguardando_confirmacao_cliente: "Confira o servico e confirme a conclusao.",
    concluido: "Servico concluido.",
    em_analise: "Seu problema esta em analise.",
  };
  return clientSteps[status] || "Acompanhe o proximo passo.";
}

export function getSolicitacaoTitle(solicitacao) {
  if (!solicitacao) {
    return "Solicitacao";
  }
  if (solicitacao.tipo_servico === "tabelado") {
    return "Servico tabelado";
  }
  return solicitacao.descricao_problema?.slice(0, 48) || "Servico personalizado";
}

export function formatMoney(value) {
  if (value === null || value === undefined) {
    return null;
  }
  return `R$ ${Number(value).toFixed(2).replace(".", ",")}`;
}
