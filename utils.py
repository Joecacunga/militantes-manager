import pandas as pd
from io import BytesIO

def detectar_duplicados(df):
    """Deteta duplicados por Nome, Telefone ou Nº de CAP"""
    duplicados = df[df.duplicated(
        subset=["Primeiro Nome", "Último Nome", "Telefone", "Nº CAP"],
        keep=False
    )]
    return duplicados

def exportar_excel(df):
    """Exporta DataFrame para Excel em memória"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Militantes")
    processed_data = output.getvalue()
    return processed_data
