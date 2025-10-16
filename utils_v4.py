import json
import pandas as pd
import os
from fpdf import FPDF

# =====================================================
# 🔹 Funções de Base de Dados
# =====================================================

def carregar_base_dados(caminho="base_dados.json"):
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_base_dados(base, caminho="base_dados.json"):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(base, f, indent=4, ensure_ascii=False)

def adicionar_militante(base, dados):
    novo_id = f"{len(base) + 1:02d}"  # Começa com 01
    dados["id"] = novo_id
    base.append(dados)
    guardar_base_dados(base)
    return base

def remover_registro(base, id_registro):
    base = [m for m in base if m.get("id") != id_registro]
    guardar_base_dados(base)
    return base

def atualizar_registro(base, id_registro, novos_dados):
    for i, item in enumerate(base):
        if item.get("id") == id_registro:
            base[i].update(novos_dados)
            guardar_base_dados(base)
            return True
    return False

# =====================================================
# 🔹 Importação / Exportação
# =====================================================

def importar_dados_excel(arquivo_excel):
    try:
        df = pd.read_excel(arquivo_excel)
        return df.to_dict(orient="records")
    except Exception:
        return []

def importar_dados_texto(texto):
    linhas = texto.strip().split("\n")
    registros = []
    for linha in linhas:
        partes = [p.strip() for p in linha.split("\t")]
        if len(partes) >= 8:
            registro = {
                "primeiro_nome": partes[0],
                "ultimo_nome": partes[1],
                "cap": partes[2],
                "telefone": partes[3],
                "cartao": partes[4],
                "provincia": partes[5],
                "municipio": partes[6],
                "comuna": partes[7],
                "bairro": partes[8] if len(partes) > 8 else "",
            }
            registros.append(registro)
    return registros

def exportar_para_excel(base, caminho="Base_Militantes.xlsx"):
    df = pd.DataFrame(base)
    df.to_excel(caminho, index=False)
    return caminho

# =====================================================
# 🔹 Estrutura de Localidades
# =====================================================

def carregar_localidades():
    caminho = "localidades_luanda_v3.json"
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def obter_comunas_por_municipio(municipio, localidades):
    """Retorna a lista de comunas de um município específico."""
    if municipio in localidades:
        return localidades[municipio]
    else:
        return []

# =====================================================
# 🔹 Geração de PDF (Recibo Oficial)
# =====================================================

class PDFMilitante(FPDF):
    def header(self):
        try:
            self.image("Flag_of_MPLA.svg.png", 10, 8, 25)
            self.image("EMBLEMA_MPLA (1).jpg", 170, 8, 25)
        except:
            pass

        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "MOVIMENTO POPULAR DE LIBERTAÇÃO DE ANGOLA (MPLA)", 0, 1, "C")
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "RECIBO OFICIAL DO MILITANTE", 0, 1, "C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 9)
        self.cell(0, 10, "Servir o Povo e Fazer Angola Crescer", 0, 0, "C")

def gerar_recibo_militante_pdf(dados, output_path="recibo_militante.pdf"):
    pdf = PDFMilitante()
    pdf.add_page()
    pdf.set_font("Arial", "", 11)

    foto_path = "foto_generica.jpg"
    if os.path.exists(foto_path):
        pdf.image(foto_path, 160, 45, 30, 35)

    campos = [
        ("Nome Completo", f"{dados.get('primeiro_nome', '')} {dados.get('ultimo_nome', '')}"),
        ("Nº CAP", dados.get("cap", "")),
        ("Telefone", dados.get("telefone", "")),
        ("Cartão de Eleitor", dados.get("cartao", "")),
        ("Província", dados.get("provincia", "")),
        ("Município", dados.get("municipio", "")),
        ("Comuna", dados.get("comuna", "")),
        ("Bairro", dados.get("bairro", "")),
    ]

    for campo, valor in campos:
        pdf.cell(50, 8, f"{campo}:", 0, 0)
        pdf.cell(0, 8, valor, 0, 1)

    pdf.ln(10)
    pdf.cell(0, 8, "_____________________________", 0, 1, "L")
    pdf.cell(0, 8, "Secretário do CAP / Responsável de Organização", 0, 1, "L")

    pdf.output(output_path)
    return output_path
