import subprocess
import sys

# 🔧 Instala o reportlab automaticamente se faltar
try:
    from reportlab.lib.pagesizes import A4
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
    from reportlab.lib.pagesizes import A4

import streamlit as st
import pandas as pd
import json
from utils_v4 import (
    carregar_base_dados,
    guardar_base_dados,
    gerar_recibo_pdf,
    importar_dados_excel,
    importar_dados_texto,
    exportar_para_excel,
    remover_registro,
    atualizar_registro,
)

# ========================
# CONFIGURAÇÕES GERAIS
# ========================
st.set_page_config(
    page_title="Gestão de Militantes MPLA v4",
    page_icon="🇦🇴",
    layout="wide"
)

st.title("🟥🟨⬛ Gestão de Militantes MPLA v4")
st.markdown("### Servir o Povo e Fazer Angola Crescer")

# ========================
# CARREGAR LOCALIDADES
# ========================
try:
    with open("localidades_luanda_v3.json", "r", encoding="utf-8") as f:
        localidades = json.load(f)
except Exception:
    localidades = {}

# ========================
# CARREGAR BASE DE DADOS
# ========================
df = carregar_base_dados()

# ========================
# MENU PRINCIPAL
# ========================
menu = st.sidebar.radio("📋 Menu", ["➕ Novo Militante", "📂 Base de Dados", "📥 Importar Dados", "📤 Exportar Dados", "📑 Recibos"])

# ========================
# 1️⃣ NOVO MILITANTE
# ========================
if menu == "➕ Novo Militante":
    st.header("➕ Formulário de Registo de Militante")
    with st.form("novo_militante"):
        col1, col2, col3 = st.columns(3)
        with col1:
            primeiro_nome = st.text_input("Nome(s) Próprio(s)")
        with col2:
            ultimo_nome = st.text_input("Último Nome")
        with col3:
            numero_cap = st.text_input("Nº CAP (ex: CAP001)").upper()

        telefone = st.text_input("Telefone (9 dígitos)").strip()
        cartao = st.text_input("Nº do Cartão de Militante").strip()

        provincia = st.selectbox("Província", ["Luanda"])
        municipio = st.selectbox("Município", list(localidades.keys()))
        comunas = localidades.get(municipio, [])
        if comunas:
            comuna = st.selectbox("Comuna", comunas)
        else:
            st.info("📍 Este município não possui comunas. Introduza o bairro manualmente.")
            comuna = st.text_input("Comuna (manual)").strip()
        bairro = st.text_input("Bairro (manual)").strip()

        submit = st.form_submit_button("💾 Guardar Registo")

        if submit:
            novo_registro = {
                "Primeiro Nome": primeiro_nome,
                "Último Nome": ultimo_nome,
                "Nº CAP": numero_cap,
                "Telefone": telefone,
                "Cartão": cartao,
                "Província": provincia,
                "Município": municipio,
                "Comuna": comuna,
                "Bairro": bairro
            }
            if primeiro_nome and ultimo_nome and numero_cap:
                df = guardar_base_dados(df, novo_registro)
                st.success(f"✅ Militante {primeiro_nome} {ultimo_nome} registado com sucesso!")
            else:
                st.error("⚠️ Preencha todos os campos obrigatórios.")

# ========================
# 2️⃣ BASE DE DADOS
# ========================
elif menu == "📂 Base de Dados":
    st.header("📂 Base de Dados de Militantes")
    st.dataframe(df, use_container_width=True)

    st.subheader("✏️ Editar / Eliminar Registos")
    col1, col2 = st.columns(2)
    with col1:
        id_registro = st.number_input("ID do Registo", min_value=0, step=1)
    with col2:
        acao = st.radio("Ação", ["Editar", "Eliminar"])

    if acao == "Editar":
        st.info("⚙️ Introduza os novos dados abaixo:")
        novo_nome = st.text_input("Novo Nome Próprio")
        novo_apelido = st.text_input("Novo Último Nome")
        if st.button("💾 Atualizar"):
            df = atualizar_registro(df, id_registro, novo_nome, novo_apelido)
            st.success("✅ Registo atualizado com sucesso!")
    else:
        if st.button("🗑️ Eliminar"):
            df = remover_registro(df, id_registro)
            st.warning("❌ Registo eliminado com sucesso!")

# ========================
# 3️⃣ IMPORTAR DADOS
# ========================
elif menu == "📥 Importar Dados":
    st.header("📥 Importar Dados")

    tab1, tab2 = st.tabs(["📂 Ficheiro Excel", "📋 Colar Dados"])
    with tab1:
        file = st.file_uploader("Carregar ficheiro (.xlsx / .csv)", type=["xlsx", "csv"])
        if file:
            df = importar_dados_excel(df, file)
            st.success("✅ Dados importados com sucesso!")

    with tab2:
        texto = st.text_area("Colar dados (usar separador TAB ou |)")
        if st.button("📥 Processar Colagem"):
            df = importar_dados_texto(df, texto)
            st.success("✅ Colagem processada com sucesso!")

# ========================
# 4️⃣ EXPORTAR DADOS
# ========================
elif menu == "📤 Exportar Dados":
    st.header("📤 Exportar Dados")
    if st.button("💾 Exportar para Excel"):
        exportar_para_excel(df)
        st.success("✅ Ficheiro Excel gerado com sucesso!")

# ========================
# 5️⃣ RECIBOS
# ========================
elif menu == "📑 Recibos":
    st.header("📑 Emitir Recibo Oficial do Militante")
    if len(df) == 0:
        st.warning("⚠️ Ainda não existem registos.")
    else:
        nomes = df["Primeiro Nome"] + " " + df["Último Nome"]
        nome_selecionado = st.selectbox("Selecionar Militante", nomes)
        if st.button("🧾 Gerar Recibo"):
            militante = df.iloc[nomes[nomes == nome_selecionado].index[0]]
            gerar_recibo_pdf(militante)
            st.success("✅ Recibo gerado com sucesso! Verifique a pasta de saída.")
