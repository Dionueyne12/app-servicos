import React from "react";
import { StyleSheet, Text, View } from "react-native";

import { colors, spacing } from "../theme";
import { getStatusLabel } from "../utils/status";

const statusColors = {
  aguardando_prestador: [colors.warning, colors.softOrange],
  aceito: [colors.primary, colors.softBlue],
  aguardando_aprovacao_cliente: [colors.warning, colors.softOrange],
  material_aprovado: [colors.success, colors.softGreen],
  em_andamento: [colors.primary, colors.softBlue],
  aguardando_confirmacao_cliente: [colors.warning, colors.softOrange],
  concluido: [colors.success, colors.softGreen],
  cancelado: [colors.danger, colors.softRed],
  em_analise: [colors.danger, colors.softRed],
};

export default function StatusBadge({ status }) {
  const [textColor, backgroundColor] = statusColors[status] || [colors.muted, colors.border];

  return (
    <View style={[styles.badge, { backgroundColor }]}>
      <Text style={[styles.text, { color: textColor }]}>{getStatusLabel(status)}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    alignSelf: "flex-start",
    borderRadius: 999,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
  },
  text: {
    fontSize: 12,
    fontWeight: "800",
  },
});
