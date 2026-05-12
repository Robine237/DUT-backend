import random
from django.utils import timezone
from app.models import OTP


class OTPService:
    """
    Gestion des OTP
    """

    @staticmethod
    def generate_otp():
        """
        Génère un code OTP à 6 chiffres
        """
        return str(random.randint(100000, 999999))

    @staticmethod
    def create_otp(user):
        """
        Crée un OTP pour un utilisateur
        """

        code = OTPService.generate_otp()

        otp = OTP.objects.create(
            user=user,
            code=code,
            created_at=timezone.now()
        )

        return otp

    @staticmethod
    def verify_otp(user, code):
        """
        Vérifie OTP
        """

        try:
            otp = OTP.objects.filter(
                user=user,
                code=code,
                is_used=False
            ).latest('created_at')

        except OTP.DoesNotExist:
            return False

        # expiration 5 min
        if otp.is_expired():
            return False

        otp.is_used = True
        otp.save()

        return True