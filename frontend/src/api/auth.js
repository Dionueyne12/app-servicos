import { api, setAuthToken } from "./client";

export async function loginRequest(email, senha) {
  const { data } = await api.post("/auth/login", { email, senha });
  setAuthToken(data.access_token);
  const profile = await meRequest();
  return {
    token: data.access_token,
    usuario: profile.usuario,
    cliente_id: profile.cliente_id,
    prestador_id: profile.prestador_id,
    status_validacao_prestador: profile.status_validacao_prestador,
  };
}

export async function cadastroRequest(perfil, payload) {
  const path = perfil === "prestador" ? "/prestadores/cadastro" : "/clientes/cadastro";
  console.log("[API cadastro]", { path, payload: { ...payload, senha: "***" } });
  const { data } = await api.post(path, payload);
  return data;
}

export async function meRequest() {
  const { data } = await api.get("/auth/me");
  return data;
}
