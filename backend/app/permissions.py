from rest_framework.permissions import BasePermission


class IsAuthenticatedAndRole(BasePermission):
    """
    Classe de base pour vérifier rôle utilisateur
    """

    allowed_roles = []  # sera redéfini dans les classes enfants

    def has_permission(self, request, view):
        # vérifier utilisateur connecté
        if not request.user or not request.user.is_authenticated:
            return False

        # vérifier rôle
        return request.user.role in self.allowed_roles

class IsCitoyen(IsAuthenticatedAndRole):
    """
    Accès uniquement citoyen
    """

    allowed_roles = ["CITOYEN"]        

class IsMairie(IsAuthenticatedAndRole):
    """
    Accès uniquement mairie
    """

    allowed_roles = ["MAIRIE"]    

class IsBunec(IsAuthenticatedAndRole):
    """
    Accès uniquement BUNEC
    """

    allowed_roles = ["BUNEC"]    

class IsMairieOrBunec(IsAuthenticatedAndRole):
    """
    Accès mairie ou bunec
    """

    allowed_roles = ["MAIRIE", "BUNEC"]    