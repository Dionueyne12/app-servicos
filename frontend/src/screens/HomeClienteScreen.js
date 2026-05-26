import React, { useCallback, useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import { useFocusEffect } from "@react-navigation/native";

import { listSolicitacoes } from "../api/requests";
import AppButton from "../components/AppButton";
import AppCard from "../components/AppCard";
import Header from "../components/Header";
import LoadingState from "../components/LoadingState";
import Screen from "../components/Screen";
import ServiceCard from "../components/ServiceCard";
import StepIndicator from "../components/StepIndicator";
import { useAuth } from "../context/AuthContext";
import { colors, spacing } from "../theme";
import { logoutAndGoToLogin } from "../utils/logout";
import { formatMoney, getNextStep, getSolicitacaoTitle } from "../utils/status";

export default function HomeClienteScreen({ navigation }) {
  const { user, signOut } = useAuth();
  const [latest, setLatest] = useState(null);
  const [loading, setLoading] = useState(true);

  useFocusEffect(
    useCallback(() => {
      let active = true;
      async function load() {
        setLoading(true);
        try {
          const items = await listSolicitacoes();
          if (active) {
            setLatest(items[0] || null);
          }
        } finally {
          if (active) {
            setLoading(false);
          }
        }
      }
      load();
      return () => {
        active = false;
      };
    }, []),
  );

  return (
    <Screen>
      <Header title={`Ola, ${user?.nome?.split(" ")[0] || "cliente"}`} subtitle="Qual servico voce precisa hoje?" />
      <AppCard style={styles.hero}>
        <Text style={styles.heroTitle}>Solicite em poucos passos</Text>
        <Text style={styles.heroText}>Descreva o problema, escolha o material e acompanhe o servico.</Text>
        <StepIndicator steps={["Pedido", "Aguardando", "Execucao", "Finalizacao"]} current={latest ? stepFromStatus(latest.status) : 0} />
        <AppButton title="Solicitar servico" onPress={() => navigation.navigate("CriarSolicitacao")} />
        <AppButton title="Meus pedidos" variant="secondary" onPress={() => navigation.navigate("MinhasSolicitacoes")} />
        <AppButton
          title="Acompanhar"
          variant="secondary"
          onPress={() =>
            latest
              ? navigation.navigate("DetalheSolicitacao", { solicitacaoId: latest.id })
              : navigation.navigate("MinhasSolicitacoes")
          }
        />
        <AppButton title="Perfil" variant="secondary" onPress={() => navigation.navigate("Perfil")} />
        <AppButton title="Sair ou trocar conta" variant="secondary" onPress={() => logoutAndGoToLogin(signOut)} />
      </AppCard>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Ultimo servico</Text>
        {loading ? (
          <LoadingState message="Buscando suas solicitacoes..." />
        ) : latest ? (
          <ServiceCard
            title={getSolicitacaoTitle(latest)}
            description={latest.descricao_problema}
            status={latest.status}
            price={formatMoney(latest.valor_total_estimado || latest.valor_mao_obra)}
            nextStep={getNextStep(latest.status, "cliente")}
            onPress={() => navigation.navigate("DetalheSolicitacao", { solicitacaoId: latest.id })}
          />
        ) : (
          <Text style={styles.emptyText}>Voce ainda nao tem solicitacoes. Toque em Solicitar servico para comecar.</Text>
        )}
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  hero: {
    gap: spacing.lg,
  },
  heroTitle: {
    color: colors.text,
    fontSize: 22,
    fontWeight: "900",
  },
  heroText: {
    color: colors.muted,
    fontSize: 15,
    lineHeight: 21,
  },
  section: {
    gap: spacing.md,
  },
  sectionTitle: {
    color: colors.text,
    fontSize: 18,
    fontWeight: "900",
  },
  emptyText: {
    color: colors.muted,
    fontSize: 14,
    lineHeight: 20,
  },
});

function stepFromStatus(status) {
  if (status === "aguardando_prestador") return 1;
  if (status === "em_andamento") return 2;
  if (status === "concluido") return 3;
  return 1;
}
