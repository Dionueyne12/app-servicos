import { api } from "./client";

export async function loginAdmin(email, senha) {
  const { data } = await api.post("/admin/login", { email, senha });
  return data;
}

export async function getMe() {
  const { data } = await api.get("/auth/me");
  return data;
}

export async function getDashboard() {
  const { data } = await api.get("/admin/dashboard");
  return data;
}

export async function getMetricas() {
  const { data } = await api.get("/admin/metricas");
  return data;
}

export async function getMonitoramento() {
  const { data } = await api.get("/admin/monitoramento");
  return data;
}

export async function listPrestadores(params = {}) {
  const { data } = await api.get("/admin/prestadores", { params });
  return data;
}

export async function listPrestadoresPendentes(params = {}) {
  const { data } = await api.get("/admin/prestadores/pendentes", { params });
  return data;
}

export async function approvePrestador(id) {
  const { data } = await api.patch(`/admin/prestadores/${id}/aprovar`);
  return data;
}

export async function rejectPrestador(id, observacao_admin) {
  const { data } = await api.patch(`/admin/prestadores/${id}/rejeitar`, { observacao_admin });
  return data;
}

export async function getPrestadorDocs(id) {
  const { data } = await api.get(`/admin/prestadores/${id}/documentos`);
  return data;
}

export async function listClientes(params = {}) {
  const { data } = await api.get("/admin/clientes", { params });
  return data;
}

export async function listSolicitacoes(params = {}) {
  const { data } = await api.get("/admin/solicitacoes", { params });
  return data;
}

export async function listServicos(params = {}) {
  const { data } = await api.get("/servicos-tabelados", { params });
  return data;
}

export async function listCategoriasServico(params = {}) {
  const { data } = await api.get("/categorias-servico", { params });
  return data;
}

export async function createServico(payload) {
  const { data } = await api.post("/servicos-tabelados", payload);
  return data;
}

export async function updateServico(id, payload) {
  const { data } = await api.put(`/servicos-tabelados/${id}`, payload);
  return data;
}

export async function setServicoAtivo(id, ativo) {
  const action = ativo ? "ativar" : "desativar";
  const { data } = await api.patch(`/servicos-tabelados/${id}/${action}`);
  return data;
}

export async function getFinanceiro(params = {}) {
  const { data } = await api.get("/admin/relatorios/financeiro", { params });
  return data;
}

export async function listRepasses(params = {}) {
  const { data } = await api.get("/admin/relatorios/repasses", { params });
  return data;
}
