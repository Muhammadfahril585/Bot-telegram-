from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import io

def buat_pdf_rekap_bulanan(teks: str) -> io.BytesIO:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 11)

    x_margin = 2.5 * cm
    y = height - 3 * cm
    baris = teks.split("\n")

    for line in baris:
        if y < 2.5 * cm:
            c.showPage()
            y = height - 3 * cm
            c.setFont("Helvetica", 11)
        c.drawString(x_margin, y, line)
        y -= 14  # spasi baris

    c.save()
    buffer.seek(0)
    return buffer
