from django.contrib.auth import get_user_model

User = get_user_model()


class CitizenService:
    """
    Logique métier des citoyens
    """

    @staticmethod
    def get_or_create_citizen(matricule, email=None):
        """
        Récupère ou crée un citoyen
        """

        user = User.objects.filter(matricule=matricule).first()

        if user:
            return user, False

        user = User.objects.create(
            username=matricule,
            matricule=matricule,
            email=email,
            role="CITOYEN"
        )

        return user, True