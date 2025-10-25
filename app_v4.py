# app_v4.py  (MPLA v4.6)
import streamlit as st
import os
import io
import base64
from datetime import datetime
from utils_v4 import (
    carregar_base_dados,
    guardar_base_dados,
    carregar_localidades,
    obter_comunas_por_municipio,
    adicionar_militante,
    atualizar_militante_por_cap,
    remover_por_cap,
    importar_dados_excel,
    importar_dados_texto,
    exportar_para_excel,
    gerar_recibo_pdf_bytes,
)

st.set_page_config(page_title="MPLA — SISTEMA DE GESTÃO DE MILITANTES", layout="wide")

# -------------------------
# Cabeçalho visual (bandeira pequena, tricolor decorativo, título, emblema)
# -------------------------
st.markdown("""
    <style>
    body { background-color: white; font-family: Arial, sans-serif; }
    .title-box { display:flex; align-items:center; gap:12px; }
    .tricolor { width:36px; height:14px; display:inline-block; border-radius:2px; margin-right:8px; }
    .tricolor .r { background:#D00000; width:12px; height:14px; display:inline-block; }
    .tricolor .y { background:#FFD400; width:12px; height:14px; display:inline-block; }
    .tricolor .b { background:#000000; width:12px; height:14px; display:inline-block; }
    .title { font-weight:700; font-size:20px; color:black; border:1px solid #000; padding:6px 12px; background:#fff; border-radius:6px; }
    .subtitle { color:#b30000; font-weight:700; margin-top:6px; }
    </style>
""", unsafe_allow_html=True)

cols = st.columns([1,8,1])
with cols[0]:
    if os.path.exists("Flag_of_MPLA.svg.png"):
        st.image("Flag_of_MPLA.svg.png", width=70)
with cols[1]:
    st.markdown('<div class="title-box"><div class="tricolor"><span class="r"></span><span class="y"></span><span class="b"></span></div><div class="title">MPLA — SISTEMA DE GESTÃO DE MILITANTES</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">MPLA — Servir o Povo e Fazer Angola Crescer</div>', unsafe_allow_html=True)
with cols[2]:
    if os.path.exists("EMBLEMA_MPLA (1).jpg"):
        st.image("EMBLEMA_MPLA (1).jpg", width=70)

# -------------------------
# Carregar base + localidades
# -------------------------
base = carregar_base_dados()
localidades = carregar_localidades()

# -------------------------
# Menu lateral
# -------------------------
menu = st.sidebar.selectbox("Menu", ["Página Inicial", "Formulário de Registo", "Base de Dados", "Importar/Colar", "Exportar", "Recibos", "Remover Registo", "Ajuda"])

# -------------------------
# Página Inicial
# -------------------------
if menu == "Página Inicial":
    st.header("Página Inicial")
    st.write("Bem-vindo ao MPLA — SISTEMA DE GESTÃO DE MILITANTES")
    st.write(f"Total de militantes registados: **{len(base)}**")
    st.info("Use o menu lateral para aceder ao Formulário, Base de Dados, Recibos e outras funcionalidades.")

