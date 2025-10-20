# =====================================================
# MPLA Gestão de Militantes - Utils (v4.4)
# =====================================================
# Desenvolvido por: Joe Cacunga & GPT-5
# Lema: MPLA — Servir o Povo e Fazer Angola Crescer
# =====================================================

import json
import os
import pandas as pd
from datetime import datetime
from fpdf import FPDF

BASE_PATH = "base_militantes.json"

# =====================================================
# FUNÇÕES DE BASE DE DADOS
# =====================================================

def carregar_base_dados():
    """Carrega a base de dados JSON de militantes"""
    if os.path.exists(BASE_PATH):
        with open(BASE_PATH, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def guardar_base_dados(base):
    """Guarda a base de dados no ficheiro JSON"""
    with open(BASE_PATH, "w", encoding="utf-8") as f:
        json.dump(base, f, ensure_ascii=False, indent=4)


def proximo_numero_por_cap(base, cap):
    """Gera o próximo número de registo por CAP"""
    cap = cap.strip().upper()
    registros_cap = [m for m in base if m.get("cap") == cap]
    numero = len(registros_cap) + 1
    return f"REG-{cap}-{numero:04d}"


def adicionar_militante(base, militante):
    """Adiciona um novo militante à base"""
    reg_numero = proximo_numero_por_cap(base, militante["cap"])
    militante["registro_interno"] = reg_numero
    base.append(militante)
    guardar_base_dados(base)
    return base


def remover_registro(base, registro_interno):
    """Remove um militante pelo número de registo"""
    base = [m for m in base if m.get("registro_interno") != registro_interno]
    guardar_base_dados(base)
    return base


def atualizar_registro(base, registro_interno, novos_dados):
    """Atualiza os dados de um militante"""
    for i, m in enumerate(base):
        if m.get("registro_interno") == registro_interno:
            base[i].update(novos_dados)
            break
    guardar_base_dados(base)
    return base

# =====================================================
# FUNÇÕES DE IMPORTAÇÃO E EXPORTAÇÃO
# =====================================================

def importar_dados_excel(base, uploaded_file):
    """Importa militantes de um ficheiro Excel ou CSV"""
    ext = uploaded_file.name.split(".")[-1].lower()
    try:
        if ext == "xlsx":
            df = pd.read_excel(uploaded_file)
        elif ext == "csv":
            df = pd.read_csv(uploaded_file)
        else:
            return base

        for _, row in df.iterrows():
            militante = {
                "nome_proprio": str(row.get("Nome(s) Próprio(s)", "")).strip(),
                "ultimo_nome": str(row.get("Último Nome", "")).strip(),
                "cap": str(row.get("Nº CAP", "")).strip().upper(),
                "telefone": str(row.get("Telefone", "")),
                "cartao": str(row.get("Nº de Cartão", "")),
                "provincia": str(row.get("Província", "Luanda")),
                "municipio": str(row.get("Município", "")),
                "comuna": str(row.get("Comuna", "")),
                "bairro": str(row.get("Bairro", "")),
                "foto": "",
                "data_registo": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
            base = adicionar_militante(base, militante)
        return base

    except Exception as e:
        print("Erro na importação:", e)
        return base


def importar_dados_texto(base, texto):
    """Importa dados colados manualmente"""
    linhas = texto.strip().split("\n")
    for linha in linhas:
        partes = [p.strip() for p in linha.split("\t")]
        if len(partes) < 5:
            continue
        militante = {
            "nome_proprio": partes[0],
            "ultimo_nome": partes[1],
            "cap": partes[2].upper(),
            "telefone": partes[3],
            "cartao": partes[4] if len(partes) > 4 else "",
            "provincia": "Luanda",
            "municipio": partes[5] if len(partes) > 5 else "",
            "comuna": partes[6] if len(partes) > 6 else "",
            "bairro": partes[7] if len(partes) > 7 else "",
            "foto": "",
            "data_registo": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        base = adicionar_militante(base, militante)
    return base


def exportar_para_excel(base):
    """Exporta a base de militantes para ficheiro Excel"""
    if not base:
        return
    df = pd.DataFrame(base)
    caminho = "Base_Militantes_Exportada.xlsx"
    df.to_excel(caminho, index=False)
    return caminho

# =====================================================
# FUNÇÕES DE LOCALIDADES
# =====================================================

def carregar_localidades():
    """
    Carrega o ficheiro de localidades e converte para dicionário se necessário.
    """
    caminho = "localidades_luanda_v3.json"
    if not os.path.exists(caminho):
        return {}

    with open(caminho, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Se vier como lista, converte para dicionário
    if isinstance(data, list):
        novo = {}
        for item in data:
            if isinstance(item, dict):
                novo.update(item)
        data = novo

    if not isinstance(data, dict):
        data = {}

    return data


def obter_comunas_por_municipio(localidades, municipio):
    """Retorna comunas de um município específico"""
    if isinstance(localidades, dict):
        return localidades.get(municipio, [])
    else:
        return []

# =====================================================
# FUNÇÃO PARA GERAR RECIBO PDF
# =====================================================

def gerar_recibo_militante_pdf(militante):
    """Gera o Recibo Oficial do Militante em formato PDF"""
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "MPLA - SERVIR O POVO E FAZER ANGOLA CRESCER", 0, 1, "C")

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "RECIBO OFICIAL DE MILITANTE", 0, 1, "C")
    pdf.ln(10)

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Nome: {militante['nome_proprio']} {militante['ultimo_nome']}", 0, 1)
    pdf.cell(0, 8, f"Nº CAP: {militante['cap']}", 0, 1)
    pdf.cell(0, 8, f"Telefone: {militante['telefone']}", 0, 1)
    pdf.cell(0, 8, f"Nº Cartão: {militante['cartao']}", 0, 1)
    pdf.cell(0, 8, f"Província: {militante['provincia']}", 0, 1)
    pdf.cell(0, 8, f"Município: {militante['municipio']}", 0, 1)
    pdf.cell(0, 8, f"Comuna: {militante['comuna']}", 0, 1)
    pdf.cell(0, 8, f"Bairro: {militante['bairro']}", 0, 1)
    pdf.cell(0, 8, f"Nº de Registo Interno: {militante.get('registro_interno', '')}", 0, 1)
    pdf.ln(10)

    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 8, f"Emitido em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 1, "C")

    caminho = f"Recibo_{militante['cap']}_{militante['ultimo_nome']}.pdf"
    pdf.output(caminho, "F")
    return caminho
