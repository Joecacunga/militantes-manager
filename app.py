import streamlit as st
import pandas as pd
from utils import detectar_duplicados, exportar_excel

# Configuração da página
st.set_page_config(page_title="Gestão de Militantes", layout="wide")

# Título principal
st.title("📋 Sistema de Registo de Militantes")

# --- Seleção de localização ---
st.header("🌍 Selecionar Localização")
col1, col2, col3 = st.columns(3)

with col1:
    provincia = st.selectbox(
        "Província",
        ["Luanda", "Benguela", "Huambo", "Huíla", "Cuanza Sul", "Outra..."]
    )

with col2:
    municipio = st.selectbox(
        "Município",
        ["Cazenga", "Viana", "Belas", "Lubango", "Lobito", "Outro..."]
    )

with col3:
    comuna = st.selectbox(
        "Comuna",
        ["Comuna 1", "Comuna 2", "Comuna 3", "Outra..."]
    )

st.info(f"📍 Localização ativa: {provincia} > {municipio} > {comuna}")

# --- Secção Upload ---
st.header("📂 Importar ficheiro Excel")
uploaded_file = st.file_uploader("Selecione o ficheiro Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    # Ler dados do Excel
    try:
        df = pd.read_excel(uploaded_file)
        st.success("✅ Ficheiro carregado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao ler o ficheiro: {e}")
        st.stop()

    # Adicionar colunas de localização ao dataset
    df["Província"] = provincia
    df["Município"] = municipio
    df["Comuna"] = comuna

    # Criar abas para organizar a interface
    tab1, tab2, tab3 = st.tabs(["👀 Pré-visualizar", "🔍 Verificação de Duplicados", "📤 Exportação"])

    # --- Aba 1: Pré-visualizar ---
    with tab1:
        st.subheader("👀 Pré-visualização dos dados carregados")
        st.dataframe(df.head(50))  # mostra os 50 primeiros registos
        st.info(f"O ficheiro contém {len(df)} registos.")

    # --- Aba 2: Verificação de Duplicados ---
    with tab2:
        st.subheader("🔍 Duplicados encontrados")
        duplicados = detectar_duplicados(df)

        if not duplicados.empty:
            st.warning(f"⚠️ Foram encontrados {len(duplicados)} registos duplicados!")
            st.dataframe(duplicados)
        else:
            st.success("✅ Nenhum duplicado encontrado.")

    # --- Aba 3: Exportação ---
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
