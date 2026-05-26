import React from "react";
import { Pressable, StyleSheet, Text } from "react-native";

import { colors, spacing } from "../theme";

export default function AppButton({ title, onPress, variant = "primary", disabled = false }) {
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled}
      style={({ pressed }) => [
        styles.button,
        styles[variant],
        disabled && styles.disabled,
        pressed && !disabled && styles.pressed,
      ]}
    >
      <Text style={[styles.text, variant === "secondary" && styles.secondaryText]}>{title}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    minHeight: 54,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: spacing.lg,
  },
  primary: {
    backgroundColor: colors.primary,
  },
  secondary: {
    backgroundColor: colors.softBlue,
  },
  success: {
    backgroundColor: colors.success,
  },
  danger: {
    backgroundColor: colors.danger,
  },
  disabled: {
    opacity: 0.5,
  },
  pressed: {
    opacity: 0.86,
  },
  text: {
    color: colors.card,
    fontSize: 16,
    fontWeight: "700",
  },
  secondaryText: {
    color: colors.primary,
  },
});
