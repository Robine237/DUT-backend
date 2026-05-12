import qrcode
from io import BytesIO
from django.core.files.base import ContentFile


class QRService:

    @staticmethod
    def generate(certification):
        """
        Génère et attache un QR code à une certification
        """

        # 🔗 lien de vérification
        data = f"http://localhost:8000/api/verify/{certification.verification_code}"

        # 🧾 génération QR
        qr = qrcode.make(data)

        # 📦 buffer mémoire
        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        # 💾 sauvegarde dans le champ ImageField
        certification.qr_code.save(
            f"qr_{certification.id}.png",
            ContentFile(buffer.getvalue()),
            save=False
        )