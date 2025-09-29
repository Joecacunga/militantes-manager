import streamlit as st
import pandas as pd
from utils import (
    detectar_duplicados,
    exportar_excel,
    carregar_listas,
    guardar_listas,
    gerar_listas_padrao,
)

# -------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -------------------------------
st.set_page_config(page_title="Gestão de Militantes", layout="wide")
st.title("📋 Sistema de Registo de Militantes")

# -------------------------------
# CARREGAR LISTAS DO JSON
# -------------------------------
listas = carregar_listas()

# -------------------------------
# SIDEBAR: CONFIGURAÇÃO DE LOCALIZAÇÕES
# -------------------------------
st.sidebar.header("⚙️ Configuração de Localizações")
st.sidebar.write("Aqui podes editar as listas de Províncias, Municípios e Comunas.")

# Área de edição das listas
with st.sidebar.expander("✏️ Editar Listas"):
    provincias_editadas = st.text_area(
        "Províncias (uma por linha)", "\n".join(listas["provincias"])
    ).split("\n")

    municipios_editados = st.text_area(
        "Municípios (uma por linha)", "\n".join(listas["municipios"])
    ).split("\n")

    comunas_editadas = st.text_area(
        "Comunas (uma por linha)", "\n".join(listas["comunas"])
    ).split("\n")

# Botões de ação na barra lateral
col_save, col_reset = st.sidebar.columns(2)
with col_save:
    if st.button("💾 Guardar listas"):
        listas_atualizadas = {
            "provincias": [p.strip() for p in provincias_editadas if p.strip()],
            "municipios": [m.strip() for m in municipios_editados if m.strip()],
            "comunas": [c.strip() for c in comunas_editadas if c.strip()],
        }
        sucesso = guardar_listas(listas_atualizadas)
        if sucesso:
            st.sidebar.success("✅ Listas guardadas com sucesso! Atualize a página para aplicar.")
        else:
            st.sidebar.error("❌ Erro ao guardar as listas.")

with col_reset:
    if st.button("♻️ Restaurar padrão"):
        guardar_listas(gerar_listas_padrao())
        st.sidebar.warning("⚠️ Listas restauradas para o padrão. Atualize a página para ver.")

st.sidebar.info("💡 As listas são gravadas num ficheiro JSON local e mantêm-se mesmo após fechar a aplicação.")

# -------------------------------
# SELEÇÃO DE LOCALIZAÇÃO PRINCIPAL
# -------------------------------
st.header("🌍 Selecionar Localização")
col1, col2, col3 = st.columns(3)

with col1:
    provincia = st.selectbox("Província", listas["provincias"])

with col2:
    municipio = st.selectbox("Município", listas["municipios"])

with col3:
    comuna = st.selectbox("Comuna", listas["comunas"])

st.info(f"📍 Localização ativa: {provincia} > {municipio} > {comuna}")

# -------------------------------
# UPLOAD DE FICHEIRO EXCEL
# -------------------------------
st.header("📂 Importar ficheiro Excel")
uploaded_file = st.file_uploader("Selecione o ficheiro Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("✅ Ficheiro carregado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao ler o ficheiro: {e}")
        st.stop()

    # Adicionar colunas de localização
    df["Província"] = provincia
    df["Município"] = municipio
    df["Comuna"] = comuna

    # Abas de navegação
    tab1, tab2, tab3 = st.tabs(["👀 Pré-visualizar", "🔍 Verificar Duplicados", "📤 Exportar"])

    # Aba 1 — Pré-visualização
    with tab1:
        st.subheader("👀 Pré-visualização dos dados")
        st.dataframe(df.head(50))
        st.info(f"O ficheiro contém {len(df)} registos.")

    # Aba 2 — Duplicados
    with tab2:
        st.subheader("🔍 Verificação de Duplicados")
        duplicados = detectar_duplicados(df)
        if not duplicados.empty:
            st.warning(f"⚠️ Foram encontrados {len(duplicados)} registos duplicados!")
            st.dataframe(duplicados)
        else:
            st.success("✅ Nenhum duplicado encontrado.")

    # Aba 3 — Exportação
    with tab3:
        st.subheader("📤 Exportar ficheiro tratado")
        if st.button("💾 Gerar ficheiro Excel Limpo"):
            output = exportar_excel(df)
            st.download_button(
                label="⬇️ Baixar ficheiro tratado",
                data=output,
                file_name="militantes_processados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
