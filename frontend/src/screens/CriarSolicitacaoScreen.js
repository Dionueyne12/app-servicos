import React, { useEffect, useState } from "react";
import { Alert, Image, Platform, Pressable, StyleSheet, Text, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import * as ImagePicker from "expo-image-picker";

import { createSolicitacao, uploadFotoSolicitacao } from "../api/requests";
import { listServicosTabelados } from "../api/services";
import AppButton from "../components/AppButton";
import AppCard from "../components/AppCard";
import AppInput from "../components/AppInput";
import ErrorMessage from "../components/ErrorMessage";
import Header from "../components/Header";
import LoadingState from "../components/LoadingState";
import Screen from "../components/Screen";
import StepIndicator from "../components/StepIndicator";
import { useAuth } from "../context/AuthContext";
import { colors, spacing } from "../theme";
import { getApiErrorMessage, logApiError } from "../utils/apiError";

const materialOptions = [
  { id: "cliente_fornece_material", title: "Eu tenho material", text: "Voce ja comprou ou tem a peca." },
  { id: "prestador_providencia_material", title: "Prestador providencia", text: "O prestador informa valor antes." },
  { id: "material_indefinido", title: "Nao sei ainda", text: "O prestador avalia o necessario." },
];

export default function CriarSolicitacaoScreen({ navigation }) {
  const { user } = useAuth();
  const [tipo, setTipo] = useState("personalizado");
  const [servicos, setServicos] = useState([]);
  const [servicoId, setServicoId] = useState(null);
  const [descricao, setDescricao] = useState("");
  const [endereco, setEndereco] = useState("");
  const [material, setMaterial] = useState("material_indefinido");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [photoLoading, setPhotoLoading] = useState(false);
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});
  const [fotos, setFotos] = useState([]);

  useEffect(() => {
    async function loadServicos() {
      setLoading(true);
      try {
        const data = await listServicosTabelados();
        setServicos(data);
        setServicoId(data[0]?.id || null);
      } catch {
        setError("Nao foi possivel carregar os servicos tabelados.");
      } finally {
        setLoading(false);
      }
    }

    loadServicos();
  }, []);

  async function handleCriar() {
    const selectedService = servicos.find((item) => item.id === servicoId) || servicos[0];

    setError("");
    const validationErrors = validarSolicitacaoLocal({
      clienteId: user?.cliente_id,
      selectedService,
      descricao,
      endereco,
      material,
      tipo,
    });
    setFieldErrors(validationErrors);
    if (Object.keys(validationErrors).length > 0) {
      console.log("[VALIDACAO] campo obrigatório faltando", validationErrors);
      setError(validationErrors.geral || "Nao foi possivel salvar. Confira os campos marcados.");
      return;
    }

    setSaving(true);
    try {
      const payload = {
        cliente_id: user.cliente_id,
        tipo_servico: tipo,
        servico_tabelado_id: tipo === "tabelado" ? selectedService.id : null,
        categoria_id: selectedService.categoria_id,
        descricao_problema: descricao.trim(),
        endereco: endereco.trim(),
        urgencia: "normal",
        melhor_horario: null,
        observacoes: null,
        valor_mao_obra: tipo === "tabelado" ? selectedService.preco_mao_obra : 0,
        tempo_estimado: tipo === "tabelado" ? selectedService.tempo_estimado_minutos : 60,
        tipo_material: material,
      };
      const created = await createSolicitacao(payload);
      if (fotos.length > 0) {
        await uploadFotosComSeguranca(created.id);
      }
      navigation.replace("SucessoSolicitacao", { solicitacaoId: created.id });
    } catch (err) {
      logApiError("CriarSolicitacao", err, {
        tipo,
        material,
        totalFotos: fotos.length,
      });
      console.log("[VALIDACAO] erro backend tratado", err?.response?.data);
      setError(getApiErrorMessage(err) || "Nao foi possivel salvar. Verifique os dados e tente novamente.");
    } finally {
      setSaving(false);
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

  async function abrirCamera() {
    setError("");
    setPhotoLoading(true);
    try {
      console.log("[CAMERA] abertura iniciada");
      if (Platform.OS === "web") {
        console.log("[CAMERA] fallback galeria");
        setError("No navegador, escolha uma foto do computador ou celular para testar.");
        await abrirGaleriaInterna();
        return;
      }
      const permission = await ImagePicker.requestCameraPermissionsAsync();
      if (!permission.granted) {
        setError("Permissao da camera negada. Ative a permissao para tirar foto.");
        console.log("[CAMERA] falhou", permission);
        return;
      }
      const result = await withTimeout(
        ImagePicker.launchCameraAsync({
          mediaTypes: ["images"],
          quality: 0.75,
          allowsEditing: false,
        }),
        20000,
        "Tempo esgotado ao abrir camera.",
      );
      if (!result || result.canceled) {
        console.log("[CAMERA] cancelada pelo usuario");
        return;
      }
      console.log("[CAMERA] imagem selecionada", result);
      adicionarFotosDoResultado(result);
    } catch (err) {
      console.log("[CAMERA] falhou", err);
      mostrarFallbackGaleria();
    } finally {
      setPhotoLoading(false);
    }
  }

  async function abrirGaleria() {
    setError("");
    setPhotoLoading(true);
    await abrirGaleriaInterna();
  }

  async function abrirGaleriaInterna() {
    try {
      console.log("[GALERIA] abertura iniciada");
      const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (!permission.granted) {
        setError("Permissao da galeria negada. Ative a permissao para escolher fotos.");
        console.log("[GALERIA] falhou", permission);
        return;
      }
      const result = await withTimeout(
        ImagePicker.launchImageLibraryAsync({
          mediaTypes: ["images"],
          quality: 0.75,
          allowsMultipleSelection: true,
          selectionLimit: 5,
        }),
        20000,
        "Tempo esgotado ao abrir galeria.",
      );
      if (!result || result.canceled) {
        console.log("[GALERIA] cancelada pelo usuario");
        return;
      }
      console.log("[GALERIA] imagem selecionada", result);
      adicionarFotosDoResultado(result);
    } catch (err) {
      console.log("[GALERIA] falhou", err);
      setError("Nao foi possivel abrir a galeria. Tente novamente.");
    } finally {
      setPhotoLoading(false);
    }
  }

  function mostrarFallbackGaleria() {
    setError("Nao foi possivel usar a camera neste aparelho agora. Voce pode escolher uma foto pela galeria.");
    Alert.alert(
      "Camera indisponivel",
      "Nao foi possivel usar a camera neste aparelho agora.\nVoce pode escolher uma foto pela galeria.",
      [
        {
          text: "Cancelar",
          style: "cancel",
        },
        {
          text: "Abrir galeria",
          onPress: () => {
            console.log("[CAMERA] fallback galeria");
            abrirGaleria();
          },
        },
      ],
    );
  }

  function adicionarFotosDoResultado(result) {
    if (!result || result.canceled) {
      return;
    }
    const assets = result.assets || [];
    const validAssets = assets
      .filter((asset) => asset?.uri)
      .map((asset) => ({
        uri: asset.uri,
        fileName: asset.fileName || asset.uri.split("/").pop() || `foto-${Date.now()}.jpg`,
        mimeType: asset.mimeType || inferMimeType(asset.uri),
      }));
    if (validAssets.length === 0) {
      console.log("[Imagem] retorno sem URI valida", result);
      setError("Foto nao carregou, tente novamente.");
      return;
    }
    setFotos((current) => [...current, ...validAssets].slice(0, 5));
  }

  function removerFoto(uri) {
    setFotos((current) => current.filter((foto) => foto.uri !== uri));
  }

  async function uploadFotosComSeguranca(solicitacaoId) {
    for (const foto of fotos) {
      try {
        console.log("[Imagem] enviando foto", {
          solicitacaoId,
          uri: foto.uri,
          mimeType: foto.mimeType,
          fileName: foto.fileName,
        });
        await uploadFotoSolicitacao(solicitacaoId, foto);
      } catch (err) {
        logApiError("UploadFotoSolicitacao", err, { solicitacaoId, foto });
        console.log("[Imagem] upload falhou, solicitacao foi criada mesmo assim");
      }
    }
  }

  return (
    <Screen>
      <Header title="Novo servico" subtitle="Voce pode voltar ou cancelar quando quiser." showBack />
      <StepIndicator steps={["Pedido", "Aguardando", "Execucao", "Finalizacao"]} current={0} />
      <ErrorMessage message={error} />
      <View style={styles.switchRow}>
        <Choice
          selected={tipo === "tabelado"}
          title="Tabelado"
          onPress={() => updateField("servico", setTipo, "tabelado")}
        />
        <Choice
          selected={tipo === "personalizado"}
          title="Personalizado"
          onPress={() => updateField("servico", setTipo, "personalizado")}
        />
      </View>
      {fieldErrors.servico ? <Text style={styles.fieldError}>{fieldErrors.servico}</Text> : null}
      {loading ? <LoadingState message="Carregando servicos..." /> : null}
      {tipo === "tabelado" && servicos.length > 0 ? (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Escolha o servico</Text>
          {servicos.map((servico) => (
            <Pressable key={servico.id} onPress={() => updateField("servico", setServicoId, servico.id)}>
              <AppCard style={[styles.option, servicoId === servico.id && styles.selectedOption]}>
                <Text style={styles.optionTitle}>{servico.nome}</Text>
                <Text style={styles.optionText}>{servico.descricao}</Text>
              </AppCard>
            </Pressable>
          ))}
        </View>
      ) : null}
      <AppInput
        label="Descreva o problema"
        placeholder="Ex: preciso trocar o registro do chuveiro..."
        value={descricao}
        onChangeText={(value) => updateField("descricao", setDescricao, value)}
        multiline
        error={fieldErrors.descricao}
      />
      <AppInput
        label="Endereco"
        placeholder="Rua, numero e complemento"
        value={endereco}
        onChangeText={(value) => updateField("endereco", setEndereco, value)}
        error={fieldErrors.endereco}
      />
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Material</Text>
        {materialOptions.map((option) => (
          <Pressable key={option.id} onPress={() => updateField("material", setMaterial, option.id)}>
            <AppCard style={[styles.option, material === option.id && styles.selectedOption]}>
              <Text style={styles.optionTitle}>{option.title}</Text>
              <Text style={styles.optionText}>{option.text}</Text>
            </AppCard>
          </Pressable>
        ))}
        {fieldErrors.material ? <Text style={styles.fieldError}>{fieldErrors.material}</Text> : null}
      </View>
      <AppCard style={styles.photoCard}>
        <View style={styles.photoIcon}>
          <Ionicons name="camera-outline" size={28} color={colors.primary} />
        </View>
        <Text style={styles.optionTitle}>Fotos do problema</Text>
        <Text style={styles.optionText}>As fotos ajudam o prestador a avaliar melhor o servico.</Text>
        <View style={styles.photoButtons}>
          <AppButton title={photoLoading ? "Carregando foto..." : "Tirar foto"} variant="secondary" onPress={abrirCamera} disabled={photoLoading} />
          <AppButton title={photoLoading ? "Carregando foto..." : "Galeria"} variant="secondary" onPress={abrirGaleria} disabled={photoLoading} />
        </View>
        {fotos.length > 0 ? (
          <View style={styles.previewGrid}>
            {fotos.map((foto) => (
              <View key={foto.uri} style={styles.previewItem}>
                <Image source={{ uri: foto.uri }} style={styles.previewImage} />
                <Pressable onPress={() => removerFoto(foto.uri)} style={styles.removePhoto}>
                  <Text style={styles.removeText}>Remover</Text>
                </Pressable>
              </View>
            ))}
          </View>
        ) : null}
        <Text style={styles.skipText}>Voce tambem pode pular esta etapa por enquanto.</Text>
      </AppCard>
      <AppButton
        title={saving ? "Enviando..." : "Confirmar solicitacao"}
        onPress={handleCriar}
        disabled={saving || Object.keys(fieldErrors).length > 0}
      />
      <AppButton title="Cancelar e voltar ao inicio" variant="secondary" onPress={() => navigation.navigate("ClienteTabs", { screen: "HomeCliente" })} />
    </Screen>
  );
}

function validarSolicitacaoLocal({ clienteId, selectedService, descricao, endereco, material, tipo }) {
  const errors = {};
  if (!clienteId) {
    errors.geral = "Nao encontramos seu perfil de cliente. Entre novamente.";
  }
  if (!tipo || (tipo === "tabelado" && !selectedService?.id) || !selectedService?.categoria_id) {
    errors.servico = "Escolha um servico ou categoria para continuar.";
  }
  if (!descricao.trim()) {
    errors.descricao = "Descricao do problema obrigatoria.";
  } else if (descricao.trim().length < 10) {
    errors.descricao = "Descreva o problema com pelo menos 10 caracteres.";
  }
  if (!endereco.trim()) {
    errors.endereco = "Endereco obrigatorio.";
  }
  if (!material) {
    errors.material = "Escolha o tipo de material.";
  }
  return errors;
}

function inferMimeType(uri) {
  const lower = String(uri || "").toLowerCase();
  if (lower.includes(".png")) return "image/png";
  if (lower.includes(".webp")) return "image/webp";
  return "image/jpeg";
}

function withTimeout(promise, milliseconds, message) {
  return Promise.race([
    promise,
    new Promise((_, reject) => {
      setTimeout(() => reject(new Error(message)), milliseconds);
    }),
  ]);
}

function Choice({ title, selected, onPress }) {
  return (
    <Pressable onPress={onPress} style={[styles.choice, selected && styles.choiceSelected]}>
      <Text style={[styles.choiceText, selected && styles.choiceTextSelected]}>{title}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  switchRow: {
    flexDirection: "row",
    gap: spacing.md,
  },
  choice: {
    flex: 1,
    minHeight: 48,
    borderRadius: 12,
    backgroundColor: colors.card,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: colors.border,
  },
  choiceSelected: {
    backgroundColor: colors.softBlue,
    borderColor: colors.primary,
  },
  choiceText: {
    color: colors.muted,
    fontWeight: "800",
  },
  choiceTextSelected: {
    color: colors.primary,
  },
  section: {
    gap: spacing.md,
  },
  sectionTitle: {
    color: colors.text,
    fontSize: 18,
    fontWeight: "900",
  },
  option: {
    gap: spacing.xs,
    borderWidth: 1,
    borderColor: colors.card,
  },
  selectedOption: {
    borderColor: colors.primary,
    backgroundColor: colors.softBlue,
  },
  optionTitle: {
    color: colors.text,
    fontSize: 16,
    fontWeight: "900",
  },
  optionText: {
    color: colors.muted,
    fontSize: 14,
    lineHeight: 20,
  },
  photoCard: {
    borderStyle: "dashed",
    borderWidth: 1,
    borderColor: colors.border,
    gap: spacing.xs,
  },
  photoIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.softBlue,
    alignItems: "center",
    justifyContent: "center",
  },
  photoButtons: {
    gap: spacing.sm,
    marginTop: spacing.sm,
  },
  skipText: {
    color: colors.muted,
    fontSize: 13,
    lineHeight: 18,
  },
  previewGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.md,
    marginTop: spacing.md,
  },
  previewItem: {
    width: "47%",
    gap: spacing.sm,
  },
  previewImage: {
    width: "100%",
    aspectRatio: 1,
    borderRadius: 12,
    backgroundColor: colors.border,
  },
  removePhoto: {
    minHeight: 36,
    borderRadius: 10,
    backgroundColor: colors.softRed,
    alignItems: "center",
    justifyContent: "center",
  },
  removeText: {
    color: colors.danger,
    fontWeight: "900",
  },
  fieldError: {
    color: colors.danger,
    fontSize: 13,
    fontWeight: "700",
    lineHeight: 18,
  },
});
