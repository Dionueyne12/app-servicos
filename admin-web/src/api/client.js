import axios from "axios";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_BASE_URL) {
  console.error("[ADMIN API] VITE_API_BASE_URL nao configurada.");
} else {
  console.log("[ADMIN API] URL carregada:", API_BASE_URL);
}

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

let onUnauthorized = null;

export function setUnauthorizedHandler(handler) {
  onUnauthorized = handler;
}

export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
    return;
  }
  delete api.defaults.headers.common.Authorization;
}

api.interceptors.request.use((config) => {
  console.log("[ADMIN API] request", {
    method: config.method,
    url: `${config.baseURL || ""}${config.url || ""}`,
    params: config.params,
    data: maskSensitive(config.data),
  });
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.log("[ADMIN API] erro", {
      status: error?.response?.status,
      url: `${error?.config?.baseURL || ""}${error?.config?.url || ""}`,
      data: error?.response?.data,
    });
    if (error?.response?.status === 401 && onUnauthorized) {
      onUnauthorized();
    }
    return Promise.reject(error);
  },
);

function maskSensitive(data) {
  if (!data || typeof data !== "object") return data;
  if (data.senha) return { ...data, senha: "***" };
  return data;
}
