import React from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

import { useAuth } from "../context/AuthContext";
import LoadingState from "../components/LoadingState";
import Screen from "../components/Screen";
import AuthNavigator from "./AuthNavigator";
import ClienteNavigator from "./ClienteNavigator";
import PrestadorNavigator from "./PrestadorNavigator";

const Stack = createNativeStackNavigator();

export default function RootNavigator() {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <Screen scroll={false}>
        <LoadingState message="Preparando seu app..." />
      </Screen>
    );
  }

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {!isAuthenticated ? (
        <Stack.Screen name="Auth" component={AuthNavigator} />
      ) : user?.tipo_usuario === "prestador" ? (
        <Stack.Screen name="Prestador" component={PrestadorNavigator} />
      ) : (
        <Stack.Screen name="Cliente" component={ClienteNavigator} />
      )}
    </Stack.Navigator>
  );
}
