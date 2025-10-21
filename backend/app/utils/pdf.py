from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def build_pdf(title: str, lines: list[str]) -> bytes:
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50
    p.setFont("Helvetica-Bold", 16); p.drawString(50, y, title); y -= 30
    p.setFont("Helvetica", 11)
    for line in lines:
        if y < 50:
            p.showPage(); y = height - 50; p.setFont("Helvetica", 11)
        p.drawString(50, y, line[:1000]); y -= 18
    p.showPage(); p.save(); buffer.seek(0)
    return buffer.read()
