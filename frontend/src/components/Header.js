import React from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { useNavigation } from "@react-navigation/native";

import { colors, spacing } from "../theme";

export default function Header({ title, subtitle, right, showBack = false }) {
  const navigation = useNavigation();
  const canGoBack = navigation.canGoBack();

  return (
    <View style={styles.container}>
      {showBack && canGoBack ? (
        <Pressable onPress={() => navigation.goBack()} style={styles.backButton}>
          <Text style={styles.backText}>Voltar</Text>
        </Pressable>
      ) : null}
      <View style={styles.texts}>
        <Text style={styles.title}>{title}</Text>
        {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
      </View>
      {right ? <View>{right}</View> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: spacing.lg,
  },
  backButton: {
    minHeight: 40,
    borderRadius: 12,
    backgroundColor: colors.card,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: spacing.md,
  },
  backText: {
    color: colors.primary,
    fontSize: 14,
    fontWeight: "900",
  },
  texts: {
    flex: 1,
    gap: spacing.xs,
  },
  title: {
    color: colors.text,
    fontSize: 26,
    fontWeight: "900",
  },
  subtitle: {
    color: colors.muted,
    fontSize: 15,
    lineHeight: 21,
  },
});
