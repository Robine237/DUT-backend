from django.core.mail import send_mail


class EmailService:
    """
    Gère tous les envois d'emails
    """

    @staticmethod
    def send_otp_email(email, otp):
        """
        Envoie un OTP par email
        """

        subject = "Code OTP - Plateforme Etat Civil"

        message = f"""
        Bonjour,

        Votre code OTP est : {otp}

        Ce code expire dans 5 minutes.

        Merci.
        """

        send_mail(
            subject,          # sujet
            message,          # contenu
            None,             # expéditeur (settings)
            [email],          # destinataire
            fail_silently=False
        )