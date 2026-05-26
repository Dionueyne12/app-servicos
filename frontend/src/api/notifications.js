import { api } from "./client";

export async function listNotificacoes() {
  const { data } = await api.get("/notificacoes");
  return data;
}
