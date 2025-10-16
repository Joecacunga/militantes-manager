# app_v4.py
import streamlit as st
import pandas as pd
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

st.set_page_config(page_title="Gestão de Militantes MPLA v4", layout="wide")
st.title("🟥🟨⬛ Gestão de Militantes MPLA v4")
st.caption("Servir o Povo e Fazer Angola Crescer")

# Carregar base e localidades
base = carregar_base_dados()
localidades = carregar_localidades()

menu = st.sidebar.radio("Menu", ["Formulário", "Base de Dados", "Importar/Colar", "Exportar", "Recibos"])

# ---------- FORMULÁRIO --------------
if menu == "Formulário":
    st.header("Formulário Individual de Militante")

    with st.form("form_militante"):
        c1, c2 = st.columns(2)
        with c1:
            numero = st.text_input("Nº (registro interno)")
            primeiro_nome = st.text_input("Nome(s) Próprio(s)")
            ultimo_nome = st.text_input("Último Nome")
            data_nascimento = st.text_input("Data de Nascimento (DD/MM/AAAA)")
            comuna_distrito = st.text_input("Comuna/Distrito Urbano")
            municipio = st.selectbox("Município", list(localidades.keys()))
            provincia = st.selectbox("Província", ["Luanda"])
            bi_numero = st.text_input("Portador do B.I Nº")
            arquivo_identificacao = st.text_input("Arquivo de identificação")
            estado_civil = st.text_input("Estado civil")
            cartao = st.text_input("Número do Cartão de Eleitor")
            grupo = st.text_input("Grupo")
            local_trabalho = st.text_input("Local de trabalho")
            habilitacoes = st.text_input("Habilitações Literárias")
            profissao = st.text_input("Verdadeira profissão")
        with c2:
            ocupacao = st.text_input("Ocupação actual")
            morada = st.text_input("Morada")
            comunas = obter_comunas_por_municipio(municipio, localidades)
            if comunas:
                comuna = st.selectbox("Comuna", comunas)
            else:
                comuna = st.text_input("Comuna (manual)")
            bairro = st.text_input("Bairro")
            telefone = st.text_input("Telefone nº")
            nome_pai = st.text_input("Nome do pai")
            nome_mae = st.text_input("Nome da mãe")
            nome_conjuge = st.text_input("Nome do cônjuge")
            profissao_conjuge = st.text_input("Profissão do cônjuge")
            estuda = st.text_input("Estuda actualmente (Sim/Não)")
            estuda_onde = st.text_input("Se estuda onde")
            linguas = st.text_input("Línguas que fala")
            estrangeiro = st.text_input("Esteve no estrangeiro (Motivo)")

            st.markdown("📸 **Fotografia do Militante**")
            foto_camera = st.camera_input("Tirar Foto (opcional)")
            foto_path_manual = st.text_input("Ou indicar caminho/nome da foto (opcional)")

        cap_field = st.text_input("Nº CAP (Ex: CAP041)")

        submitted = st.form_submit_button("💾 Guardar Militante")
        if submitted:
            foto_salva = foto_path_manual or "foto_generica.jpg"
            # se foto da camera foi tirada, gravar com nome baseado no CAP se existir
            if foto_camera is not None:
                nome_foto = (cap_field.strip() or f"foto_{len(base)+1}").replace(" ", "_") + ".jpg"
                with open(nome_foto, "wb") as f:
                    f.write(foto_camera.getbuffer())
                foto_salva = nome_foto

            registro = {
                "numero": numero,
                "primeiro_nome": primeiro_nome,
                "ultimo_nome": ultimo_nome,
                "data_nascimento": data_nascimento,
                "comuna_distrito": comuna_distrito,
                "municipio": municipio,
                "provincia": provincia,
                "bi_numero": bi_numero,
                "arquivo_identificacao": arquivo_identificacao,
                "estado_civil": estado_civil,
                "cartao": cartao,
                "grupo": grupo,
                "local_trabalho": local_trabalho,
                "habilitacoes": habilitacoes,
                "profissao": profissao,
                "ocupacao": ocupacao,
                "morada": morada,
                "comuna": comuna,
                "bairro": bairro,
                "telefone": telefone,
                "nome_pai": nome_pai,
                "nome_mae": nome_mae,
                "nome_conjuge": nome_conjuge,
                "profissao_conjuge": profissao_conjuge,
                "estuda": estuda,
                "estuda_onde": estuda_onde,
                "linguas": linguas,
                "estrangeiro": estrangeiro,
                "foto_path": foto_salva,
                "cap": cap_field
            }
            if not registro["primeiro_nome"] or not registro["ultimo_nome"] or not registro["cap"]:
                st.error("Preencha pelo menos: Nome(s), Último Nome e Nº CAP")
            else:
                base, ok, msg = adicionar_militante(base, registro)
                if ok:
                    st.success(msg)
                    st.experimental_rerun()
                else:
                    st.error(msg)

