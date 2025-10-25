# utils_v4.py  (MPLA v4.6)
import os
import json
import base64
import io
import tempfile
from datetime import datetime
import pandas as pd
from fpdf import FPDF
from PIL import Image

BASE_JSON = "base_militantes.json"
LOCALIDADES_FILE = "localidades_luanda_v4.json"

# -------------------------
# Base de dados
# -------------------------
def carregar_base_dados():
    if os.path.exists(BASE_JSON):
        try:
            with open(BASE_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def guardar_base_dados(base):
    with open(BASE_JSON, "w", encoding="utf-8") as f:
        json.dump(base, f, ensure_ascii=False, indent=2)

# -------------------------
# Localidades
# -------------------------
def carregar_localidades():
    if not os.path.exists(LOCALIDADES_FILE):
        return {}
    with open(LOCALIDADES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        merged = {}
        for it in data:
            if isinstance(it, dict):
                merged.update(it)
        data = merged
    if not isinstance(data, dict):
        data = {}
    return data

def obter_comunas_por_municipio(localidades, municipio):
    if not isinstance(localidades, dict):
        return []
    return localidades.get(municipio, [])

# -------------------------
# Utilitários foto <-> base64
# -------------------------
def foto_bytes_para_b64(bytes_obj):
    return base64.b64encode(bytes_obj).decode("utf-8")

def foto_b64_para_bytes(b64str):
    return base64.b64decode(b64str.encode("utf-8"))

# -------------------------
# Sequência REG por CAP
# -------------------------
def contar_por_cap(base, cap):
    if not cap:
        return 0
    return sum(1 for m in base if (m.get("cap") or "").strip().upper() == cap.strip().upper())

def gerar_registro_interno_por_cap(base, cap):
    cap_str = (cap or "CAP").strip().upper()
    seq = contar_por_cap(base, cap_str) + 1
    return f"REG-{cap_str}-{seq:04d}"

# -------------------------
# Adicionar / editar / remover
# -------------------------
def adicionar_militante(base, dados):
    # valida CAP
    cap = (dados.get("cap") or "").strip().upper()
    if not cap:
        return base, False, "Nº CAP é obrigatório."
    # detecção simples de duplicado por CAP + nome completo
    nome_completo = f"{(dados.get('primeiro_nome') or '').strip()} {(dados.get('ultimo_nome') or '').strip()}".strip().upper()
    for m in base:
        if (m.get("cap") or "").strip().upper() == cap and \
           f\"{(m.get('primeiro_nome') or '').strip()} {(m.get('ultimo_nome') or '').strip()}\".strip().upper() == nome_completo:
            return base, False, "Duplicado detectado (mesmo Nome + CAP)."

    # gerar registro interno por CAP
    dados["registro_interno"] = gerar_registro_interno_por_cap(base, cap)
    dados["cap"] = cap
    # tratar fotografia: se bytes (UploadedFile) já transformados em 'foto_b64' no app, manter
    # timestamp
    dados["_created_at"] = datetime.now().isoformat()
    base.append(dados)
    guardar_base_dados(base)
    return base, True, "Militante adicionado com sucesso."

def atualizar_militante_por_cap(base, cap, novos_dados):
    cap = (cap or "").strip().upper()
    updated = False
    for i, m in enumerate(base):
        if (m.get("cap") or "").strip().upper() == cap:
            base[i].update(novos_dados)
            updated = True
    if updated:
        guardar_base_dados(base)
    return updated

def remover_por_cap(base, cap, nome=None):
    cap = (cap or "").strip().upper()
    if not cap:
        return base
    nova = []
    for m in base:
        if (m.get("cap") or "").strip().upper() == cap:
            if nome:
                full = f\"{(m.get('primeiro_nome') or '')} {(m.get('ultimo_nome') or '')}\".strip().upper()
                if full == nome.strip().upper():
                    continue
                else:
                    nova.append(m)
            else:
                continue
        else:
            nova.append(m)
    guardar_base_dados(nova)
    return nova

# -------------------------
# Import / Export
# -------------------------
def importar_dados_excel(base, uploaded_file):
    try:
        ext = uploaded_file.name.split(".")[-1].lower()
        if ext == "csv":
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        registros = df.to_dict(orient="records")
        added = 0
        for r in registros:
            militante = {
                "primeiro_nome": r.get("Nome(s) Próprio(s)") or r.get("primeiro_nome") or r.get("first_name") or "",
                "ultimo_nome": r.get("Último Nome") or r.get("ultimo_nome") or r.get("last_name") or "",
                "data_nascimento": r.get("Data de Nascimento") or "",
                "comuna_distrito": r.get("Comuna/Distrito Urbano") or r.get("comuna") or "",
                "municipio": r.get("Município") or r.get("municipio") or "",
                "provincia": r.get("Província") or "Luanda",
                "bi_numero": r.get("Portador do B.I Nº") or "",
                "arquivo_identificacao": r.get("Arquivo de identificação") or "",
                "estado_civil": r.get("Estado civil") or "",
                "local_trabalho": r.get("Local de trabalho") or "",
                "habilitacoes": r.get("Habilitações Literárias") or "",
                "profissao": r.get("Verdadeira profissão") or "",
                "ocupacao": r.get("Ocupação actual") or "",
                "morada": r.get("Morada") or "",
                "telefone": r.get("Telefone") or "",
                "nome_pai": r.get("Nome do pai") or "",
                "nome_mae": r.get("Nome da mãe") or "",
                "nome_conjuge": r.get("Nome do cônjuge") or "",
                "profissao_conjuge": r.get("Profissão do cônjuge") or "",
                "estuda": r.get("Estuda actualmente") or "",
                "estuda_onde": r.get("Se estuda onde") or "",
                "linguas": r.get("Línguas que fala") or "",
                "estrangeiro": r.get("Esteve no estrangeiro (Motivo)") or "",
                "cap": (r.get("Nº CAP") or r.get("cap") or "").strip().upper(),
                "foto_b64": ""
            }
            base, ok, _ = adicionar_militante(base, militante)
            if ok:
                added += 1
        return base, added
    except Exception as e:
        print("Erro importar excel:", e)
        return base, 0

def importar_dados_texto(base, texto):
    linhas = [l for l in texto.splitlines() if l.strip()]
    added = 0
    for linha in linhas:
        partes = linha.split("\t") if "\t" in linha else linha.split("|")
        if len(partes) >= 3:
            militante = {
                "primeiro_nome": partes[0].strip(),
                "ultimo_nome": partes[1].strip(),
                "cap": partes[2].strip().upper(),
                "telefone": partes[3].strip() if len(partes) > 3 else "",
                "provincia": "Luanda",
                "municipio": partes[4].strip() if len(partes) > 4 else "",
                "comuna": partes[5].strip() if len(partes) > 5 else "",
                "bairro": partes[6].strip() if len(partes) > 6 else "",
                "foto_b64": ""
            }
            base, ok, _ = adicionar_militante(base, militante)
            if ok:
                added += 1
    return base, added

def exportar_para_excel(base):
    if not base:
        return None
    df = pd.DataFrame(base)
    caminho = "Base_Militantes_Exportada.xlsx"
    df.to_excel(caminho, index=False)
    return caminho

# -------------------------
# GERAR RECIBO -> retorna bytes do PDF (não grava no servidor)
# -------------------------
class PDFRecibo(FPDF):
    def header(self):
        # pequena bandeira canto esquerdo
        try:
            if os.path.exists("Flag_of_MPLA.svg.png"):
                self.image("Flag_of_MPLA.svg.png", x=10, y=8, w=30)
            if os.path.exists("EMBLEMA_MPLA (1).jpg"):
                self.image("EMBLEMA_MPLA (1).jpg", x=170, y=8, w=20)
        except Exception:
            pass
        self.set_font("Arial", "B", 14)
        self.cell(0, 8, "MPLA", 0, 1, "C")
        self.set_line_width(0.4)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-25)
        self.set_font("Arial", "I", 9)
        self.cell(0, 6, "MPLA — Servir o Povo e Fazer Angola Crescer", 0, 1, "C")
        self.set_font("Arial", "", 8)
        self.cell(0, 4, "Secretário do CAP / Responsável de Organização", 0, 0, "C")

def gerar_recibo_pdf_bytes(militante):
    """
    Gera PDF em memória e devolve bytes (não grava ficheiro permanentemente).
    Usa 'foto_b64' se presente (decodifica, cria temporário e remove).
    """
    pdf = PDFRecibo()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "", 11)

    # incluir foto se existir: decodifica base64 para temp file
    foto_path_temp = None
    foto_b64 = militante.get("foto_b64") or militante.get("foto_path") or ""
    if foto_b64:
        try:
            # se já for um caminho de ficheiro no repo, usamos; senão interpretamos como base64
            if os.path.exists(foto_b64):
                foto_path_temp = foto_b64
            else:
                img_bytes = base64.b64decode(foto_b64.encode("utf-8"))
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                tmp.write(img_bytes)
                tmp.flush()
                tmp.close()
                foto_path_temp = tmp.name
        except Exception:
            foto_path_temp = None

    if foto_path_temp and os.path.exists(foto_path_temp):
        try:
            pdf.image(foto_path_temp, x=150, y=50, w=35, h=40)
        except Exception:
            pass

    # campos principais
    campos = [
        ("Registro interno", militante.get("registro_interno","")),
        ("Nome completo", f\"{militante.get('primeiro_nome','')} {militante.get('ultimo_nome','')}\"),
        ("Nº CAP", militante.get("cap","")),
        ("Telefone", militante.get("telefone","")),
        ("Município", militante.get("municipio","")),
        ("Comuna", militante.get("comuna","")),
        ("Bairro", militante.get("bairro",""))
    ]
    pdf.ln(5)
    for label, val in campos:
        pdf.set_font("Arial", "B", 10)
        pdf.cell(50, 7, f\"{label}:\", 0, 0)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 7, val if val else " ")

    pdf.ln(8)
    pdf.cell(0, 7, "______________________________", 0, 1, "L")
    pdf.cell(0, 6, "Secretário do CAP / Responsável de Organização", 0, 1, "L")

    # recolher resultado em memória
    pdf_bytes = pdf.output(dest="S").encode("latin-1")

    # remover temp image se criado
    if foto_path_temp and os.path.exists(foto_path_temp) and foto_path_temp.startswith(tempfile.gettempdir()):
        try:
            os.remove(foto_path_temp)
        except Exception:
            pass

    return pdf_bytes
