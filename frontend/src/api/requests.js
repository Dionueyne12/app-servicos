import { api } from "./client";

export async function listSolicitacoes() {
  const { data } = await api.get("/solicitacoes");
  return data.items || [];
}

export async function listSolicitacoesDisponiveis() {
  const { data } = await api.get("/solicitacoes/disponiveis");
  return data.items || [];
}

export async function listMeusServicosPrestador() {
  const { data } = await api.get("/prestadores/meus-servicos");
  return data.items || [];
}

export async function getSolicitacao(id) {
  const { data } = await api.get(`/solicitacoes/${id}`);
  return data;
}

export async function createSolicitacao(payload) {
  const { data } = await api.post("/solicitacoes", payload);
  return data;
}

export async function uploadFotoSolicitacao(solicitacaoId, foto) {
  const response = await fetch(foto.uri);
  const blob = await response.blob();
  const mimeType = foto.mimeType || inferMimeType(foto);
  const nomeOriginal = foto.fileName || `foto-${Date.now()}.${mimeType.split("/")[1] || "jpg"}`;
  const { data } = await api.post(`/solicitacoes/${solicitacaoId}/fotos`, blob, {
    params: {
      nome_original: nomeOriginal,
      mime_type: mimeType,
      tipo_foto: "problema",
    },
    headers: {
      "Content-Type": "application/octet-stream",
    },
    timeout: 20000,
  });
  return data;
}

export async function aceitarSolicitacao(id) {
  const { data } = await api.post(`/solicitacoes/${id}/aceitar`);
  return data;
}

export async function iniciarSolicitacao(id) {
  const { data } = await api.patch(`/solicitacoes/${id}/iniciar`);
  return data;
}

export async function concluirSolicitacao(id) {
  const { data } = await api.patch(`/solicitacoes/${id}/concluir`);
  return data;
}

function inferMimeType(foto) {
  const value = `${foto.fileName || ""} ${foto.uri || ""}`.toLowerCase();
  if (value.includes(".png")) return "image/png";
  if (value.includes(".webp")) return "image/webp";
  return "image/jpeg";
}
