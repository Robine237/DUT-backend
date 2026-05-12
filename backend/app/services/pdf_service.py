from reportlab.pdfgen import canvas
from io import BytesIO


class PDFService:
    """
    Génération PDF officiel certifié
    """

    @staticmethod
    def generate(certification, act, commune):

        buffer = BytesIO()
        p = canvas.Canvas(buffer)

        # 🧾 TITRE
        p.drawString(200, 800, "ACTE DE NAISSANCE CERTIFIÉ")

        # 👶 ACTE
        p.drawString(100, 760, f"Nom: {act.child_lastname}")
        p.drawString(100, 740, f"Prénom: {act.child_firstname}")
        p.drawString(100, 720, f"Date: {act.date_of_birth}")

        # 🏛️ MAIRIE
        p.drawString(100, 680, f"Mairie: {commune.name}")
        p.drawString(100, 660, f"Maire: {commune.mayor_name}")

        # 🧾 TIMBRE
        p.drawString(100, 620, f"Timbre: {certification.stamp_number}")

        # 🔳 QR CODE (image)
        if certification.qr_code:
            p.drawImage(certification.qr_code.path, 400, 600, width=100, height=100)

        # ✍️ SIGNATURE MAIRE
        if hasattr(commune, "signature") and commune.signature:
            p.drawImage(commune.signature.path, 100, 500, width=150, height=80)

        # 🔐 CODE
        p.drawString(100, 450, f"Code: {certification.verification_code}")

        p.showPage()
        p.save()

        buffer.seek(0)

        return buffer