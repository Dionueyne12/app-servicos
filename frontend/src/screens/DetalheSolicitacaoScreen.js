import React, { useCallback, useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import { useFocusEffect } from "@react-navigation/native";

import { aceitarSolicitacao, concluirSolicitacao, getSolicitacao, iniciarSolicitacao } from "../api/requests";
import AppButton from "../components/AppButton";
import AppCard from "../components/AppCard";
import ErrorMessage from "../components/ErrorMessage";
import Header from "../components/Header";
import LoadingState from "../components/LoadingState";
import Screen from "../components/Screen";
import StatusBadge from "../components/StatusBadge";
import StepIndicator from "../components/StepIndicator";
import { useAuth } from "../context/AuthContext";
import { colors, spacing } from "../theme";
import { formatMoney, getNextStep, getSolicitacaoTitle } from "../utils/status";

export default function DetalheSolicitacaoScreen({ navigation, route }) {
  const { user } = useAuth();
  const isPrestador = user?.tipo_usuario === "prestador";
  const solicitacaoId = route.params?.solicitacaoId;
  const [solicitacao, setSolicitacao] = useState(route.params?.solicitacao || null);
  const [loading, setLoading] = useState(Boolean(solicitacaoId));
  const [error, setError] = useState("");
  const [actionLoading, setActionLoading] = useState(false);

  const load = useCallback(async () => {
    if (!solicitacaoId) {
      return;
    }
    setLoading(true);
    setError("");
    try {
      setSolicitacao(await getSolicitacao(solicitacaoId));
    } catch {
      setError("Nao foi possivel carregar os detalhes.");
    } finally {
      setLoading(false);
    }
  }, [solicitacaoId]);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load]),
  );

  async function runAction(action) {
    if (!solicitacao?.id) {
      return;
    }
    setActionLoading(true);
    setError("");
    try {
      const updated = await action(solicitacao.id);
      setSolicitacao(updated);
    } catch {
      setError("Nao foi possivel executar esta acao agora.");
    } finally {
      setActionLoading(false);
    }
  }

  if (loading) {
    return (
      <Screen>
        <Header title="Detalhes" showBack />
        <LoadingState message="Carregando solicitacao..." />
      </Screen>
    );
  }

  if (!solicitacao) {
    return (
      <Screen>
        <Header title="Detalhes" showBack />
        <ErrorMessage message={error || "Solicitacao nao encontrada."} />
        <AppButton title="Tentar novamente" onPress={load} />
        <AppButton title="Voltar para inicio" variant="secondary" onPress={() => navigation.navigate(isPrestador ? "PrestadorTabs" : "ClienteTabs")} />
      </Screen>
    );
  }

  return (
    <Screen>
      <Header title="Detalhes" subtitle="Status e proximo passo em um lugar so." showBack />
      <ErrorMessage message={error} />
      <AppCard style={styles.card}>
        <View style={styles.top}>
          <Text style={styles.title}>{getSolicitacaoTitle(solicitacao)}</Text>
          <StatusBadge status={solicitacao.status} />
        </View>
        <Text style={styles.description}>{solicitacao.descricao_problema}</Text>
        <StepIndicator steps={["Pedido", "Aguardando", "Execucao", "Finalizacao"]} current={stepFromStatus(solicitacao.status)} />
      </AppCard>
      <AppCard style={styles.card}>
        <Text style={styles.sectionTitle}>Proximo passo</Text>
        <Text style={styles.description}>{getNextStep(solicitacao.status, user?.tipo_usuario)}</Text>
        <Text style={styles.price}>Total estimado: {formatMoney(solicitacao.valor_total_estimado || solicitacao.valor_mao_obra) || "A definir"}</Text>
        {isPrestador ? (
          <>
            <PrestadorActions status={solicitacao.status} loading={actionLoading} onAction={runAction} />
            <AppButton title="Ir para inicio" variant="secondary" onPress={() => navigation.navigate("PrestadorTabs", { screen: "HomePrestador" })} />
            <AppButton title="Meus atendimentos" variant="secondary" onPress={() => navigation.navigate("PrestadorTabs", { screen: "MeusServicos" })} />
          </>
        ) : (
          <>
            <AppButton title="Atualizar detalhes" variant="secondary" onPress={load} />
            <AppButton title="Ir para inicio" variant="secondary" onPress={() => navigation.navigate("ClienteTabs", { screen: "HomeCliente" })} />
            <AppButton title="Ver meus pedidos" onPress={() => navigation.navigate("ClienteTabs", { screen: "MinhasSolicitacoes" })} />
          </>
        )}
      </AppCard>
    </Screen>
  );
}

function PrestadorActions({ status, loading, onAction }) {
  if (status === "aguardando_prestador") {
    return <AppButton title={loading ? "Aceitando..." : "Aceitar servico"} onPress={() => onAction(aceitarSolicitacao)} disabled={loading} />;
  }
  if (status === "aceito" || status === "material_aprovado") {
    return <AppButton title={loading ? "Iniciando..." : "Iniciar servico"} onPress={() => onAction(iniciarSolicitacao)} disabled={loading} />;
  }
  if (status === "em_andamento") {
    return <AppButton title={loading ? "Concluindo..." : "Concluir servico"} onPress={() => onAction(concluirSolicitacao)} disabled={loading} />;
  }
  return <AppButton title="Acompanhar andamento" variant="secondary" disabled />;
}

function stepFromStatus(status) {
  if (status === "aguardando_prestador") return 1;
  if (status === "aceito" || status === "aguardando_aprovacao_cliente" || status === "material_aprovado") return 1;
  if (status === "em_andamento") return 2;
  return 3;
}

const styles = StyleSheet.create({
  card: {
    gap: spacing.lg,
  },
  top: {
    gap: spacing.sm,
  },
  title: {
    color: colors.text,
    fontSize: 22,
    fontWeight: "900",
  },
  description: {
    color: colors.muted,
    fontSize: 15,
    lineHeight: 22,
  },
  sectionTitle: {
    color: colors.text,
    fontSize: 18,
    fontWeight: "900",
  },
  price: {
    color: colors.text,
    fontSize: 15,
    fontWeight: "900",
  },
});
