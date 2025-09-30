import streamlit as st
import pandas as pd
import json
from pathlib import Path
from utils_v2 import (
    normalizar_telefone,
    validar_cap,
    carregar_base,
    guardar_base,
    adicionar_militante,
    importar_excel_para_base,
    gerar_relatorio_excel,
    carregar_localidades,
)

# Config
st.set_page_config(page_title="Gestão de Militantes — v2", layout="wide")
st.title("📋 Sistema de Registo de Militantes — v2 (Híbrido)")

DATA_DIR = Path(".")
BASE_FILE = DATA_DIR / "base_militantes.json"
LOCALIDADES_FILE = DATA_DIR / "localidades_luanda.json"

# Carregar localidades e base
localidades = carregar_localidades(str(LOCALIDADES_FILE))
base = carregar_base(str(BASE_FILE))

# --- Sidebar: localização e ações ---
st.sidebar.header("⚙️ Configuração / Ações Rápidas")

with st.sidebar.expander("📁 Base de dados"):
    st.write(f"Ficheiro base: `{BASE_FILE.name}`")
    if st.button("🔄 Recarregar base"):
        base = carregar_base(str(BASE_FILE))
        st.sidebar.success("Base recarregada.")

    if st.button("💾 Fazer download do JSON da base"):
        st.sidebar.download_button("⬇️ Baixar base_militantes.json", data=json.dumps(base, ensure_ascii=False, indent=2), file_name="base_militantes.json", mime="application/json")

st.sidebar.markdown("---")
st.sidebar.header("📍 Seleção global de localização (opcional)")
prov_default = st.sidebar.selectbox("Província (padrão)", list(localidades.keys()))
# Municípios dependentes
municipios_list = sorted(localidades.get(prov_default, {}).keys())
municipio_default = st.sidebar.selectbox("Município (padrão)", municipios_list)
comunas_list = sorted(localidades.get(prov_default, {}).get(municipio_default, {}).keys())
comuna_default = st.sidebar.selectbox("Comuna (padrão)", comunas_list)
st.sidebar.markdown("---")

# --- Tabs principais ---
tab_import, tab_form, tab_dupes, tab_stats, tab_export = st.tabs([
    "📂 Importar Dados", "✍️ Registar Militante", "🔍 Duplicados", "📈 Estatísticas", "📤 Exportar"
])

# -------------------- TAB: IMPORTAR --------------------
with tab_import:
    st.header("📂 Importar ficheiros (.xlsx / .csv)")
    st.write("Ao importar, os registos serão validados e mesclados na base sem duplicações.")
    uploaded = st.file_uploader("Carregar ficheiro Excel (.xlsx) ou CSV", type=["xlsx","csv"])
    if uploaded is not None:
        try:
            n_before = sum(len(v) for v in base.values())
            base, stats = importar_excel_para_base(base, uploaded)
            guardar_base(base, str(BASE_FILE))
            n_after = sum(len(v) for v in base.values())
            st.success(f"Importação concluída: +{n_after-n_before} registos adicionados (total agora {n_after}).")
            st.write("Resumo da importação:")
            st.json(stats)
        except Exception as e:
            st.error(f"Erro na importação: {e}")

# -------------------- TAB: FORMULÁRIO --------------------
with tab_form:
    st.header("✍️ Formulário: Adicionar novo militante")
    with st.form("form_militante", clear_on_submit=False):
        col1, col2 = st.columns([2,1])
        with col1:
            nomes = st.text_input("Nome(s) Próprio(s) *", help="Aceita múltiplos nomes (ex.: José António)")
            apelido = st.text_input("Último Nome (Apelido) *")
        with col2:
            cap_in = st.text_input("Nº CAP *", value="CAP", help="Formato obrigatório: CAP seguido de números (ex.: CAP041)")
            telefone_in = st.text_input("Telefone *", help="9 dígitos angolanos; aceitamos +244 ou 244 como prefixo")
            cartao = st.selectbox("Cartão de Militante", options=["Sim","Não"])
        col3, col4 = st.columns(2)
        with col3:
            prov = st.selectbox("Província", options=list(localidades.keys()), index=list(localidades.keys()).index(prov_default))
        with col4:
            mun_list = sorted(localidades.get(prov, {}).keys())
            mun = st.selectbox("Município", options=mun_list, index=mun_list.index(municipio_default) if municipio_default in mun_list else 0)
        # Comunas dependentes
        comuna_opts = sorted(localidades.get(prov, {}).get(mun, {}).keys())
        com = st.selectbox("Comuna", options=comuna_opts, index=comuna_opts.index(comuna_default) if comuna_default in comuna_opts else 0)
        bairro_opts = localidades.get(prov, {}).get(mun, {}).get(com, []) or []
        bairro = st.selectbox("Bairro", options=bairro_opts if bairro_opts else ["-"], index=0)
        submitted = st.form_submit_button("💾 Salvar Militante")
        if submitted:
            # Validações
            if not nomes.strip() or not apelido.strip():
                st.error("Por favor preenche Nome(s) Próprio(s) e Último Nome.")
            elif not validar_cap(cap_in):
                st.error("Formato de Nº CAP inválido. Use CAP + números (ex.: CAP041).")
            else:
                tel_norm = normalizar_telefone(telefone_in)
                if not tel_norm:
                    st.error("Telefone inválido. Introduz 9 dígitos ou +244...")
                else:
                    # Preparar registo
                    reg = {
                        "Nome(s) Próprio(s)": " ".join(nomes.split()),
                        "Último Nome": apelido.strip(),
                        "Nº CAP": cap_in.strip().upper().replace(" ","").replace("-",""),
                        "Telefone": tel_norm,
                        "Cartão": cartao,
                        "Província": prov,
                        "Município": mun,
                        "Comuna": com,
                        "Bairro": bairro
                    }
                    ok, msg = adicionar_militante(base, reg)
                    if ok:
                        guardar_base(base, str(BASE_FILE))
                        st.success("Militante registado com sucesso!")
                    else:
                        st.warning(f"Registo não adicionado: {msg}")

