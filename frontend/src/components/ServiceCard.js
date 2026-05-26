import React from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { colors, spacing } from "../theme";
import AppCard from "./AppCard";
import StatusBadge from "./StatusBadge";

export default function ServiceCard({ title, description, status, price, nextStep, onPress }) {
  return (
    <Pressable onPress={onPress}>
      {({ pressed }) => (
        <AppCard style={[styles.card, pressed && styles.pressed]}>
          <View style={styles.top}>
            <Text style={styles.title}>{title}</Text>
            {price ? <Text style={styles.price}>{price}</Text> : null}
          </View>
          <Text style={styles.description}>{description}</Text>
          {status ? <StatusBadge status={status} /> : null}
          {nextStep ? <Text style={styles.nextStep}>{nextStep}</Text> : null}
        </AppCard>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    gap: spacing.md,
  },
  pressed: {
    opacity: 0.88,
  },
  top: {
    flexDirection: "row",
    alignItems: "flex-start",
    justifyContent: "space-between",
    gap: spacing.md,
  },
  title: {
    flex: 1,
    color: colors.text,
    fontSize: 17,
    fontWeight: "900",
  },
  price: {
    color: colors.primary,
    fontSize: 15,
    fontWeight: "900",
  },
  description: {
    color: colors.muted,
    fontSize: 14,
    lineHeight: 20,
  },
  nextStep: {
    color: colors.text,
    fontSize: 14,
    fontWeight: "800",
    lineHeight: 20,
  },
});
