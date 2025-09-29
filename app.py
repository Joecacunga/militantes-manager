import streamlit as st
import pandas as pd
from utils import detectar_duplicados, exportar_excel

# -------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -------------------------------
st.set_page_config(page_title="Gestão de Militantes", layout="wide")

st.title("📋 Sistema de Registo de Militantes")

# -------------------------------
# SIDEBAR: CONFIGURAÇÃO DAS LISTAS
# -------------------------------
st.sidebar.header("⚙️ Configuração de Localizações")
st.sidebar.write("Aqui podes editar as listas de Províncias, Municípios e Comunas.")

# Carregar listas padrão (ou anteriores)
if "provincias" not in st.session_state:
    st.session_state.provincias = ["Luanda", "Benguela", "Huambo", "Huíla", "Cuanza Sul", "Outra..."]
if "municipios" not in st.session_state:
    st.session_state.municipios = ["Cazenga", "Viana", "Belas", "Lubango", "Lobito", "Outro..."]
if "comunas" not in st.session_state:
    st.session_state.comunas = ["Comuna 1", "Comuna 2", "Comuna 3", "Outra..."]

# Formulário de edição na sidebar
with st.sidebar.expander("✏️ Editar Listas"):
    st.session_state.provincias = st.text_area(
        "Províncias (uma por linha)", "\n".join(st.session_state.provincias)
    ).split("\n")

    st.session_state.municipios = st.text_area(
        "Municípios (uma por linha)", "\n".join(st.session_state.municipios)
    ).split("\n")

    st.session_state.comunas = st.text_area(
        "Comunas (uma por linha)", "\n".join(st.session_state.comunas)
    ).split("\n")

st.sidebar.success("✅ Listas carregadas e prontas para uso!")

# -------------------------------
# SELEÇÃO DE LOCALIZAÇÃO PRINCIPAL
# -------------------------------
st.header("🌍 Selecionar Localização")
col1, col2, col3 = st.columns(3)

with col1:
    provincia = st.selectbox("Província", st.session_state.provincias)

with col2:
    municipio = st.selectbox("Município", st.session_state.municipios)

with col3:
    comuna = st.selectbox("Comuna", st.session_state.comunas)

st.info(f"📍 Localização ativa: {provincia} > {municipio} > {comuna}")

# -------------------------------
# UPLOAD DE FICHEIRO EXCEL
# -------------------------------
st.header("📂 Importar ficheiro Excel")
uploaded_file = st.file_uploader("Selecione o ficheiro Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    # Ler dados
    try:
        df = pd.read_excel(uploaded_file)
        st.success("✅ Ficheiro carregado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao ler o ficheiro: {e}")
        st.stop()

    # Adicionar localização
    df["Província"] = provincia
    df["Município"] = municipio
    df["Comuna"] = comuna

    # Criar abas para navegação
    tab1, tab2, tab3 = st.tabs(["👀 Pré-visualizar", "🔍 Verificar Duplicados", "📤 Exportar"])

    # Aba 1: Pré-visualização
    with tab1:
        st.subheader("👀 Pré-visualização dos dados")
        st.dataframe(df.head(50))
        st.info(f"O ficheiro contém {len(df)} registos.")

    # Aba 2: Duplicados
    with tab2:
        st.subheader("🔍 Verificação de Duplicados")
        duplicados = detectar_duplicados(df)
        if not duplicados.empty:
            st.warning(f"⚠️ Foram encontrados {len(duplicados)} registos duplicados!")
            st.dataframe(duplicados)
        else:
            st.success("✅ Nenhum duplicado encontrado.")

    # Aba 3: Exportação
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
