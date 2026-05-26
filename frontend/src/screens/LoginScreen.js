import React, { useState } from "react";
import { StyleSheet, Text, View } from "react-native";

import AppButton from "../components/AppButton";
import ErrorMessage from "../components/ErrorMessage";
import AppInput from "../components/AppInput";
import Header from "../components/Header";
import Screen from "../components/Screen";
import { useAuth } from "../context/AuthContext";
import { colors, spacing } from "../theme";
import { API_BASE_URL } from "../api/client";
import { getApiErrorMessage, logApiError } from "../utils/apiError";

export default function LoginScreen({ navigation }) {
  const { signIn } = useAuth();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [mostrarSenha, setMostrarSenha] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin() {
    setError("");
    setLoading(true);
    try {
      console.log("[Login] tentando entrar", { baseURL: API_BASE_URL, email: email.trim() });
      await signIn(email.trim(), senha);
    } catch (err) {
      logApiError("Login", err, { baseURL: API_BASE_URL, email: email.trim() });
      setError(getApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <Screen>
      <Header title="Bem-vindo" subtitle="Entre para solicitar ou aceitar servicos." />
      <View style={styles.form}>
        <AppInput
          label="E-mail"
          placeholder="seuemail@exemplo.com"
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
        />
        <AppInput
          label="Senha"
          placeholder="Sua senha"
          value={senha}
          onChangeText={setSenha}
          secureTextEntry={!mostrarSenha}
          rightLabel={mostrarSenha ? "Ocultar" : "Ver"}
          onRightPress={() => setMostrarSenha((current) => !current)}
          autoCapitalize="none"
        />
      </View>
      <ErrorMessage message={error} />
      <AppButton title={loading ? "Entrando..." : "Entrar"} onPress={handleLogin} disabled={loading} />
      <Text style={styles.helper}>Use o e-mail e senha cadastrados no backend FastAPI.</Text>
      <AppButton title="Criar conta" variant="secondary" onPress={() => navigation.navigate("EscolhaPerfil")} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  form: {
    gap: spacing.lg,
  },
  helper: {
    color: colors.muted,
    fontSize: 13,
    lineHeight: 19,
    textAlign: "center",
  },
});
