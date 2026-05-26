import React, { useCallback, useState } from "react";
import { View } from "react-native";
import { useFocusEffect } from "@react-navigation/native";

import { listSolicitacoesDisponiveis } from "../api/requests";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import Header from "../components/Header";
import LoadingState from "../components/LoadingState";
import Screen from "../components/Screen";
import ServiceCard from "../components/ServiceCard";
import { spacing } from "../theme";
import { formatMoney, getNextStep, getSolicitacaoTitle } from "../utils/status";

export default function ServicosDisponiveisScreen({ navigation }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useFocusEffect(
    useCallback(() => {
      let active = true;
      async function load() {
        setLoading(true);
        setError("");
        try {
          const data = await listSolicitacoesDisponiveis();
          if (active) {
            setItems(data);
          }
        } catch {
          if (active) {
            setError("Nao foi possivel carregar servicos disponiveis.");
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
      <Header title="Disponiveis" subtitle="Abra os detalhes antes de aceitar." />
      <ErrorMessage message={error} />
      {loading ? (
        <LoadingState message="Buscando servicos..." />
      ) : items.length === 0 ? (
        <EmptyState title="Nenhum servico agora" description="Novas solicitacoes aparecerao aqui automaticamente." />
      ) : (
        <View style={{ gap: spacing.md }}>
          {items.map((item) => (
            <ServiceCard
              key={item.id}
              title={getSolicitacaoTitle(item)}
              description={item.descricao_problema}
              status={item.status}
              price={formatMoney(item.valor_total_estimado || item.valor_mao_obra)}
              nextStep={getNextStep(item.status, "prestador")}
              onPress={() => navigation.navigate("DetalheSolicitacao", { solicitacaoId: item.id })}
            />
          ))}
        </View>
      )}
    </Screen>
  );
}
