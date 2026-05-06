from django.contrib.auth import authenticate


class AuthService:
    """
    Gestion authentification username/password
    """

    @staticmethod
    def authenticate_user(username, password):
        """
        Vérifie les identifiants utilisateur
        """

        user = authenticate(username=username, password=password)

        if not user:
            return None

        # autoriser uniquement mairie et bunec ici
        if user.role not in ["MAIRIE", "BUNEC"]:
            return None

        return user