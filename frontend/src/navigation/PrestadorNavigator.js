import React from "react";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import DetalheSolicitacaoScreen from "../screens/DetalheSolicitacaoScreen";
import HomePrestadorScreen from "../screens/HomePrestadorScreen";
import MinhasSolicitacoesScreen from "../screens/MinhasSolicitacoesScreen";
import NotificacoesScreen from "../screens/NotificacoesScreen";
import PerfilScreen from "../screens/PerfilScreen";
import ServicosDisponiveisScreen from "../screens/ServicosDisponiveisScreen";
import { colors } from "../theme";

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

function PrestadorTabs() {
  const insets = useSafeAreaInsets();

  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.muted,
        tabBarStyle: {
          minHeight: 64 + insets.bottom,
          paddingBottom: Math.max(insets.bottom, 12),
          paddingTop: 8,
          borderTopColor: colors.border,
          backgroundColor: colors.card,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: "700",
        },
      }}
    >
      <Tab.Screen name="HomePrestador" component={HomePrestadorScreen} options={{ title: "Inicio", tabBarIcon: ({ color, size }) => <Ionicons name="home-outline" color={color} size={size} /> }} />
      <Tab.Screen name="ServicosDisponiveis" component={ServicosDisponiveisScreen} options={{ title: "Pedidos", tabBarIcon: ({ color, size }) => <Ionicons name="briefcase-outline" color={color} size={size} /> }} />
      <Tab.Screen name="MeusServicos" component={MinhasSolicitacoesScreen} options={{ title: "Meus", tabBarIcon: ({ color, size }) => <Ionicons name="checkmark-done-outline" color={color} size={size} /> }} />
      <Tab.Screen name="Perfil" component={PerfilScreen} options={{ title: "Perfil", tabBarIcon: ({ color, size }) => <Ionicons name="person-circle-outline" color={color} size={size} /> }} />
    </Tab.Navigator>
  );
}

export default function PrestadorNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="PrestadorTabs" component={PrestadorTabs} />
      <Stack.Screen name="DetalheSolicitacao" component={DetalheSolicitacaoScreen} />
      <Stack.Screen name="Notificacoes" component={NotificacoesScreen} />
    </Stack.Navigator>
  );
}
