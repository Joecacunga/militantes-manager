import streamlit as st
import pandas as pd
import json
from pathlib import Path
from utils_v3 import (
    normalizar_telefone,
    validar_cap,
    carregar_base,
    guardar_base,
    adicionar_militante,
    importar_excel_para_base,
    gerar_relatorio_excel,
    carregar_localidades,
    importar_paste_texto
)

st.set_page_config(page_title="Gestão de Militantes — v3", layout="wide")
st.title("📋 Sistema de Registo de Militantes — v3 (Híbrido)")

DATA_DIR = Path(".")
BASE_FILE = DATA_DIR / "base_militantes.json"
LOCALIDADES_FILE = DATA_DIR / "localidades_luanda_v3.json"

localidades = carregar_localidades(str(LOCALIDADES_FILE))
base = carregar_base(str(BASE_FILE))

st.sidebar.header("⚙️ Ações Rápidas / Base de Dados")
with st.sidebar.expander("📁 Base de Dados"):
    st.write(f"Ficheiro base: `{BASE_FILE.name}`")
    if st.button("🔄 Recarregar base"):
        base = carregar_base(str(BASE_FILE))
        st.sidebar.success("Base recarregada.")
    if st.button("💾 Fazer download do JSON da base"):
        if BASE_FILE.exists():
            with open(BASE_FILE, "r", encoding="utf-8") as f:
                dados = f.read()
            st.sidebar.download_button("⬇️ Baixar base_militantes.json", data=dados, file_name="base_militantes.json", mime="application/json")
        else:
            st.sidebar.info("Ainda não existe ficheiro base. Adiciona registos primeiro.")

st.sidebar.markdown('---')
st.sidebar.header("📍 Seleção global (opcional)")
prov_default = st.sidebar.selectbox("Província (padrão)", list(localidades.keys()))
municipios_list = sorted(localidades.get(prov_default, {}).keys())
municipio_default = st.sidebar.selectbox("Município (padrão)", municipios_list)
comunas_list = sorted(localidades.get(prov_default, {}).get(municipio_default, {}).keys())
comuna_default = st.sidebar.selectbox("Comuna (padrão)", comunas_list if comunas_list else ["-"])
st.sidebar.markdown('---')

tab_import, tab_form, tab_dupes, tab_stats, tab_db, tab_export = st.tabs([
    "📂 Importar Dados", "✍️ Registar Militante", "🔍 Duplicados", "📈 Estatísticas", "📚 Base de Dados", "📤 Exportar"
])

with tab_import:
    st.header("📂 Importar ficheiros (.xlsx / .csv) ou colar dados")
    st.write("Ao importar, os registos serão validados e mesclados na base sem duplicações.")
    col1, col2 = st.columns(2)
    with col1:
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
    with col2:
        st.write("📋 Colar dados (do Excel/Word). Cada linha = 1 registo. Utiliza separador TAB ou |")
        pasted = st.text_area("Colar aqui (CTRL+V) — exemplo de cabeçalho: Nome(s) Próprio(s)\tÚltimo Nome\tNº CAP\tTelefone\tCartão\tMunicípio\tComuna\tBairro", height=200)
        if st.button("📥 Importar do texto colado"):
            if not pasted.strip():
                st.error("Nenhum texto colado.")
            else:
                try:
                    base, stats = importar_paste_texto(base, pasted)
                    guardar_base(base, str(BASE_FILE))
                    st.success(f"Importação por colagem concluída: {stats.get('added',0)} adicionados, {stats.get('skipped_invalid',0)} inválidos, {stats.get('skipped_duplicates',0)} duplicados.")
                    st.json(stats)
                except Exception as e:
                    st.error(f"Erro ao importar texto: {e}")

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
        comuna_opts = sorted(localidades.get(prov, {}).get(mun, {}).keys())
        if comuna_opts:
            com = st.selectbox("Comuna", options=comuna_opts, index=comuna_opts.index(comuna_default) if comuna_default in comuna_opts else 0)
            bairro = st.text_input("Bairro (manual)", value="")
        else:
            st.info("Este município não possui comunas definidas. Introduz o bairro manualmente.")
            com = ""
            bairro = st.text_input("Bairro (manual)")
        submitted = st.form_submit_button("💾 Salvar Militante")
        if submitted:
            if not nomes.strip() or not apelido.strip():
                st.error("Por favor preenche Nome(s) Próprio(s) e Último Nome.")
            elif not validar_cap(cap_in):
                st.error("Formato de Nº CAP inválido. Use CAP + números (ex.: CAP041).")
            else:
                tel_norm = normalizar_telefone(telefone_in)
                if not tel_norm:
                    st.error("Telefone inválido. Introduz 9 dígitos ou +244...")
                else:
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