# -------------------------
# Formulário de Registo (separado)
# -------------------------
elif menu == "Formulário de Registo":
    st.header("Formulário de Registo de Militante")
    with st.form("form_registo", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            primeiro_nome = st.text_input("Nome(s) Próprio(s)")
            ultimo_nome = st.text_input("Último Nome")
            data_nascimento = st.text_input("Data de nascimento (DD/MM/AAAA)")
            comuna_distrito = st.text_input("Comuna/Distrito Urbano")
            municipio = st.selectbox("Município", list(localidades.keys()) if localidades else [""])
            provincia = st.selectbox("Província", ["Luanda"])
            bi_numero = st.text_input("Portador do B.I Nº")
            arquivo_identificacao = st.text_input("Arquivo de identificação")
            data_emissao = st.text_input("Data de emissão do BI (DD/MM/AAAA)")
            estado_civil = st.text_input("Estado civil")
            # removidos: Cartão de eleitor, Grupo
            local_trabalho = st.text_input("Local de trabalho")
            habilitacoes = st.text_input("Habilitações Literárias")
            profissao = st.text_input("Verdadeira profissão")
        with c2:
            ocupacao = st.text_input("Ocupação actual")
            morada = st.text_input("Morada")
            comuna_endereco = st.text_input("Comuna/Distrito Urbano (endereço)")
            municipio_end = st.text_input("Município (endereço)")
            provincia_end = st.text_input("Província (endereço)", value="Luanda")
            telefone = st.text_input("Telefone nº")
            nome_pai = st.text_input("Nome do pai")
            nome_mae = st.text_input("Nome da mãe")
            nome_conjuge = st.text_input("Nome do cônjuge")
            profissao_conjuge = st.text_input("Profissão do cônjuge")
            estuda = st.selectbox("Estuda actualmente?", ["", "Sim", "Não"])
            estuda_onde = st.text_input("Se estuda, onde")
            linguas = st.text_input("Línguas que fala")
            estrangeiro = st.selectbox("Esteve no estrangeiro?", ["", "Sim", "Não"])
            motivo_estrangeiro = st.text_input("Motivo (se aplicável)")

        st.markdown("📸 Fotografia do Militante (opcional)")
        foto = st.camera_input("Tirar foto")  # returns UploadedFile-like or None
        foto_manual = st.file_uploader("Ou carregar foto (jpg/png)", type=["jpg","jpeg","png"])

        cap = st.text_input("Nº CAP (Ex: CAP041)")

        submitted = st.form_submit_button("💾 Guardar Militante")
        if submitted:
            # validações mínimas
            if not primeiro_nome or not ultimo_nome or not cap:
                st.error("Preencha pelo menos: Nome(s), Último Nome e Nº CAP.")
            else:
                # preparar registro
                registro = {
                    "primeiro_nome": primeiro_nome,
                    "ultimo_nome": ultimo_nome,
                    "data_nascimento": data_nascimento,
                    "comuna_distrito": comuna_distrito,
                    "municipio": municipio,
                    "provincia": provincia,
                    "bi_numero": bi_numero,
                    "arquivo_identificacao": arquivo_identificacao,
                    "data_emissao": data_emissao,
                    "estado_civil": estado_civil,
                    "local_trabalho": local_trabalho,
                    "habilitacoes": habilitacoes,
                    "profissao": profissao,
                    "ocupacao": ocupacao,
                    "morada": morada,
                    "comuna": comuna_endereco,
                    "municipio_end": municipio_end,
                    "provincia_end": provincia_end,
                    "telefone": telefone,
                    "nome_pai": nome_pai,
                    "nome_mae": nome_mae,
                    "nome_conjuge": nome_conjuge,
                    "profissao_conjuge": profissao_conjuge,
                    "estuda": estuda,
                    "estuda_onde": estuda_onde,
                    "linguas": linguas,
                    "estrangeiro": estrangeiro,
                    "motivo_estrangeiro": motivo_estrangeiro,
                    "cap": cap.strip().upper()
                }

                # tratar foto: preferir foto da camera, senão ficheiro manual
                foto_b64 = ""
                if foto is not None:
                    foto_bytes = foto.getbuffer()
                    foto_b64 = base64.b64encode(foto_bytes).decode("utf-8")
                elif foto_manual is not None:
                    foto_bytes = foto_manual.read()
                    foto_b64 = base64.b64encode(foto_bytes).decode("utf-8")
                if foto_b64:
                    registro["foto_b64"] = foto_b64

                base, ok, msg = adicionar_militante(base, registro)
                if ok:
                    st.success(msg)
                    # limpar form automaticamente: não há clear_on_submit global para todos campos, recarregamos a página
                    st.experimental_rerun()
                else:
                    st.error(msg)

# -------------------------
# Base de Dados
# -------------------------
elif menu == "Base de Dados":
    st.header("Base de Dados")
    if not base:
        st.info("Base de dados vazia.")
    else:
        df = pd.DataFrame(base)
        st.dataframe(df, use_container_width=True)

        st.markdown("### Editar por Nº CAP")
        cap_edit = st.text_input("Nº CAP para editar (Ex: CAP041)")
        if cap_edit:
            militantes = [m for m in base if (m.get("cap") or "").strip().upper() == cap_edit.strip().upper()]
            if not militantes:
                st.warning("Nenhum registo encontrado.")
            else:
                m = militantes[0]
                with st.form("edit_form"):
                    p1, p2 = st.columns(2)
                    with p1:
                        primeiro_e = st.text_input("Nome(s)", m.get("primeiro_nome",""))
                        ultimo_e = st.text_input("Último nome", m.get("ultimo_nome",""))
                        telefone_e = st.text_input("Telefone", m.get("telefone",""))
                        municipio_e = st.selectbox("Município", list(localidades.keys()), index=list(localidades.keys()).index(m.get("municipio")) if m.get("municipio") in localidades else 0)
                    with p2:
                        profissao_e = st.text_input("Profissão", m.get("profissao",""))
                        bairro_e = st.text_input("Bairro", m.get("bairro",""))
                        foto_file = st.file_uploader("Substituir foto (opcional)", type=["jpg","jpeg","png"])
                    if st.form_submit_button("💾 Aplicar Alterações"):
                        novos = {
                            "primeiro_nome": primeiro_e,
                            "ultimo_nome": ultimo_e,
                            "telefone": telefone_e,
                            "municipio": municipio_e,
                            "profissao": profissao_e,
                            "bairro": bairro_e
                        }
                        # foto substituição
                        if foto_file is not None:
                            novos["foto_b64"] = base64.b64encode(foto_file.read()).decode("utf-8")
                        ok = atualizar_militante_por_cap(base, cap_edit.strip().upper(), novos)
                        if ok:
                            st.success("Registo atualizado.")
                            st.experimental_rerun()
                        else:
                            st.error("Falha ao atualizar.")

# -------------------------
# Importar / Colar
# -------------------------
elif menu == "Importar/Colar":
    st.header("Importar / Colar Dados")
    uploaded = st.file_uploader("Carregar .xlsx ou .csv", type=["xlsx","csv"])
    if uploaded:
        base, added = importar_dados_excel(base, uploaded)
        st.success(f"{added} registos adicionados.")
    st.markdown("---")
    texto = st.text_area("Colar dados (TAB ou |) — cada linha = 1 registo")
    if st.button("📥 Processar Colagem"):
        base, added = importar_dados_texto(base, texto)
        st.success(f"{added} registos adicionados por colagem.")

# -------------------------
# Exportar
# -------------------------
elif menu == "Exportar":
    st.header("Exportar Base")
    if st.button("📤 Exportar para Excel"):
        caminho = exportar_para_excel(base)
        if caminho and os.path.exists(caminho):
            with open(caminho, "rb") as f:
                st.download_button("⬇️ Baixar Excel", f, file_name=os.path.basename(caminho))
        else:
            st.error("Nenhum registo para exportar.")

# -------------------------
# Recibos
# -------------------------
elif menu == "Recibos":
    st.header("Gerar Recibo Oficial")
    if not base:
        st.info("Sem registos.")
    else:
        escolhas = [f"{m.get('primeiro_nome','')} {m.get('ultimo_nome','')} — {m.get('cap','')}" for m in base]
        sel = st.selectbox("Selecionar Militante", escolhas)
        if st.button("🧾 Gerar Recibo / Download"):
            idx = escolhas.index(sel)
            militante = base[idx]
            pdf_bytes = gerar_recibo_pdf_bytes(militante)
            if pdf_bytes:
                st.success("Recibo gerado com sucesso — faça o download abaixo.")
                st.download_button(
                    "⬇️ Baixar Recibo PDF",
                    data=pdf_bytes,
                    file_name=f"Recibo_{militante.get('cap')}.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("Erro ao gerar recibo.")

# -------------------------
# Remover Registo
# -------------------------
elif menu == "Remover Registo":
    st.header("Remover Registo por CAP")
    cap_rem = st.text_input("Nº CAP (Ex: CAP041)")
    nome_rem = st.text_input("Nome (opcional)")
    if st.button("🗑️ Remover"):
        if not cap_rem:
            st.warning("Informe o Nº CAP.")
        else:
            base = remover_por_cap(base, cap_rem.strip().upper(), nome_rem.strip() or None)
            st.success("Operação concluída.")
            st.experimental_rerun()

# -------------------------
# Ajuda
# -------------------------
elif menu == "Ajuda":
    st.header("Ajuda / Instruções")
    st.write("- Preencha o formulário em 'Formulário de Registo'.")
    st.write("- A fotografia pode ser capturada com a câmara ou carregada.")
    st.write("- O recibo é gerado em memória e disponibilizado para download imediato.")
    st.write("- Use 'Base de Dados' para editar e 'Exportar' para baixar em Excel.")
