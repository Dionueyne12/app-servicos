import React from "react";
import { Pressable, StyleSheet, Text, TextInput, View } from "react-native";

import { colors, spacing } from "../theme";

export default function AppInput({
  label,
  placeholder,
  value,
  onChangeText,
  multiline = false,
  secureTextEntry = false,
  rightLabel,
  onRightPress,
  keyboardType = "default",
  autoCapitalize = "sentences",
  error,
}) {
  return (
    <View style={styles.wrapper}>
      {label ? <Text style={[styles.label, error && styles.labelError]}>{label}</Text> : null}
      <View style={styles.inputWrap}>
        <TextInput
          value={value}
          onChangeText={onChangeText}
          placeholder={placeholder}
          placeholderTextColor={colors.muted}
          multiline={multiline}
          secureTextEntry={secureTextEntry}
          keyboardType={keyboardType}
          autoCapitalize={autoCapitalize}
          style={[
            styles.input,
            multiline && styles.multiline,
            rightLabel && styles.inputWithRight,
            error && styles.inputError,
          ]}
        />
        {rightLabel ? (
          <Pressable onPress={onRightPress} style={styles.rightButton}>
            <Text style={styles.rightText}>{rightLabel}</Text>
          </Pressable>
        ) : null}
      </View>
      {error ? <Text style={styles.errorText}>{error}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    gap: spacing.sm,
  },
  label: {
    color: colors.text,
    fontSize: 14,
    fontWeight: "700",
  },
  labelError: {
    color: colors.danger,
  },
  input: {
    minHeight: 52,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.card,
    color: colors.text,
    paddingHorizontal: spacing.lg,
    fontSize: 16,
  },
  inputWrap: {
    position: "relative",
  },
  inputError: {
    borderColor: colors.danger,
    backgroundColor: colors.softRed,
  },
  inputWithRight: {
    paddingRight: 88,
  },
  rightButton: {
    position: "absolute",
    right: spacing.sm,
    top: 6,
    minHeight: 40,
    paddingHorizontal: spacing.md,
    borderRadius: 10,
    alignItems: "center",
    justifyContent: "center",
  },
  rightText: {
    color: colors.primary,
    fontSize: 13,
    fontWeight: "900",
  },
  errorText: {
    color: colors.danger,
    fontSize: 13,
    fontWeight: "700",
    lineHeight: 18,
  },
  multiline: {
    minHeight: 116,
    paddingTop: spacing.lg,
    textAlignVertical: "top",
  },
});
