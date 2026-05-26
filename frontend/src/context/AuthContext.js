import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";

import { setAuthToken } from "../api/client";
import { cadastroRequest, loginRequest, meRequest } from "../api/auth";

const AuthContext = createContext(null);
const TOKEN_KEY = "@app_servicos_token";
const USER_KEY = "@app_servicos_user";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function restoreSession() {
      try {
        const savedToken = await AsyncStorage.getItem(TOKEN_KEY);
        const savedUser = await AsyncStorage.getItem(USER_KEY);
        if (savedToken) {
          setAuthToken(savedToken);
          const profile = await meRequest();
          const hydratedUser = buildUser(profile);
          setToken(savedToken);
          setUser(hydratedUser);
          await AsyncStorage.setItem(USER_KEY, JSON.stringify(hydratedUser));
          return;
        }
        if (savedUser) {
          setUser(JSON.parse(savedUser));
        }
      } catch {
        await AsyncStorage.multiRemove([TOKEN_KEY, USER_KEY]);
        setAuthToken(null);
      } finally {
        setIsLoading(false);
      }
    }

    restoreSession();
  }, []);

  async function signIn(email, senha) {
    const profile = await loginRequest(email, senha);
    const authenticatedUser = buildUser(profile);
    setToken(profile.token);
    setUser(authenticatedUser);
    await AsyncStorage.setItem(TOKEN_KEY, profile.token);
    await AsyncStorage.setItem(USER_KEY, JSON.stringify(authenticatedUser));
  }

  async function signUp(profile, payload) {
    await cadastroRequest(profile, payload);
    await signIn(payload.email, payload.senha);
  }

  async function refreshProfile() {
    const profile = await meRequest();
    const refreshedUser = buildUser(profile);
    setUser(refreshedUser);
    await AsyncStorage.setItem(USER_KEY, JSON.stringify(refreshedUser));
    return refreshedUser;
  }

  async function signOut() {
    setToken(null);
    setUser(null);
    setAuthToken(null);
    await AsyncStorage.multiRemove([TOKEN_KEY, USER_KEY]);
  }

  const value = useMemo(
    () => ({
      user,
      token,
      isLoading,
      isAuthenticated: Boolean(token),
      signIn,
      signUp,
      refreshProfile,
      signOut,
    }),
    [user, token, isLoading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}

function buildUser(profile) {
  return {
    ...profile.usuario,
    cliente_id: profile.cliente_id,
    prestador_id: profile.prestador_id,
    status_validacao_prestador: profile.status_validacao_prestador,
  };
}
