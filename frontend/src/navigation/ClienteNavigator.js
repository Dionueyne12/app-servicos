import React from "react";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import CriarSolicitacaoScreen from "../screens/CriarSolicitacaoScreen";
import DetalheSolicitacaoScreen from "../screens/DetalheSolicitacaoScreen";
import HomeClienteScreen from "../screens/HomeClienteScreen";
import MinhasSolicitacoesScreen from "../screens/MinhasSolicitacoesScreen";
import NotificacoesScreen from "../screens/NotificacoesScreen";
import PerfilScreen from "../screens/PerfilScreen";
import SucessoSolicitacaoScreen from "../screens/SucessoSolicitacaoScreen";
import { colors } from "../theme";

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

function ClienteTabs() {
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
      <Tab.Screen name="HomeCliente" component={HomeClienteScreen} options={{ title: "Inicio", tabBarIcon: ({ color, size }) => <Ionicons name="home-outline" color={color} size={size} /> }} />
      <Tab.Screen name="MinhasSolicitacoes" component={MinhasSolicitacoesScreen} options={{ title: "Pedidos", tabBarIcon: ({ color, size }) => <Ionicons name="clipboard-outline" color={color} size={size} /> }} />
      <Tab.Screen name="Notificacoes" component={NotificacoesScreen} options={{ title: "Avisos", tabBarIcon: ({ color, size }) => <Ionicons name="notifications-outline" color={color} size={size} /> }} />
      <Tab.Screen name="Perfil" component={PerfilScreen} options={{ title: "Perfil", tabBarIcon: ({ color, size }) => <Ionicons name="person-circle-outline" color={color} size={size} /> }} />
    </Tab.Navigator>
  );
}

export default function ClienteNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="ClienteTabs" component={ClienteTabs} />
      <Stack.Screen name="CriarSolicitacao" component={CriarSolicitacaoScreen} />
      <Stack.Screen name="SucessoSolicitacao" component={SucessoSolicitacaoScreen} />
      <Stack.Screen name="DetalheSolicitacao" component={DetalheSolicitacaoScreen} />
    </Stack.Navigator>
  );
}
