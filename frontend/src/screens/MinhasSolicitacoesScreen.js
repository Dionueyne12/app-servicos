import React, { useCallback, useState } from "react";
import { View } from "react-native";
import { useFocusEffect } from "@react-navigation/native";

import { listMeusServicosPrestador, listSolicitacoes } from "../api/requests";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import Header from "../components/Header";
import LoadingState from "../components/LoadingState";
import Screen from "../components/Screen";
import ServiceCard from "../components/ServiceCard";
import { useAuth } from "../context/AuthContext";
import { spacing } from "../theme";
import { formatMoney, getNextStep, getSolicitacaoTitle } from "../utils/status";

export default function MinhasSolicitacoesScreen({ navigation }) {
  const { user } = useAuth();
  const isPrestador = user?.tipo_usuario === "prestador";
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
          const data = isPrestador ? await listMeusServicosPrestador() : await listSolicitacoes();
          if (active) {
            setItems(data);
          }
        } catch {
          if (active) {
            setError("Nao foi possivel carregar suas solicitacoes.");
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
    }, [isPrestador]),
  );

  return (
    <Screen>
      <Header title={isPrestador ? "Meus atendimentos" : "Minhas solicitacoes"} subtitle="Status e proximo passo sempre visiveis." />
      <ErrorMessage message={error} />
      {loading ? (
        <LoadingState message="Carregando solicitacoes..." />
      ) : items.length === 0 ? (
        <EmptyState
          title="Nada por aqui"
          description={isPrestador ? "Quando voce aceitar servicos, eles aparecerao aqui." : "Sua proxima solicitacao aparecera aqui."}
          actionLabel={isPrestador ? "Ver disponiveis" : "Solicitar servico"}
          onAction={() => navigation.navigate(isPrestador ? "ServicosDisponiveis" : "CriarSolicitacao")}
        />
      ) : (
        <View style={{ gap: spacing.md }}>
          {items.map((item) => (
            <ServiceCard
              key={item.id}
              title={getSolicitacaoTitle(item)}
              description={item.descricao_problema}
              status={item.status}
              price={formatMoney(item.valor_total_estimado || item.valor_mao_obra)}
              nextStep={getNextStep(item.status, user?.tipo_usuario)}
              onPress={() => navigation.navigate("DetalheSolicitacao", { solicitacaoId: item.id })}
            />
          ))}
        </View>
      )}
    </Screen>
  );
}
