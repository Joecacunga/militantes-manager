# utils_v4.py  (versão v4.3)
import os
import json
from datetime import datetime
import pandas as pd
from fpdf import FPDF

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

def contar_por_cap(base, cap):
    if not cap:
        return 0
    return sum(1 for m in base if (m.get("cap") or "").strip().upper() == cap.strip().upper())

def gerar_registro_interno_por_cap(base, cap):
    """
    Gera: REG-CAPXXX-0001 (4 dígitos sequenciais por CAP)
    """
    cap_str = (cap or "UNKNOWN").strip().upper()
    seq = contar_por_cap(base, cap_str) + 1
    return f"REG-{cap_str}-{seq:04d}"

def adicionar_militante(base, dados):
    """
    Adiciona militante depois de validar CAP único (se CAP vazio, permite)
    Retorna: base_atualizada, ok(bool), mensagem
    """
    cap = (dados.get("cap") or "").strip()
    # Se existir militante com mesmo CAP e mesmo nome, consideramos duplicado
    if cap:
        duplicado = any(
            (m.get("cap") or "").strip().upper() == cap.upper() and
            (m.get("primeiro_nome","").strip().upper() == (dados.get("primeiro_nome") or "").strip().upper()) and
            (m.get("ultimo_nome","").strip().upper() == (dados.get("ultimo_nome") or "").strip().upper())
            for m in base
        )
        if duplicado:
            return base, False, "Duplicado detectado: já existe um militante com esse Nome e Nº CAP."

    # Gerar registro interno por CAP
    registro_interno = gerar_registro_interno_por_cap(base, cap)
    dados["registro_interno"] = registro_interno
    dados["id"] = registro_interno  # usamos id = registro interno (único por CAP)
    dados["_created_at"] = datetime.now().isoformat()
    base.append(dados)
    guardar_base_dados(base)
    return base, True, "Militante adicionado com sucesso."

def remover_registro(base, id_registro):
    base = [m for m in base if m.get("id") != id_registro]
    guardar_base_dados(base)
    return base

def atualizar_registro(base, id_registro, novos_dados):
    for i, item in enumerate(base):
        if item.get("id") == id_registro:
            # atualiza só chaves presentes em novos_dados
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
                "provincia": partes[4].strip() if len(partes) > 4 else "",
                "municipio": partes[5].strip() if len(partes) > 5 else "",
                "comuna": partes[6].strip() if len(partes) > 6 else "",
                "bairro": partes[7].strip() if len(partes) > 7 else "",
            }
            registros.append(registro)
    return registros

def exportar_para_excel(base, caminho="Base_Militantes.xlsx"):
    df = pd.DataFrame(base)
    # ordena colunas de forma coerente (se existentes)
    cols_ordem = ["id","registro_interno","primeiro_nome","ultimo_nome","cap","telefone","provincia","municipio","comuna","bairro","data_nascimento","bi_numero","estado_civil","local_trabalho","habilitacoes","profissao","ocupacao","morada","nome_pai","nome_mae","nome_conjuge","profissao_conjuge","estuda","estuda_onde","linguas","estrangeiro","foto_path","_created_at"]
    cols = [c for c in cols_ordem if c in df.columns] + [c for c in df.columns if c not in cols_ordem]
    df = df[cols]
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
        # Banner (se existir) - tenta colocar banner completo se disponível
        try:
            # se houver uma imagem de banner (largura), desenha no topo
            if os.path.exists("Flag_of_MPLA.svg.png"):
                self.image("Flag_of_MPLA.svg.png", x=10, y=8, w=190)
                # coloca emblema pequeno à direita sobre o banner se existir
                if os.path.exists("EMBLEMA_MPLA (1).jpg"):
                    self.image("EMBLEMA_MPLA (1).jpg", x=170, y=10, w=20)
                self.ln(18)
            else:
                # fallback - pequeno cabeçalho com bandeira + emblema
                if os.path.exists("Flag_of_MPLA.svg.png"):
                    self.image("Flag_of_MPLA.svg.png", x=10, y=8, w=30)
                if os.path.exists("EMBLEMA_MPLA (1).jpg"):
                    self.image("EMBLEMA_MPLA (1).jpg", x=170, y=8, w=25)
                self.ln(14)
        except Exception:
            self.ln(10)

        # Centro: MPLA
        self.set_font("Arial", "B", 16)
        self.cell(0, 8, "MPLA", 0, 1, "C")
        # Linha divisória
        self.set_line_width(0.4)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-25)
        self.set_font("Arial", "I", 9)
        self.cell(0, 6, "MPLA — Servir o Povo e Fazer Angola Crescer", 0, 1, "C")
        self.set_font("Arial", "", 8)
        self.cell(0, 4, "Secretário do CAP / Responsável de Organização", 0, 0, "C")

def gerar_recibo_militante_pdf(dados, output_path=None):
    """
    Gera um recibo PDF com os principais campos e a foto associada.
    """
    if output_path is None:
        cap = (dados.get("cap") or "CAP").replace(" ", "_")
        registro = dados.get("registro_interno") or dados.get("id") or "REG"
        nome = (dados.get("primeiro_nome","") + "_" + dados.get("ultimo_nome","")).replace(" ", "_")
        output_path = f"Recibo_{registro}_{cap}_{nome}.pdf"

    pdf = PDFMilitante(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "", 11)

    # Foto (direita)
    foto = dados.get("foto_path", "foto_generica.jpg")
    if foto and os.path.exists(foto):
        try:
            pdf.image(foto, x=150, y=60, w=35, h=40)
        except Exception:
            pass

    # Campos principais (resumido no recibo)
    campos = [
        ("Registro", dados.get("registro_interno","")),
        ("Nome Completo", f"{dados.get('primeiro_nome','')} {dados.get('ultimo_nome','')}"),
        ("Nº CAP", dados.get("cap","")),
        ("Telefone", dados.get("telefone","")),
        ("Município", dados.get("municipio","")),
        ("Comuna", dados.get("comuna","")),
        ("Bairro", dados.get("bairro","")),
    ]

    pdf.ln(5)
    for label, valor in campos:
        pdf.set_font("Arial", "B", 10)
        pdf.cell(45, 7, f"{label}:", 0, 0)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 7, valor if valor else " ")
    pdf.ln(8)

    pdf.cell(0, 10, "_" * 40, 0, 1, "L")
    pdf.cell(0, 6, "Secretário do CAP / Responsável de Organização", 0, 1, "L")

    pdf.output(output_path)
    return output_path
