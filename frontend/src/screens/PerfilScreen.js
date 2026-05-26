import React from "react";
import { StyleSheet, Text } from "react-native";

import AppButton from "../components/AppButton";
import AppCard from "../components/AppCard";
import Header from "../components/Header";
import Screen from "../components/Screen";
import { useAuth } from "../context/AuthContext";
import { colors, spacing } from "../theme";
import { logoutAndGoToLogin } from "../utils/logout";

export default function PerfilScreen() {
  const { user, signOut } = useAuth();

  return (
    <Screen>
      <Header title="Perfil" subtitle="Seus dados e preferencias do app." />
      <AppCard style={styles.card}>
        <Text style={styles.name}>{user?.nome || "Usuario"}</Text>
        <Text style={styles.role}>{user?.tipo_usuario === "prestador" ? "Prestador" : "Cliente"}</Text>
        {user?.tipo_usuario === "prestador" ? (
          <Text style={styles.validation}>
            Validacao: {user?.status_validacao_prestador === "aprovado" ? "aprovado" : "aguardando aprovacao"}
          </Text>
        ) : null}
        <Text style={styles.text}>Na proxima etapa, esta tela buscara os dados reais do backend.</Text>
      </AppCard>
      <AppButton title="Sair" variant="danger" onPress={() => logoutAndGoToLogin(signOut)} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  card: {
    gap: spacing.sm,
  },
  name: {
    color: colors.text,
    fontSize: 22,
    fontWeight: "900",
  },
  role: {
    color: colors.primary,
    fontSize: 15,
    fontWeight: "800",
  },
  validation: {
    color: colors.warning,
    fontSize: 14,
    fontWeight: "900",
  },
  text: {
    color: colors.muted,
    fontSize: 14,
    lineHeight: 20,
  },
});
