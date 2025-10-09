import pandas as pd
import json
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

BASE_DADOS_JSON = "base_militantes.json"

# ============================
# 1️⃣ Carregar Base de Dados
# ============================
def carregar_base_dados():
    if os.path.exists(BASE_DADOS_JSON):
        with open(BASE_DADOS_JSON, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return pd.DataFrame(data)
            except Exception:
                return pd.DataFrame(columns=[
                    "Primeiro Nome", "Último Nome", "Nº CAP", "Telefone", "Cartão",
                    "Província", "Município", "Comuna", "Bairro"
                ])
    else:
        return pd.DataFrame(columns=[
            "Primeiro Nome", "Último Nome", "Nº CAP", "Telefone", "Cartão",
            "Província", "Município", "Comuna", "Bairro"
        ])

# ============================
# 2️⃣ Guardar Base de Dados
# ============================
def guardar_base_dados(df, registro):
    if registro["Nº CAP"].strip() == "":
        return df

    if df.empty:
        df = pd.DataFrame([registro])
    else:
        duplicado = df[
            (df["Nº CAP"] == registro["Nº CAP"]) |
            ((df["Primeiro Nome"] == registro["Primeiro Nome"]) &
             (df["Último Nome"] == registro["Último Nome"]))
        ]
        if duplicado.empty:
            df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
        else:
            return df

    df.to_json(BASE_DADOS_JSON, orient="records", force_ascii=False, indent=4)
    return df

# ============================
# 3️⃣ Atualizar Registo
# ============================
def atualizar_registro(df, id_registro, novo_nome, novo_apelido):
    try:
        df.loc[id_registro, "Primeiro Nome"] = novo_nome
        df.loc[id_registro, "Último Nome"] = novo_apelido
        df.to_json(BASE_DADOS_JSON, orient="records", force_ascii=False, indent=4)
    except Exception:
        pass
    return df

# ============================
# 4️⃣ Remover Registo
# ============================
def remover_registro(df, id_registro):
    try:
        df = df.drop(id_registro)
        df.reset_index(drop=True, inplace=True)
        df.to_json(BASE_DADOS_JSON, orient="records", force_ascii=False, indent=4)
    except Exception:
        pass
    return df

# ============================
# 5️⃣ Importar Excel / CSV
# ============================
def importar_dados_excel(df, file):
    try:
        dados = pd.read_excel(file)
        df = pd.concat([df, dados], ignore_index=True)
        df.to_json(BASE_DADOS_JSON, orient="records", force_ascii=False, indent=4)
    except Exception:
        pass
    return df

# ============================
# 6️⃣ Importar por Colagem
# ============================
def importar_dados_texto(df, texto):
    linhas = [l.strip() for l in texto.splitlines() if l.strip()]
    adicionados = []
    for linha in linhas:
        partes = linha.split("|") if "|" in linha else linha.split("\t")
        if len(partes) >= 9:
            registro = {
                "Primeiro Nome": partes[0].strip(),
                "Último Nome": partes[1].strip(),
                "Nº CAP": partes[2].strip(),
                "Telefone": partes[3].strip(),
                "Cartão": partes[4].strip(),
                "Província": partes[5].strip(),
                "Município": partes[6].strip(),
                "Comuna": partes[7].strip(),
                "Bairro": partes[8].strip()
            }
            adicionados.append(registro)
    if adicionados:
        df = pd.concat([df, pd.DataFrame(adicionados)], ignore_index=True)
        df.to_json(BASE_DADOS_JSON, orient="records", force_ascii=False, indent=4)
    return df

# ============================
# 7️⃣ Exportar para Excel
# ============================
def exportar_para_excel(df):
    if df.empty:
        return
    output = BytesIO()
    df.to_excel(output, index=False)
    with open("Base_Militantes_Exportada.xlsx", "wb") as f:
        f.write(output.getvalue())

# ============================
# 8️⃣ Gerar Recibo PDF
# ============================
def gerar_recibo_pdf(militante):
    nome = militante["Primeiro Nome"] + " " + militante["Último Nome"]
    cap = militante["Nº CAP"]
    municipio = militante["Município"]
    comuna = militante["Comuna"]
    bairro = militante["Bairro"]

    recibo_nome = f"REC_{cap}.pdf"
    c = canvas.Canvas(recibo_nome, pagesize=A4)

    largura, altura = A4
    margem = 2 * cm
    y = altura - 2 * cm

    # Cabeçalho
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margem, y, "MPLA - Movimento Popular de Libertação de Angola")
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margem, y, "RECIBO OFICIAL DO MILITANTE")
    y -= 30

    c.setFont("Helvetica", 11)
    c.drawString(margem, y, f"Nome do Militante: {nome}")
    y -= 20
    c.drawString(margem, y, f"Nº CAP: {cap}")
    y -= 20
    c.drawString(margem, y, f"Município: {municipio}")
    y -= 20
    c.drawString(margem, y, f"Comuna: {comuna}")
    y -= 20
    c.drawString(margem, y, f"Bairro: {bairro}")
    y -= 40

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(margem, y, "Secretário do CAP / Responsável de Organização")
    y -= 30

    c.showPage()
    c.save()