with tab_dupes:
    st.header("🔍 Duplicados na base (Nome(s)+Apelido+Telefone+Nº CAP)")
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
        dup_mask = df_all.duplicated(subset=["Nome(s) Próprio(s)","Último Nome","Telefone","Nº CAP"], keep=False)
        df_dupes = df_all[dup_mask].sort_values(["Nº CAP","Último Nome"])
        if df_dupes.empty:
            st.success("Nenhum duplicado detectado.")
        else:
            st.dataframe(df_dupes)

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

with tab_db:
    st.header("📚 Base de Dados — Visualizar / Editar / Eliminar")
    rows = []
    for cap, lst in base.items():
        for r in lst:
            rr = r.copy()
            rr["_CAP"] = cap
            rows.append(rr)
    if not rows:
        st.info("Base vazia. Adiciona registos para visualizar aqui.")
    else:
        df = pd.DataFrame(rows)
        st.write("Filtro rápido:")
        fcol1, fcol2, fcol3 = st.columns(3)
        cap_filter = fcol1.selectbox("Filtrar por Nº CAP", options=["Todas"] + sorted(list({r["Nº CAP"] for r in rows})))
        mun_filter = fcol2.selectbox("Filtrar por Município", options=["Todos"] + sorted(list({r["Município"] for r in rows})))
        search = fcol3.text_input("Pesquisar nome ou telefone")
        df_filtered = df.copy()
        if cap_filter!="Todas":
            df_filtered = df_filtered[df_filtered["Nº CAP"]==cap_filter]
        if mun_filter!="Todos":
            df_filtered = df_filtered[df_filtered["Município"]==mun_filter]
        if search.strip():
            df_filtered = df_filtered[df_filtered.apply(lambda x: search.lower() in str(x["Nome(s) Próprio(s)"]).lower() or search.lower() in str(x["Telefone"]), axis=1)]
        st.dataframe(df_filtered.reset_index(drop=True))
        st.markdown('---')
        st.subheader("✏️ Editar um registo")
        with st.form("form_edit"):
            cap_sel = st.selectbox("Escolhe o Nº CAP", options=sorted(df["Nº CAP"].unique()))
            options = [f'{r["Nº Ordem"]} - {r["Nome(s) Próprio(s)"]} {r["Último Nome"]}' for r in base.get(cap_sel,[])]
            idx = st.selectbox("Escolhe o registo (Nº Ordem)", options=options)
            ordem = int(idx.split(" - ")[0])
            rec = next((r for r in base.get(cap_sel,[]) if r.get("Nº Ordem")==ordem), None)
            if rec:
                e_nome = st.text_input("Nome(s) Próprio(s)", value=rec.get("Nome(s) Próprio(s)",""))
                e_apelido = st.text_input("Último Nome", value=rec.get("Último Nome",""))
                e_tel = st.text_input("Telefone", value=rec.get("Telefone",""))
                e_cartao = st.selectbox("Cartão", options=["Sim","Não"], index=0 if rec.get("Cartão","").lower()=="sim" else 1)
                e_bairro = st.text_input("Bairro", value=rec.get("Bairro",""))
                if st.form_submit_button("💾 Guardar alterações"):
                    teln = normalizar_telefone(e_tel)
                    if not teln:
                        st.error("Telefone inválido.")
                    else:
                        rec["Nome(s) Próprio(s)"] = e_nome.strip()
                        rec["Último Nome"] = e_apelido.strip()
                        rec["Telefone"] = teln
                        rec["Cartão"] = e_cartao
                        rec["Bairro"] = e_bairro.strip()
                        guardar_base(base, str(BASE_FILE))
                        st.success("Registo atualizado com sucesso.")
            else:
                st.error("Registo não encontrado.")
        st.markdown('---')
        st.subheader("🗑️ Eliminar um registo")
        with st.form("form_delete"):
            cap_del = st.selectbox("Escolhe o Nº CAP (delete)", options=sorted(df["Nº CAP"].unique()), key="cap_del")
            opts_del = [f'{r["Nº Ordem"]} - {r["Nome(s) Próprio(s)"]} {r["Último Nome"]}' for r in base.get(cap_del,[])]
            sel_del = st.selectbox("Registo a eliminar", options=opts_del, key="opt_del")
            if st.form_submit_button("🗑️ Eliminar registo"):
                ord_del = int(sel_del.split(" - ")[0])
                base[cap_del] = [r for r in base.get(cap_del,[]) if r.get("Nº Ordem")!=ord_del]
                guardar_base(base, str(BASE_FILE))
                st.success("Registo eliminado com sucesso.")

with tab_export:
    st.header("📤 Exportar relatórios e backups")
    if st.button("📦 Gerar relatório Excel (uma folha por CAP + resumo)"):
        try:
            bio = gerar_relatorio_excel(base)
            st.download_button("⬇️ Baixar relatório Excel", data=bio, file_name="Relatorio_Militantes.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        except Exception as e:
            st.error(f"Erro ao gerar relatório: {e}")
    st.markdown('---')
    st.write("Exportar/Importar base completa (JSON):")
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
