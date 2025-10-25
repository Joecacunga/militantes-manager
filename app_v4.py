import pandas as pd
import json
import io
from fpdf import FPDF
from datetime import datetime
import os

# ----------------------------------------------------
# BASE DE DADOS
# ----------------------------------------------------
def carregar_base_dados(caminho="base_militantes.json"):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def guardar_base_dados(base, caminho="base_militantes.json"):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(base, f, ensure_ascii=False, indent=4)

# ----------------------------------------------------
# LOCALIDADES (Luanda)
# ----------------------------------------------------
def carregar_localidades(caminho="localidades_luanda_v3.json"):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def obter_comunas_por_municipio(localidades, municipio):
    if isinstance(localidades, dict):
        return localidades.get(municipio, [])
    return []

# ----------------------------------------------------
# FUNÇÃO PARA GERAR Nº AUTOMÁTICO POR CAP
# ----------------------------------------------------
def gerar_numero_registo(base, cap):
    existentes = [m for m in base if m.get("cap") == cap]
    novo_numero = len(existentes) + 1
    return f"REG-{novo_numero:04d}"

# ----------------------------------------------------
# ADICIONAR, ATUALIZAR, REMOVER
# ----------------------------------------------------
def adicionar_militante(base, militante):
    base.append(militante)
    return base

def atualizar_militante_por_cap(base, cap, novos_dados):
    for m in base:
        if m.get("cap") == cap:
            m.update(novos_dados)
            return base
    return base

def remover_por_cap(base, cap):
    base = [m for m in base if m.get("cap") != cap]
    return base

# ----------------------------------------------------
# IMPORTAR / EXPORTAR
# ----------------------------------------------------
def importar_dados_excel(arquivo):
    df = pd.read_excel(arquivo)
    return df.to_dict(orient="records")

def importar_dados_texto(texto):
    df = pd.read_csv(io.StringIO(texto))
    return df.to_dict(orient="records")

def exportar_para_excel(base):
    df = pd.DataFrame(base)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Militantes")
        worksheet = writer.sheets["Militantes"]
        for idx, col in enumerate(df.columns):
            max_len = df[col].astype(str).map(len).max()
            worksheet.set_column(idx, idx, max_len + 5)
    buffer.seek(0)
    return buffer

# ----------------------------------------------------
# RECIBO — FPDF (PDF em memória)
# ----------------------------------------------------
class PDFRecibo(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "MPLA — SERVIR O POVO E FAZER ANGOLA CRESCER", ln=True, align="C")
        self.ln(5)

def gerar_recibo_pdf_bytes(militante):
    pdf = PDFRecibo()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for chave, valor in militante.items():
        pdf.cell(0, 10, f"{chave}: {valor}", ln=True)

    pdf_bytes = bytes(pdf.output(dest="S").encode("latin1"))
    return pdf_bytes
