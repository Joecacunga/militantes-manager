# utils_v4.py
import json
import os
import pandas as pd
from fpdf import FPDF
from datetime import datetime

BASE_ARQUIVO = "base_dados.json"
LOCALIDADES_ARQUIVO = "localidades_luanda_v3.json"

# ----------------------------
# Base de dados (lista de dicts)
# ----------------------------
def carregar_base_dados(caminho=BASE_ARQUIVO):
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def guardar_base_dados(base, caminho=BASE_ARQUIVO):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(base, f, ensure_ascii=False, indent=4)

def gerar_novo_id(base):
    return f"{len(base) + 1:02d}"

def adicionar_militante(base, dados):
    # se já existir CAP igual, não adicionar
    cap = dados.get("cap","").strip()
    if cap:
        exists = any(m.get("cap","").strip().upper() == cap.upper() for m in base)
        if exists:
            return base, False, "Já existe um militante com esse Nº CAP."
    novo_id = gerar_novo_id(base)
    dados["id"] = novo_id
    # timestamp
    dados["_created_at"] = datetime.now().isoformat()
    base.append(dados)
    guardar_base_dados(base)
    return base, True, "Adicionado com sucesso."

def remover_registro(base, id_registro):
    base = [m for m in base if m.get("id") != id_registro]
    guardar_base_dados(base)
    return base

def atualizar_registro(base, id_registro, novos_dados):
    for i, item in enumerate(base):
        if item.get("id") == id_registro:
            # atualiza só as chaves presentes em novos_dados
            base[i].update(novos_dados)
            guardar_base_dados(base)
            return True
    return False

# ----------------------------
# Import / Export
# ----------------------------
def importar_dados_excel(file_obj):
    try:
        df = pd.read_excel(file_obj)
        registros = df.to_dict(orient="records")
        # Mapeamento livre — o app tentará preencher campos com nomes conhecidos
        return registros
    except Exception:
        return []

def importar_dados_texto(texto):
    linhas = [l for l in texto.splitlines() if l.strip()]
    registros = []
    for linha in linhas:
        partes = linha.split("\t") if "\t" in linha else linha.split("|")
        if len(partes) >= 3:
            registro = {
                "primeiro_nome": partes[0].strip() if len(partes) > 0 else "",
                "ultimo_nome": partes[1].strip() if len(partes) > 1 else "",
                "cap": partes[2].strip() if len(partes) > 2 else "",
                "telefone": partes[3].strip() if len(partes) > 3 else "",
                "cartao": partes[4].strip() if len(partes) > 4 else "",
                "provincia": partes[5].strip() if len(partes) > 5 else "",
                "municipio": partes[6].strip() if len(partes) > 6 else "",
                "comuna": partes[7].strip() if len(partes) > 7 else "",
                "bairro": partes[8].strip() if len(partes) > 8 else "",
            }
            registros.append(registro)
    return registros

def exportar_para_excel(base, caminho="Base_Militantes.xlsx"):
    df = pd.DataFrame(base)
    df.to_excel(caminho, index=False)
    return caminho

# ----------------------------
# Localidades
# ----------------------------
def carregar_localidades(caminho=LOCALIDADES_ARQUIVO):
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}

def obter_comunas_por_municipio(municipio, localidades):
    return localidades.get(municipio, [])

# ----------------------------
# PDF - Recibo e Formulário Individual
# ----------------------------
class PDFMilitante(FPDF):
    def header(self):
        # Bandeira esquerda, emblema direita
        try:
            if os.path.exists("Flag_of_MPLA.svg.png"):
                self.image("Flag_of_MPLA.svg.png", x=10, y=8, w=30)
        except:
            pass
        try:
            if os.path.exists("EMBLEMA_MPLA (1).jpg"):
                self.image("EMBLEMA_MPLA (1).jpg", x=170, y=8, w=25)
        except:
            pass
        self.set_font("Arial", "B", 14)
        self.cell(0, 7, "MPLA", 0, 1, "C")
        self.set_font("Arial", "", 10)
        self.cell(0, 6, "Departamento de Organização e Mobilização – Comité Central", 0, 1, "C")
        self.ln(4)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-20)
        self.set_font("Arial", "I", 9)
        self.cell(0, 6, "Servir o Povo e Fazer Angola Crescer", 0, 1, "C")
        self.set_font("Arial", "", 8)
        self.cell(0, 4, "Secretário do CAP / Responsável de Organização", 0, 0, "C")

def gerar_recibo_militante_pdf(dados, output_path=None):
    if output_path is None:
        cap = dados.get("cap", "CAP")
        nome = (dados.get("primeiro_nome","") + "_" + dados.get("ultimo_nome","")).replace(" ", "_")
        output_path = f"Recibo_{cap}_{nome}.pdf"

    pdf = PDFMilitante(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "", 11)

    # foto
    foto = dados.get("foto_path", "foto_generica.jpg")
    if foto and os.path.exists(foto):
        try:
            pdf.image(foto, x=150, y=45, w=35, h=40)
        except:
            pass

    # campos principais (resumido no recibo)
    campos = [
        ("Nome Completo", f"{dados.get('primeiro_nome','')} {dados.get('ultimo_nome','')}"),
        ("Nº CAP", dados.get("cap", "")),
        ("Telefone", dados.get("telefone", "")),
        ("Cartão de Eleitor", dados.get("cartao", "")),
        ("Município", dados.get("municipio", "")),
        ("Comuna", dados.get("comuna", "")),
        ("Bairro", dados.get("bairro", "")),
    ]

    pdf.ln(10)
    for label, valor in campos:
        pdf.set_font("Arial", "B", 10)
        pdf.cell(50, 7, f"{label}:", 0, 0)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 7, valor if valor else " ")
    pdf.ln(10)
    pdf.cell(0, 8, "_____________________________", 0, 1, "L")
    pdf.cell(0, 6, "Secretário do CAP / Responsável de Organização", 0, 1, "L")

    pdf.output(output_path)
    return output_path
