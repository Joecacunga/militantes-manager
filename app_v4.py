# app_v4.py  (versão v4.3)
import streamlit as st
import pandas as pd
import os
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

# Configuração da página
st.set_page_config(page_title="Gestão de Militantes MPLA v4.3", layout="wide")
# Banner / cabeçalho com a bandeira real (se existir)
if os.path.exists("Flag_of_MPLA.svg.png"):
    st.image("Flag_of_MPLA.svg.png", use_column_width=True)

st.title("🟥🟨⬛ Gestão de Militantes MPLA v4.3")
st.markdown("**MPLA — Servir o Povo e Fazer Angola Crescer**")

# Carregar dados
base = carregar_base_dados()
localidades = carregar_localidades()

menu = st.sidebar.radio("Menu", ["Formulário", "Base de Dados", "Importar/Colar", "Exportar", "Recibos"])

# ---------- FORMULÁRIO --------------
if menu == "Formulário":
    st.header("Formulário Individual de Militante")
    with st.form("form_militante"):
        c1, c2 = st.columns(2)
        with c1:
            # Nota: registro_interno mostrado (readonly) após preencher CAP (ver abaixo)
            primeiro_nome = st.text_input("Nome(s) Próprio(s)")
            ultimo_nome = st.text_input("Último Nome")
            data_nascimento = st.text_input("Data de Nascimento (DD/MM/AAAA)")
            bi_numero = st.text_input("Portador do B.I Nº")
            arquivo_identificacao = st.text_input("Arquivo de identificação")
            estado_civil = st.text_input("Estado civil")
            # removidos: Cartão de Eleitor, Grupo
            local_trabalho = st.text_input("Local de trabalho")
            habilitacoes = st.text_input("Habilitações Literárias")
            profissao = st.text_input("Verdadeira profissão")
        with c2:
            municipio = st.selectbox("Município", list(localidades.keys()))
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

        cap_field = st.text_input("Nº CAP (Ex: CAP041)")

        # Mostrar número interno (readonly) gerado a partir da cap atual
        registro_preview = ""
        if cap_field.strip():
            registro_preview = None
            # calcula preview localmente (sem adicionar)
            registro_preview = f"REG-{cap_field.strip().upper()}-{(sum(1 for m in base if (m.get('cap') or '').strip().upper()==cap_field.strip().upper()) + 1):04d}"
            st.info(f"Nº interno (gerado por CAP): {registro_preview}")

        submitted = st.form_submit_button("💾 Guardar Militante")
        if submitted:
            if not primeiro_nome or not ultimo_nome or not cap_field.strip():
                st.error("Preencha pelo menos: Nome(s), Último Nome e Nº CAP")
            else:
                # salvar foto se foi tirada
                foto_salva = "foto_generica.jpg"
                if foto_camera is not None:
                    nome_foto = f"{cap_field.strip().upper()}_{datetime_now_str()}.jpg"
                    try:
                        with open(nome_foto, "wb") as f:
                            f.write(foto_camera.getbuffer())
                        foto_salva = nome_foto
                    except Exception:
                        foto_salva = "foto_generica.jpg"

                registro = {
                    "primeiro_nome": primeiro_nome,
                    "ultimo_nome": ultimo_nome,
                    "data_nascimento": data_nascimento,
                    "bi_numero": bi_numero,
                    "arquivo_identificacao": arquivo_identificacao,
                    "estado_civil": estado_civil,
                    "local_trabalho": local_trabalho,
                    "habilitacoes": habilitacoes,
                    "profissao": profissao,
                    "municipio": municipio,
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
                    "cap": cap_field.strip().upper()
                }
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
        id_edit = st.text_input("ID do Registo para Editar (ex: REG-CAP041-0001)")
        if id_edit:
            militante = next((m for m in base if m.get("id") == id_edit), None)
            if militante:
                # mostrar todos os campos editáveis (duas colunas)
                with st.form("form_edit"):
                    cols = st.columns(2)
                    novos = {}
                    # percorre keys ordenadas para apresentação
                    keys_show = ["primeiro_nome","ultimo_nome","cap","data_nascimento","bi_numero","estado_civil","local_trabalho","habilitacoes","profissao","ocupacao","morada","municipio","comuna","bairro","telefone","nome_pai","nome_mae","nome_conjuge","profissao_conjuge","estuda","estuda_onde","linguas","estrangeiro","foto_path"]
                    for i, key in enumerate(keys_show):
                        if i % 2 == 0:
                            novos[key] = cols[0].text_input(key.replace("_"," ").title(), militante.get(key,""))
                        else:
                            novos[key] = cols[1].text_input(key.replace("_"," ").title(), militante.get(key,""))
                    if st.form_submit_button("💾 Aplicar Alterações"):
                        atualizar_registro(base, id_edit, novos)
                        st.success("Registo atualizado!")
                        st.experimental_rerun()
            else:
                st.error("ID não encontrado.")

        st.subheader("Eliminar Registo")
        id_del = st.text_input("ID do Registo para Eliminar (ex: REG-CAP041-0001)", key="del")
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
                    st.download_button("⬇️ Baixar Recibo PDF", f, file_name=os.path.basename(caminho_pdf))
    else:
        st.info("Ainda não existem militantes registrados.")


# ----------------------------
# Pequenas utilidades locais
# ----------------------------
def datetime_now_str():
    return datetime.now().strftime("%Y%m%d%H%M%S")