# -------------------- TAB: DUPLICADOS --------------------
with tab_dupes:
    st.header("🔍 Duplicados na base (Nome(s)+Apelido+Telefone+Nº CAP)")
    # Criar lista plana
    rows = []
    for cap, lst in base.items():
        for r in lst:
            row = r.copy()
            row["_CAP"] = cap
            rows.append(row)
    if not rows:
        st.info("A base está vazia. Importa ficheiros ou adiciona manualmente.")
    else:
        df_all = pd.DataFrame(rows)
        # detectar duplicados exatos nas colunas chave
        dup_mask = df_all.duplicated(subset=["Nome(s) Próprio(s)","Último Nome","Telefone","Nº CAP"], keep=False)
        df_dupes = df_all[dup_mask].sort_values(["Nº CAP","Último Nome"])
        if df_dupes.empty:
            st.success("Nenhum duplicado detectado.")
        else:
            st.dataframe(df_dupes)

# -------------------- TAB: ESTATÍSTICAS --------------------
with tab_stats:
    st.header("📈 Estatísticas e Resumo")
    total_militantes = sum(len(v) for v in base.values())
    total_caps = len(base.keys())
    com_cartao = sum(1 for lst in base.values() for r in lst if r.get("Cartão","").lower()=="sim")
    sem_cartao = total_militantes - com_cartao
    st.metric("Total de Militantes", total_militantes)
    st.metric("Total de CAPs", total_caps)
    st.metric("Com Cartão", com_cartao)
    st.metric("Sem Cartão", sem_cartao)

    if total_militantes>0:
        df_stats = pd.DataFrame([r for lst in base.values() for r in lst])
        caps_count = df_stats["Nº CAP"].value_counts().reset_index()
        caps_count.columns = ["Nº CAP","Total"]
        st.subheader("Contagem por CAP")
        st.dataframe(caps_count)
        try:
            import plotly.express as px
            fig = px.bar(caps_count, x="Nº CAP", y="Total", title="Militantes por CAP", text="Total")
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.write("Plotly não disponível para gráficos interativos.")

# -------------------- TAB: EXPORTAR --------------------
with tab_export:
    st.header("📤 Exportar relatórios e backups")
    if st.button("📦 Gerar relatório Excel (uma folha por CAP + resumo)"):
        try:
            bio = gerar_relatorio_excel(base)
            st.download_button("⬇️ Baixar relatório Excel", data=bio, file_name="Relatorio_Militantes.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        except Exception as e:
            st.error(f"Erro ao gerar relatório: {e}")
    st.markdown("---")
    st.write("Exportar/Importar base completa (JSON):")
    if st.button("📥 Importar base JSON (substitui atual)"):
        st.info("Para importar JSON substituto, use o upload abaixo e depois confirme a substituição.")
    uploaded_json = st.file_uploader("Carregar ficheiro JSON da base (opcional)", type=["json"])
    if uploaded_json is not None:
        try:
            loaded = json.load(uploaded_json)
            st.write("Preview do ficheiro JSON carregado:")
            st.json(loaded)
            if st.button("⚠️ Substituir base com este JSON"):
                guardar_base(loaded, str(BASE_FILE))
                base = carregar_base(str(BASE_FILE))
                st.success("Base substituída com sucesso.")
        except Exception as e:
            st.error(f"Erro ao carregar JSON: {e}")
