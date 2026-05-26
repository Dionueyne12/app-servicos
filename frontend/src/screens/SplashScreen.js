import React, { useEffect } from "react";
import { StyleSheet, Text, View } from "react-native";

import AppButton from "../components/AppButton";
import Screen from "../components/Screen";
import { colors, spacing } from "../theme";

export default function SplashScreen({ navigation }) {
  useEffect(() => {
    const timer = setTimeout(() => navigation.replace("Login"), 900);
    return () => clearTimeout(timer);
  }, [navigation]);

  return (
    <Screen scroll={false}>
      <View style={styles.container}>
        <View style={styles.logo}>
          <Text style={styles.logoText}>S</Text>
        </View>
        <View style={styles.texts}>
          <Text style={styles.title}>App Servicos</Text>
          <Text style={styles.subtitle}>Servicos de casa sem complicacao.</Text>
        </View>
        <AppButton title="Entrar" onPress={() => navigation.replace("Login")} />
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    gap: spacing.xl,
  },
  logo: {
    width: 76,
    height: 76,
    borderRadius: 24,
    backgroundColor: colors.primary,
    alignItems: "center",
    justifyContent: "center",
  },
  logoText: {
    color: colors.card,
    fontSize: 36,
    fontWeight: "900",
  },
  texts: {
    gap: spacing.sm,
  },
  title: {
    color: colors.text,
    fontSize: 34,
    fontWeight: "900",
  },
  subtitle: {
    color: colors.muted,
    fontSize: 17,
  },
});
