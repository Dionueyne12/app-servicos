import React from "react";
import { StyleSheet, Text, View } from "react-native";

import { colors, spacing } from "../theme";

export default function ErrorMessage({ message }) {
  if (!message) {
    return null;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.text}>{message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.softRed,
    borderRadius: 12,
    padding: spacing.md,
  },
  text: {
    color: colors.danger,
    fontWeight: "700",
  },
});
