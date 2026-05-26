import React from "react";
import { StyleSheet, Text, View } from "react-native";

import { colors, spacing } from "../theme";

export default function StepIndicator({ steps = [], current = 0 }) {
  return (
    <View style={styles.container}>
      {steps.map((step, index) => {
        const active = index <= current;
        return (
          <View key={step} style={styles.step}>
            <View style={[styles.dot, active && styles.activeDot]}>
              <Text style={[styles.number, active && styles.activeNumber]}>{index + 1}</Text>
            </View>
            <Text numberOfLines={1} style={[styles.label, active && styles.activeLabel]}>
              {step}
            </Text>
          </View>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    gap: spacing.sm,
  },
  step: {
    flex: 1,
    alignItems: "center",
    gap: spacing.xs,
  },
  dot: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.border,
    alignItems: "center",
    justifyContent: "center",
  },
  activeDot: {
    backgroundColor: colors.primary,
  },
  number: {
    color: colors.muted,
    fontSize: 12,
    fontWeight: "800",
  },
  activeNumber: {
    color: colors.card,
  },
  label: {
    color: colors.muted,
    fontSize: 11,
    textAlign: "center",
  },
  activeLabel: {
    color: colors.text,
    fontWeight: "700",
  },
});
