import React from "react";
import { StyleSheet, Text } from "react-native";

import AppButton from "../components/AppButton";
import AppCard from "../components/AppCard";
import Header from "../components/Header";
import Screen from "../components/Screen";
import { colors, spacing } from "../theme";

export default function EscolhaPerfilScreen({ navigation }) {
  return (
    <Screen>
      <Header title="Criar conta" subtitle="Escolha como voce quer usar o app." showBack />
      <AppCard style={styles.card}>
        <Text style={styles.title}>Cliente</Text>
        <Text style={styles.description}>Quero pedir servicos e acompanhar tudo pelo app.</Text>
        <AppButton title="Sou cliente" onPress={() => navigation.navigate("Cadastro", { perfil: "cliente" })} />
      </AppCard>
      <AppCard style={styles.card}>
        <Text style={styles.title}>Prestador</Text>
        <Text style={styles.description}>Quero receber chamados e organizar meus servicos.</Text>
        <AppButton title="Sou prestador" variant="secondary" onPress={() => navigation.navigate("Cadastro", { perfil: "prestador" })} />
      </AppCard>
    </Screen>
  );
}

const styles = StyleSheet.create({
  card: {
    gap: spacing.md,
  },
  title: {
    color: colors.text,
    fontSize: 20,
    fontWeight: "900",
  },
  description: {
    color: colors.muted,
    fontSize: 15,
    lineHeight: 21,
  },
});
