import React from "react";
import { StyleSheet, Text, View } from "react-native";

import { colors, spacing } from "../theme";
import AppCard from "./AppCard";
import AppButton from "./AppButton";

export default function EmptyState({ title, description, actionLabel, onAction }) {
  return (
    <AppCard style={styles.card}>
      <View style={styles.icon}>
        <Text style={styles.iconText}>+</Text>
      </View>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.description}>{description}</Text>
      {actionLabel ? <AppButton title={actionLabel} onPress={onAction} /> : null}
    </AppCard>
  );
}

const styles = StyleSheet.create({
  card: {
    alignItems: "center",
    gap: spacing.md,
  },
  icon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.softBlue,
    alignItems: "center",
    justifyContent: "center",
  },
  iconText: {
    color: colors.primary,
    fontSize: 26,
    fontWeight: "800",
  },
  title: {
    color: colors.text,
    fontSize: 18,
    fontWeight: "800",
    textAlign: "center",
  },
  description: {
    color: colors.muted,
    fontSize: 14,
    textAlign: "center",
    lineHeight: 20,
  },
});
