import axios from "axios";

export const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL;

if (!API_BASE_URL) {
  console.error(
    "[API] EXPO_PUBLIC_API_BASE_URL nao foi configurada. No Expo Go Android use o IP da maquina, por exemplo: http://192.168.1.108:8000/api/v1",
  );
} else {
  console.log("[API] API BASE URL carregada:", API_BASE_URL);
}

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  const finalUrl = `${config.baseURL || ""}${config.url || ""}`;
  console.log("[API] request", {
    method: config.method,
    url: finalUrl,
    payload: maskSensitiveData(config.data),
  });
  return config;
});

api.interceptors.response.use(
  (response) => {
    console.log("[API] response", {
      status: response.status,
      url: `${response.config.baseURL || ""}${response.config.url || ""}`,
      data: response.data,
    });
    return response;
  },
  (error) => {
    console.log("[API] response error", {
      message: error?.message,
      status: error?.response?.status,
      url: `${error?.config?.baseURL || ""}${error?.config?.url || ""}`,
      data: error?.response?.data,
    });
    return Promise.reject(error);
  },
);

export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
    return;
  }
  delete api.defaults.headers.common.Authorization;
}

function maskSensitiveData(data) {
  if (!data) {
    return data;
  }
  if (typeof data === "object" && (data.size || data._data || data.type?.startsWith?.("image/"))) {
    return {
      tipo: "arquivo",
      tamanho: data.size,
      mimeType: data.type,
    };
  }
  try {
    const parsed = typeof data === "string" ? JSON.parse(data) : data;
    if (parsed?.senha) {
      return { ...parsed, senha: "***" };
    }
    return parsed;
  } catch {
    return data;
  }
}
