# =====================================================
# MPLA Gestão de Militantes - APP Oficial (v4.4)
# =====================================================
# Desenvolvido por: Joe Cacunga & GPT-5
# Lema: MPLA — Servir o Povo e Fazer Angola Crescer
# =====================================================

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from utils_v4 import (
    carregar_base_dados,
    adicionar_militante,
    remover_registro,
    atualizar_registro,
    importar_dados_excel,
    importar_dados_texto,
    exportar_para_excel,
    gerar_recibo_militante_pdf,
    carregar_localidades,
    obter_comunas_por_municipio,
)

# =====================================================
# Configuração da Página
# =====================================================
st.set_page_config(page_title="MPLA Gestão de Militantes", layout="wide")

# =====================================================
# Estilo Geral (CSS)
# =====================================================
st.markdown("""
    <style>
    body {
        background-color: white;
        font-family: Arial, sans-serif;
    }
    .title-bar {
        background-color: black;
        color: white;
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        padding: 10px 0px;
        margin-bottom: 5px;
    }
    .subtitle {
        text-align: center;
        color: red;
        font-size: 16px;
        margin-bottom: 20px;
        font-weight: bold;
    }
    .section-header {
        color: #b30000;
        font-size: 20px;
        font-weight: bold;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================
# Cabeçalho Institucional
# =====================================================
if os.path.exists("Flag_of_MPLA.svg.png"):
    st.image("Flag_of_MPLA.svg.png", width=350)

st.markdown('<div class="title-bar">🟥 MPLA Gestão de Militantes</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">MPLA — Servir o Povo e Fazer Angola Crescer</div>', unsafe_allow_html=True)

# =====================================================
# Carregar Base de Dados e Localidades
# =====================================================
base = carregar_base_dados()
localidades = carregar_localidades()

# =====================================================
# Menu Lateral
# =====================================================
menu = st.sidebar.radio("📋 Menu Principal", [
    "Formulário Individual",
    "Base de Dados",
    "Importar/Colar",
    "Exportar",
    "Recibos"
])

# =====================================================
# Funções auxiliares
# =====================================================
def datetime_now_str():
    return datetime.now().strftime("%Y%m%d%H%M%S")


# =====================================================
# FORMULÁRIO INDIVIDUAL DO MILITANTE
# =====================================================
if menu == "Formulário Individual":
    st.markdown('<div class="section-header">🧾 Formulário Individual do Militante</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        nome_proprio = st.text_input("Nome(s) Próprio(s)")
        ultimo_nome = st.text_input("Último Nome")
        cap_field = st.text_input("Nº CAP (ex: CAP041)")
        telefone = st.text_input("Telefone")
    with col2:
        numero_cartao = st.text_input("Nº de Cartão")
        provincia = "Luanda"  # fixa
        municipio = st.selectbox("Município", list(localidades.keys()))
        comunas = obter_comunas_por_municipio(localidades, municipio)
        if comunas:
            comuna = st.selectbox("Comuna", comunas)
        else:
            comuna = ""
        bairro = st.text_input("Bairro")
    with col3:
        tirar_foto = st.camera_input("📸 Capturar Fotografia (opcional)")
        foto_path = None
        if tirar_foto:
            nome_foto = f"{cap_field.strip().upper()}_{datetime_now_str()}.jpg"
            foto_path = os.path.join("fotos", nome_foto)
            os.makedirs("fotos", exist_ok=True)
            with open(foto_path, "wb") as f:
                f.write(tirar_foto.getbuffer())

    if st.button("💾 Guardar Registo"):
        if nome_proprio and ultimo_nome and cap_field:
            militante = {
                "nome_proprio": nome_proprio,
                "ultimo_nome": ultimo_nome,
                "cap": cap_field.strip().upper(),
                "telefone": telefone,
                "cartao": numero_cartao,
                "provincia": provincia,
                "municipio": municipio,
                "comuna": comuna,
                "bairro": bairro,
                "foto": foto_path,
                "data_registo": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
            base = adicionar_militante(base, militante)
            st.success(f"✅ Militante {nome_proprio} {ultimo_nome} registado com sucesso!")
        else:
            st.warning("⚠️ Preencha pelo menos o Nome, Último Nome e Nº de CAP.")

# =====================================================
# BASE DE DADOS
# =====================================================
elif menu == "Base de Dados":
    st.markdown('<div class="section-header">📂 Base de Dados de Militantes</div>', unsafe_allow_html=True)

    if len(base) == 0:
        st.info("A base de dados está vazia.")
    else:
        df = pd.DataFrame(base)
        st.dataframe(df, use_container_width=True)

# =====================================================
# IMPORTAR/COLAR
# =====================================================
elif menu == "Importar/Colar":
    st.markdown('<div class="section-header">📥 Importar Dados</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Carregar ficheiro (.xlsx ou .csv)", type=["xlsx", "csv"])
    if uploaded_file:
        base = importar_dados_excel(base, uploaded_file)
        st.success("✅ Dados importados com sucesso!")

# =====================================================
# EXPORTAR
# =====================================================
elif menu == "Exportar":
    st.markdown('<div class="section-header">📤 Exportar Dados</div>', unsafe_allow_html=True)
    if st.button("📘 Exportar para Excel"):
        exportar_para_excel(base)
        st.success("✅ Exportação concluída! Verifique a pasta local do servidor.")

# =====================================================
# RECIBOS
# =====================================================
elif menu == "Recibos":
    st.markdown('<div class="section-header">🧾 Gerar Recibos Oficiais</div>', unsafe_allow_html=True)
    if len(base) == 0:
        st.warning("⚠️ Base de dados vazia.")
    else:
        militante_escolhido = st.selectbox("Selecionar Militante", [f"{m['nome_proprio']} {m['ultimo_nome']}" for m in base])
        if st.button("🖨️ Gerar Recibo PDF"):
            militante = next((m for m in base if f"{m['nome_proprio']} {m['ultimo_nome']}" == militante_escolhido), None)
            if militante:
                gerar_recibo_militante_pdf(militante)
                st.success("✅ Recibo gerado com sucesso!")
