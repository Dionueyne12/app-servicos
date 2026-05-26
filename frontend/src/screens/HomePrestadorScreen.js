import React, { useCallback, useState } from "react";
import { StyleSheet, Text } from "react-native";
import { useFocusEffect } from "@react-navigation/native";

import { listSolicitacoesDisponiveis } from "../api/requests";
import AppButton from "../components/AppButton";
import AppCard from "../components/AppCard";
import Header from "../components/Header";
import LoadingState from "../components/LoadingState";
import Screen from "../components/Screen";
import ServiceCard from "../components/ServiceCard";
import { useAuth } from "../context/AuthContext";
import { colors, spacing } from "../theme";
import { logoutAndGoToLogin } from "../utils/logout";
import { formatMoney, getNextStep, getSolicitacaoTitle } from "../utils/status";

export default function HomePrestadorScreen({ navigation }) {
  const { user, refreshProfile, signOut } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useFocusEffect(
    useCallback(() => {
      let active = true;
      async function load() {
        if (user?.status_validacao_prestador && user.status_validacao_prestador !== "aprovado") {
          setItems([]);
          setLoading(false);
          return;
        }
        setLoading(true);
        try {
          const data = await listSolicitacoesDisponiveis();
          if (active) {
            setItems(data);
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
    }, [user?.status_validacao_prestador]),
  );

  const first = items[0];
  const aguardandoAprovacao = user?.status_validacao_prestador && user.status_validacao_prestador !== "aprovado";

  if (aguardandoAprovacao) {
    return (
      <Screen>
        <Header title="Bom trabalho" subtitle="Seu cadastro esta em analise." />
        <AppCard style={styles.card}>
          <Text style={styles.title}>Cadastro aguardando aprovacao</Text>
          <Text style={styles.text}>O administrador precisa aprovar seu cadastro antes de voce aceitar servicos.</Text>
          <AppButton title="Atualizar status" onPress={refreshProfile} />
          <AppButton title="Voltar para inicio" variant="secondary" onPress={() => navigation.navigate("HomePrestador")} />
          <AppButton title="Sair ou trocar conta" variant="secondary" onPress={() => logoutAndGoToLogin(signOut)} />
        </AppCard>
      </Screen>
    );
  }

  return (
    <Screen>
      <Header title="Bom trabalho" subtitle="Veja oportunidades perto de voce." />
      <AppCard style={styles.card}>
        <Text style={styles.metric}>{items.length}</Text>
        <Text style={styles.title}>Servicos disponiveis</Text>
        <Text style={styles.text}>Abra um chamado, confira os detalhes e aceite se puder atender.</Text>
        <AppButton title="Ver servicos" onPress={() => navigation.navigate("ServicosDisponiveis")} />
        <AppButton title="Sair ou trocar conta" variant="secondary" onPress={() => logoutAndGoToLogin(signOut)} />
      </AppCard>
      {loading ? <LoadingState message="Buscando oportunidades..." /> : null}
      {first ? (
        <ServiceCard
          title={getSolicitacaoTitle(first)}
          description={first.descricao_problema}
          status={first.status}
          price={formatMoney(first.valor_total_estimado || first.valor_mao_obra)}
          nextStep={getNextStep(first.status, "prestador")}
          onPress={() => navigation.navigate("DetalheSolicitacao", { solicitacaoId: first.id })}
        />
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  card: {
    gap: spacing.md,
  },
  metric: {
    color: colors.primary,
    fontSize: 36,
    fontWeight: "900",
  },
  title: {
    color: colors.text,
    fontSize: 20,
    fontWeight: "900",
  },
  text: {
    color: colors.muted,
    fontSize: 15,
    lineHeight: 21,
  },
});
