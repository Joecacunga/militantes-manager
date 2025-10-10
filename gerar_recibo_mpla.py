from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
import os

def gerar_recibo_mpla(militante):
    nome = f"{militante['Primeiro Nome']} {militante['Último Nome']}"
    cap = militante["Nº CAP"]
    municipio = militante["Município"]
    comuna = militante["Comuna"]
    bairro = militante["Bairro"]

    # Nome do ficheiro PDF
    nome_pdf = f"Recibo_{cap}.pdf"
    c = canvas.Canvas(nome_pdf, pagesize=A4)

    largura, altura = A4
    margem = 2 * cm
    y = altura - 2 * cm

    # Cabeçalho com bandeira à esquerda e emblema à direita
    try:
        bandeira = ImageReader("Flag_of_MPLA.svg.png")
        c.drawImage(bandeira, margem, y - 40, width=100, height=50)
    except:
        pass

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(largura / 2, y - 20, "MPLA")
    c.setFont("Helvetica", 10)
    c.drawCentredString(largura / 2, y - 35, "Movimento Popular de Libertação de Angola")

    try:
        emblema = ImageReader("EMBLEMA_MPLA (1).jpg")
        c.drawImage(emblema, largura - 4 * cm, y - 40, width=80, height=50)
    except:
        pass

    y -= 80
    c.setLineWidth(1)
    c.line(margem, y, largura - margem, y)
    y -= 20

    # Título
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(largura / 2, y, "RECIBO OFICIAL DO MILITANTE")
    y -= 30

    # Foto
    try:
        foto = ImageReader("foto_generica.jpg")
        c.drawImage(foto, margem, y - 80, width=90, height=90)
    except:
        pass

    # Dados principais
    x_texto = margem + 100
    c.setFont("Helvetica", 11)
    c.drawString(x_texto, y, f"Nome do Militante: {nome}")
    y -= 20
    c.drawString(x_texto, y, f"Nº CAP: {cap}")
    y -= 20
    c.drawString(x_texto, y, f"Município: {municipio}")
    y -= 20
    c.drawString(x_texto, y, f"Comuna: {comuna}")
    y -= 20
    c.drawString(x_texto, y, f"Bairro: {bairro}")
    y -= 40

    # Rodapé
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(margem, y, "Secretário do CAP / Responsável de Organização")
    y -= 40
    c.drawCentredString(largura / 2, y, "Servir o Povo e Fazer Angola Crescer")
    y -= 20
    c.line(margem, y, largura - margem, y)

    c.showPage()
    c.save()

    if os.path.exists(nome_pdf):
        print(f"✅ Recibo gerado com sucesso: {nome_pdf}")
    else:
        print("⚠️ Erro ao gerar o recibo.")
