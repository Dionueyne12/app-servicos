import { api } from "./client";

export async function listServicosTabelados() {
  const { data } = await api.get("/servicos-tabelados");
  return data.items || [];
}
