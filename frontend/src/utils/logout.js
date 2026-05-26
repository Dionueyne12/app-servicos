import { CommonActions } from "@react-navigation/native";

import { navigationRef } from "../navigation/navigationRef";

export async function logoutAndGoToLogin(signOut) {
  console.log("[AUTH] logout iniciado");

  await signOut();
  console.log("[AUTH] token removido");

  await waitForNavigationSwap();

  if (navigationRef.isReady()) {
    try {
      navigationRef.dispatch(
        CommonActions.reset({
          index: 0,
          routes: [
            {
              name: "Auth",
              state: {
                index: 0,
                routes: [{ name: "Login" }],
              },
            },
          ],
        }),
      );
      console.log("[AUTH] navegação resetada");
    } catch (err) {
      console.log("[AUTH] erro ao resetar navegação", err);
    }
  }

  console.log("[AUTH] logout concluído");
}

function waitForNavigationSwap() {
  return new Promise((resolve) => {
    setTimeout(resolve, 50);
  });
}