# ---------- BASE DE DADOS --------------
elif menu == "Base de Dados":
    st.header("Base de Dados de Militantes")
    if base:
        df = pd.DataFrame(base)
        st.dataframe(df, use_container_width=True)

        st.subheader("Editar um Registo")
        id_edit = st.text_input("ID do Registo para Editar (ex: 01)")
        if id_edit:
            militante = next((m for m in base if m.get("id") == id_edit), None)
            if militante:
                edit_cols = st.columns(2)
                with edit_cols[0]:
                    novo_primeiro = st.text_input("Nome(s) próprio(s)", militante.get("primeiro_nome",""))
                    novo_ultimo = st.text_input("Último nome", militante.get("ultimo_nome",""))
                    novo_cap = st.text_input("Nº CAP", militante.get("cap",""))
                    novo_telefone = st.text_input("Telefone", militante.get("telefone",""))
                    novo_cartao = st.text_input("Nº Cartão", militante.get("cartao",""))
                with edit_cols[1]:
                    novo_municipio = st.selectbox("Município", list(localidades.keys()), index=list(localidades.keys()).index(militante.get("municipio")) if militante.get("municipio") in localidades else 0)
                    comunas_list = obter_comunas_por_municipio(novo_municipio, localidades)
                    if comunas_list:
                        novo_comuna = st.selectbox("Comuna", comunas_list, index=comunas_list.index(militante.get("comuna")) if militante.get("comuna") in comunas_list else 0)
                    else:
                        novo_comuna = st.text_input("Comuna (manual)", militante.get("comuna",""))
                    novo_bairro = st.text_input("Bairro", militante.get("bairro",""))

                if st.button("💾 Aplicar Alterações"):
                    novos = {
                        "primeiro_nome": novo_primeiro,
                        "ultimo_nome": novo_ultimo,
                        "cap": novo_cap,
                        "telefone": novo_telefone,
                        "municipio": novo_municipio,
                        "comuna": novo_comuna,
                        "bairro": novo_bairro
                    }
                    atualizar_registro(base, id_edit, novos)
                    st.success("Registo atualizado!")
                    st.experimental_rerun()
            else:
                st.error("ID não encontrado.")

        st.subheader("Eliminar Registo")
        id_del = st.text_input("ID do Registo para Eliminar (ex: 01)", key="del")
        if id_del and st.button("🗑️ Eliminar Registo"):
            base = remover_registro(base, id_del)
            st.success("Registo eliminado.")
            st.experimental_rerun()
    else:
        st.info("Ainda não existem registos.")

# ---------- IMPORTAR / COLAR --------------
elif menu == "Importar/Colar":
    st.header("Importar dados")
    uploaded = st.file_uploader("Carregar ficheiro .xlsx ou .csv", type=["xlsx","csv"])
    if uploaded:
        regs = importar_dados_excel(uploaded)
        added = 0
        for r in regs:
            base, ok, msg = adicionar_militante(base, r)
            if ok:
                added += 1
        st.success(f"{added} registos importados.")
        st.experimental_rerun()

    st.write("---")
    st.subheader("Colar dados (TAB ou |)")
    texto = st.text_area("Cole aqui os registos (cada linha = 1 registo)")
    if st.button("📥 Processar Colagem"):
        regs = importar_dados_texto(texto)
        added = 0
        for r in regs:
            base, ok, msg = adicionar_militante(base, r)
            if ok:
                added += 1
        st.success(f"{added} registos adicionados por colagem.")
        st.experimental_rerun()

# ---------- EXPORTAR --------------
elif menu == "Exportar":
    st.header("Exportar Base")
    if base and st.button("📤 Exportar para Excel"):
        caminho = exportar_para_excel(base)
        with open(caminho, "rb") as f:
            st.download_button("⬇️ Baixar Base em Excel", f, file_name="Base_Militantes.xlsx")
    else:
        st.info("Não há registos para exportar.")

# ---------- RECIBOS --------------
elif menu == "Recibos":
    st.header("Gerar Recibo Oficial")
    if base:
        opcoes = [f"{m['id']} - {m.get('primeiro_nome','')} {m.get('ultimo_nome','')}" for m in base]
        escolha = st.selectbox("Selecionar Militante", opcoes)
        if st.button("🧾 Gerar Recibo"):
            mil_id = escolha.split(" - ")[0]
            militante = next((m for m in base if m['id']==mil_id), None)
            if militante:
                caminho_pdf = gerar_recibo_militante_pdf(militante)
                with open(caminho_pdf, "rb") as f:
                    st.download_button("⬇️ Baixar Recibo PDF", f, file_name=caminho_pdf)
    else:
        st.info("Ainda não existem militantes registrados.")
