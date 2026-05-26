import React, { useCallback, useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import { useFocusEffect } from "@react-navigation/native";

import { listNotificacoes } from "../api/notifications";
import AppCard from "../components/AppCard";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import Header from "../components/Header";
import LoadingState from "../components/LoadingState";
import Screen from "../components/Screen";
import { colors, spacing } from "../theme";

export default function NotificacoesScreen() {
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
          const data = await listNotificacoes();
          if (active) {
            setItems(data.items || []);
          }
        } catch {
          if (active) {
            setError("Nao foi possivel carregar os avisos.");
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
      <Header title="Avisos" subtitle="Somente o que precisa da sua atencao." />
      <ErrorMessage message={error} />
      {loading ? (
        <LoadingState message="Carregando avisos..." />
      ) : items.length === 0 ? (
        <EmptyState title="Tudo em dia" description="Quando algo importante acontecer, voce vera aqui." />
      ) : (
        <View style={styles.list}>
          {items.map((item) => (
            <AppCard key={item.id} style={styles.card}>
              <Text style={styles.title}>{item.titulo}</Text>
              <Text style={styles.text}>{item.mensagem}</Text>
            </AppCard>
          ))}
        </View>
      )}
    </Screen>
  );
}

const styles = StyleSheet.create({
  list: {
    gap: spacing.md,
  },
  card: {
    gap: spacing.xs,
  },
  title: {
    color: colors.text,
    fontSize: 16,
    fontWeight: "900",
  },
  text: {
    color: colors.muted,
    fontSize: 14,
    lineHeight: 20,
  },
});
