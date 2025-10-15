from fpdf import FPDF
import os

class PDFRecibo(FPDF):
    def header(self):
        # Cabeçalho com bandeira e emblema
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

def gerar_recibo_mpla(dados, output_path="recibo_mpla.pdf"):
    pdf = PDFRecibo()
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
