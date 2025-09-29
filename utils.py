import pandas as pd
from io import BytesIO
import json
import os

# Caminho do ficheiro JSON que vai guardar as listas
LISTS_FILE = "listas_localizacao.json"

# -----------------------------------------
# 🔹 Função para detetar duplicados
# -----------------------------------------
def detectar_duplicados(df):
    """Deteta duplicados por Nome, Telefone ou Nº de CAP"""
    duplicados = df[df.duplicated(
        subset=["Primeiro Nome", "Último Nome", "Telefone", "Nº CAP"],
        keep=False
    )]
    return duplicados


# -----------------------------------------
# 🔹 Função para exportar Excel
# -----------------------------------------
def exportar_excel(df):
    """Exporta DataFrame para Excel em memória"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Militantes")
    processed_data = output.getvalue()
    return processed_data


# -----------------------------------------
# 🔹 Funções de gestão das listas (JSON)
# -----------------------------------------
def carregar_listas():
    """Carrega listas de Províncias, Municípios e Comunas do ficheiro JSON"""
    if os.path.exists(LISTS_FILE):
        try:
            with open(LISTS_FILE, "r", encoding="utf-8") as f:
                listas = json.load(f)
        except Exception:
            listas = gerar_listas_padrao()
    else:
        listas = gerar_listas_padrao()
    return listas


def guardar_listas(listas):
    """Guarda as listas personalizadas no ficheiro JSON"""
    try:
        with open(LISTS_FILE, "w", encoding="utf-8") as f:
            json.dump(listas, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Erro ao guardar listas: {e}")
        return False


def gerar_listas_padrao():
    """Gera listas padrão de Províncias, Municípios e Comunas"""
    return {
        "provincias": ["Luanda", "Benguela", "Huambo", "Huíla", "Cuanza Sul", "Outra..."],
        "municipios": ["Cazenga", "Viana", "Belas", "Lubango", "Lobito", "Outro..."],
        "comunas": ["Comuna 1", "Comuna 2", "Comuna 3", "Outra..."]
    }
