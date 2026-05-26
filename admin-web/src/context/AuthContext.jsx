import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { getMe, loginAdmin } from "../api/admin";
import { setAuthToken, setUnauthorizedHandler } from "../api/client";

const AuthContext = createContext(null);
const TOKEN_KEY = "app_servicos_admin_token";
const USER_KEY = "app_servicos_admin_user";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState(loadUser());
  const [loading, setLoading] = useState(Boolean(token));

  useEffect(() => {
    setUnauthorizedHandler(logout);
    if (!token) {
      setLoading(false);
      return;
    }
    setAuthToken(token);
    refreshAdmin().finally(() => setLoading(false));
  }, []);

  async function signIn(email, senha) {
    const auth = await loginAdmin(email.trim().toLowerCase(), senha);
    setAuthToken(auth.access_token);
    const profile = await getMe();
    if (profile.usuario?.tipo_usuario !== "admin") {
      setAuthToken(null);
      throw new Error("Acesso negado. Esta conta nao e de administrador.");
    }
    localStorage.setItem(TOKEN_KEY, auth.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(profile.usuario));
    setToken(auth.access_token);
    setUser(profile.usuario);
  }

  async function refreshAdmin() {
    try {
      const profile = await getMe();
      if (profile.usuario?.tipo_usuario !== "admin") {
        logout();
        return;
      }
      localStorage.setItem(USER_KEY, JSON.stringify(profile.usuario));
      setUser(profile.usuario);
    } catch {
      logout();
    }
  }

  function logout() {
    console.log("[ADMIN AUTH] logout");
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setAuthToken(null);
    setToken(null);
    setUser(null);
  }

  const value = useMemo(
    () => ({
      token,
      user,
      loading,
      isAuthenticated: Boolean(token && user?.tipo_usuario === "admin"),
      signIn,
      logout,
    }),
    [token, user, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}

function loadUser() {
  try {
    const saved = localStorage.getItem(USER_KEY);
    return saved ? JSON.parse(saved) : null;
  } catch {
    return null;
  }
}
