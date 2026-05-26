import React from "react";
import { ActivityIndicator, StyleSheet, Text, View } from "react-native";

import { colors, spacing } from "../theme";

export default function LoadingState({ message = "Carregando..." }) {
  return (
    <View style={styles.container}>
      <ActivityIndicator color={colors.primary} />
      <Text style={styles.text}>{message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.md,
    padding: spacing.xl,
  },
  text: {
    color: colors.muted,
    fontSize: 14,
  },
});
