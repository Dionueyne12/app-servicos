import React, { useState } from "react";
import { StyleSheet, Text } from "react-native";

import AppButton from "../components/AppButton";
import ErrorMessage from "../components/ErrorMessage";
import AppInput from "../components/AppInput";
import Header from "../components/Header";
import Screen from "../components/Screen";
import { useAuth } from "../context/AuthContext";
import { colors, spacing } from "../theme";
import { API_BASE_URL } from "../api/client";
import { getApiErrorMessage, logApiError } from "../utils/apiError";

export default function CadastroScreen({ route }) {
  const perfil = route.params?.perfil || "cliente";
  const { signUp } = useAuth();
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [telefone, setTelefone] = useState("");
  const [senha, setSenha] = useState("");
  const [endereco, setEndereco] = useState("");
  const [bairro, setBairro] = useState("");
  const [cidade, setCidade] = useState("");
  const [estado, setEstado] = useState("");
  const [documento, setDocumento] = useState("");
  const [mostrarSenha, setMostrarSenha] = useState(false);
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});
  const [loading, setLoading] = useState(false);

  async function handleCadastro() {
    const payload = {
      nome: nome.trim(),
      email: email.trim().toLowerCase(),
      telefone: somenteNumeros(telefone),
      senha,
      endereco: endereco.trim(),
      bairro: bairro.trim(),
      cidade: cidade.trim(),
      estado: estado.trim().toUpperCase(),
      documento: documento.trim() || null,
    };

    setError("");
    const validationErrors = validarCadastroLocal(payload);
    setFieldErrors(validationErrors);
    if (Object.keys(validationErrors).length > 0) {
      console.log("[VALIDACAO] campo obrigatório faltando", validationErrors);
      setError("Cadastro incompleto. Confira os campos marcados.");
      return;
    }

    setLoading(true);
    try {
      console.log("[Cadastro] enviando para API", {
        baseURL: API_BASE_URL,
        perfil,
        payload: { ...payload, senha: "***" },
      });
      await signUp(perfil, payload);
    } catch (err) {
      logApiError("Cadastro", err, {
        baseURL: API_BASE_URL,
        perfil,
        payload: { ...payload, senha: "***" },
      });
      console.log("[VALIDACAO] erro backend tratado", err?.response?.data);
      setError(getApiErrorMessage(err) || "Nao foi possivel salvar. Verifique os dados e tente novamente.");
    } finally {
      setLoading(false);
    }
  }

  function updateField(field, setter, value) {
    setter(value);
    if (fieldErrors[field]) {
      setFieldErrors((current) => {
        const next = { ...current };
        delete next[field];
        return next;
      });
    }
  }

  return (
    <Screen>
      <Header
        title={perfil === "cliente" ? "Conta de cliente" : "Conta de prestador"}
        subtitle="Preencha os dados principais para usar o app com seguranca."
        showBack
      />
      <AppInput
        label="Nome"
        placeholder="Seu nome"
        value={nome}
        onChangeText={(value) => updateField("nome", setNome, value)}
        error={fieldErrors.nome}
      />
      <AppInput
        label="E-mail"
        placeholder="seuemail@exemplo.com"
        value={email}
        onChangeText={(value) => updateField("email", setEmail, value)}
        keyboardType="email-address"
        autoCapitalize="none"
        error={fieldErrors.email}
      />
      <AppInput
        label="Telefone"
        placeholder="11999999999"
        value={telefone}
        onChangeText={(value) => updateField("telefone", setTelefone, value)}
        keyboardType="phone-pad"
        error={fieldErrors.telefone}
      />
      <AppInput
        label="Senha"
        placeholder="Minimo 8 caracteres com letra e numero"
        value={senha}
        onChangeText={(value) => updateField("senha", setSenha, value)}
        secureTextEntry={!mostrarSenha}
        rightLabel={mostrarSenha ? "Ocultar" : "Ver"}
        onRightPress={() => setMostrarSenha((current) => !current)}
        autoCapitalize="none"
        error={fieldErrors.senha}
      />
      <AppInput
        label="Endereco"
        placeholder="Rua, numero e complemento"
        value={endereco}
        onChangeText={(value) => updateField("endereco", setEndereco, value)}
        error={fieldErrors.endereco}
      />
      <AppInput
        label="Bairro"
        placeholder="Seu bairro"
        value={bairro}
        onChangeText={(value) => updateField("bairro", setBairro, value)}
        error={fieldErrors.bairro}
      />
      <AppInput
        label="Cidade"
        placeholder="Sua cidade"
        value={cidade}
        onChangeText={(value) => updateField("cidade", setCidade, value)}
        error={fieldErrors.cidade}
      />
      <AppInput
        label="Estado"
        placeholder="UF, exemplo SP"
        value={estado}
        onChangeText={(value) => updateField("estado", setEstado, value.toUpperCase().slice(0, 2))}
        autoCapitalize="characters"
        error={fieldErrors.estado}
      />
      {perfil === "prestador" ? (
        <AppInput
          label="Documento"
          placeholder="CPF ou CNPJ para validacao posterior"
          value={documento}
          onChangeText={setDocumento}
          keyboardType="number-pad"
        />
      ) : null}
      <ErrorMessage message={error} />
      <Text style={styles.note}>
        Endereco e obrigatorio para localizar o atendimento. Prestadores ainda passam por aprovacao do admin.
      </Text>
      <AppButton
        title={loading ? "Criando..." : "Criar conta"}
        onPress={handleCadastro}
        disabled={loading || Object.keys(fieldErrors).length > 0}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  note: {
    color: colors.muted,
    fontSize: 14,
    lineHeight: 20,
    marginTop: spacing.sm,
  },
});

function somenteNumeros(value) {
  return value.replace(/\D/g, "");
}

function validarCadastroLocal(payload) {
  const errors = {};
  if (!payload.nome || !payload.email || !payload.telefone || !payload.senha) {
    if (!payload.nome) errors.nome = "Nome obrigatorio.";
    if (!payload.email) errors.email = "E-mail obrigatorio.";
    if (!payload.telefone) errors.telefone = "Telefone obrigatorio.";
    if (!payload.senha) errors.senha = "Senha obrigatoria.";
  }
  if (!payload.endereco) {
    errors.endereco = "Endereco obrigatorio.";
  }
  if (!payload.bairro) {
    errors.bairro = "Bairro obrigatorio.";
  }
  if (!payload.cidade) {
    errors.cidade = "Cidade obrigatoria.";
  }
  if (!payload.estado || payload.estado.length !== 2) {
    errors.estado = "Estado obrigatorio. Use a UF com 2 letras.";
  }
  return errors;
}
