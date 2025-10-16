import streamlit as st
import pandas as pd
import json
from utils_v4 import (
    carregar_base_dados,
    guardar_base_dados,
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
# 🔸 Cabeçalho e inicialização
# =====================================================

st.set_page_config(page_title="Gestão de Militantes MPLA v4.1", layout="wide")
st.title("🟥🟨⬛ Gestão de Militantes MPLA v4.1")
st.caption("Servir o Povo e Fazer Angola Crescer")

# Carregar base e localidades
base = carregar_base_dados()
localidades = carregar_localidades()

menu = st.sidebar.radio("📋 Menu", ["Formulário", "Base de Dados", "Gerar Recibo"])

# =====================================================
# 🔸 1. FORMULÁRIO
# =====================================================

if menu == "Formulário":
    st.header("➕ Registar Novo Militante")

    col1, col2 = st.columns(2)
    with col1:
        primeiro_nome = st.text_input("Nome(s) Próprio(s)")
        ultimo_nome = st.text_input("Último Nome")
        cap = st.text_input("Nº CAP", placeholder="Ex: CAP001")
        telefone = st.text_input("Telefone", placeholder="Ex: 923456789")

    with col2:
        cartao = st.text_input("Nº de Cartão de Eleitor")
        provincia = st.selectbox("Província", ["Luanda"])
        municipio = st.selectbox("Município", list(localidades.keys()))

        comunas = obter_comunas_por_municipio(municipio, localidades)
        if comunas:
            comuna = st.selectbox("Comuna", comunas)
        else:
            comuna = st.text_input("Comuna (manual)", "")

        bairro = st.text_input("Bairro")

    if st.button("💾 Guardar Militante"):
        novo_militante = {
            "primeiro_nome": primeiro_nome,
            "ultimo_nome": ultimo_nome,
            "cap": cap,
            "telefone": telefone,
            "cartao": cartao,
            "provincia": provincia,
            "municipio": municipio,
            "comuna": comuna,
            "bairro": bairro,
        }
        base = adicionar_militante(base, novo_militante)
        st.success("✅ Militante registado com sucesso!")
        st.experimental_rerun()

# =====================================================
# 🔸 2. BASE DE DADOS
# =====================================================

elif menu == "Base de Dados":
    st.header("📁 Base de Dados de Militantes")
    df = pd.DataFrame(base)

    if not df.empty:
        st.dataframe(df, use_container_width=True)

        id_edit = st.text_input("Digite o ID para editar")
        if id_edit:
            militante = next((m for m in base if m.get("id") == id_edit), None)
            if militante:
                st.subheader("✏️ Editar Registo")
                for chave in militante.keys():
                    novo_valor = st.text_input(chave, militante[chave])
                    militante[chave] = novo_valor

                if st.button("💾 Atualizar"):
                    atualizar_registro(base, id_edit, militante)
                    st.success("Registo atualizado!")
                    st.experimental_rerun()

        id_del = st.text_input("Digite o ID para eliminar")
        if id_del and st.button("🗑️ Eliminar"):
            base = remover_registro(base, id_del)
            st.warning("Registo eliminado!")
            st.experimental_rerun()

        st.divider()
        if st.button("📤 Exportar Excel"):
            arquivo = exportar_para_excel(base)
            with open(arquivo, "rb") as f:
                st.download_button("⬇️ Baixar Base Excel", f, file_name="Base_Militantes.xlsx")

    else:
        st.info("Nenhum militante registado ainda.")

# =====================================================
# 🔸 3. GERAR RECIBO
# =====================================================

elif menu == "Gerar Recibo":
    st.header("🧾 Gerar Recibo Oficial do Militante")

    if base:
        nomes = [f"{m['id']} - {m['primeiro_nome']} {m['ultimo_nome']}" for m in base]
        escolha = st.selectbox("Selecione o Militante", nomes)

        if st.button("📄 Gerar Recibo PDF"):
            militante_id = escolha.split(" - ")[0]
            militante = next((m for m in base if m["id"] == militante_id), None)
            if militante:
                pdf_path = gerar_recibo_militante_pdf(militante)
                with open(pdf_path, "rb") as f:
                    st.download_button("⬇️ Baixar Recibo PDF", f, file_name=pdf_path)
    else:
        st.warning("Nenhum militante disponível para gerar recibo.")
