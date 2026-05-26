import React from "react";
import { StyleSheet, Text, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";

import AppButton from "../components/AppButton";
import AppCard from "../components/AppCard";
import Header from "../components/Header";
import Screen from "../components/Screen";
import { colors, spacing } from "../theme";

export default function SucessoSolicitacaoScreen({ navigation, route }) {
  const solicitacaoId = route.params?.solicitacaoId;

  return (
    <Screen>
      <Header title="Pedido enviado" subtitle="Agora e so acompanhar o status." showBack />
      <AppCard style={styles.card}>
        <View style={styles.icon}>
          <Ionicons name="checkmark" size={34} color={colors.card} />
        </View>
        <Text style={styles.title}>Solicitacao criada com sucesso</Text>
        <Text style={styles.text}>Seu pedido ja esta no sistema e aguardando um prestador aceitar.</Text>
      </AppCard>
      <AppButton
        title="Ver solicitacao"
        onPress={() => navigation.replace("DetalheSolicitacao", { solicitacaoId })}
      />
      <AppButton
        title="Voltar para inicio"
        variant="secondary"
        onPress={() => navigation.navigate("ClienteTabs", { screen: "HomeCliente" })}
      />
      <AppButton
        title="Ver meus pedidos"
        variant="secondary"
        onPress={() => navigation.navigate("ClienteTabs", { screen: "MinhasSolicitacoes" })}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  card: {
    alignItems: "center",
    gap: spacing.md,
  },
  icon: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: colors.success,
    alignItems: "center",
    justifyContent: "center",
  },
  title: {
    color: colors.text,
    fontSize: 22,
    fontWeight: "900",
    textAlign: "center",
  },
  text: {
    color: colors.muted,
    fontSize: 15,
    lineHeight: 22,
    textAlign: "center",
  },
});
