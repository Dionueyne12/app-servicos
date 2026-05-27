import axios from "axios";

const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL;
export const API_BASE_URL = normalizeApiBaseUrl(rawApiBaseUrl);

if (!API_BASE_URL) {
  console.error("[ADMIN API] VITE_API_BASE_URL nao configurada.");
} else {
  console.log("API BASE URL:", API_BASE_URL);
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
  if (!API_BASE_URL) {
    const error = new Error("VITE_API_BASE_URL nao configurada.");
    error.code = "ERR_ADMIN_API_BASE_URL";
    throw error;
  }

  console.log("[ADMIN API] request", {
    apiBaseUrlUsada: API_BASE_URL,
    method: config.method,
    endpointChamado: buildLogUrl(config.baseURL, config.url),
    params: config.params,
    data: maskSensitive(config.data),
  });
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.log("[ADMIN API] erro", {
      apiBaseUrlUsada: API_BASE_URL,
      endpointChamado: buildLogUrl(error?.config?.baseURL, error?.config?.url),
      code: error?.code,
      status: error?.response?.status,
      mensagem: error?.message,
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

function normalizeApiBaseUrl(value) {
  if (!value || typeof value !== "string") return "";

  const trimmed = value.trim();
  if (!trimmed || trimmed === "undefined") return "";

  let url;
  try {
    url = new URL(trimmed);
  } catch {
    return "";
  }

  url.hash = "";
  url.search = "";
  url.pathname = normalizeApiPath(url.pathname);
  return url.toString().replace(/\/+$/, "");
}

function normalizeApiPath(pathname) {
  const cleanPath = String(pathname || "").replace(/\/+$/, "");
  if (!cleanPath || cleanPath === "/") return "/api/v1";
  if (cleanPath === "/docs" || cleanPath === "/openapi.json") return "/api/v1";
  if (cleanPath.endsWith("/api/v1")) return cleanPath;
  if (cleanPath.endsWith("/api")) return `${cleanPath}/v1`;
  if (cleanPath.includes("/api/v1/")) return cleanPath.slice(0, cleanPath.indexOf("/api/v1/") + "/api/v1".length);
  if (cleanPath.includes("/api/")) return cleanPath.slice(0, cleanPath.indexOf("/api/") + "/api".length) + "/v1";
  return `${cleanPath}/api/v1`;
}

function buildLogUrl(baseUrl = "", path = "") {
  if (!baseUrl) return path || "";
  if (!path) return baseUrl;
  return `${String(baseUrl).replace(/\/+$/, "")}/${String(path).replace(/^\/+/, "")}`;
}
