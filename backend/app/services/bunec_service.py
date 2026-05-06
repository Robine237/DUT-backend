from app.models import BirthAct


class BunecService:
    """
    Simule la récupération des données citoyen via numéro d'acte
    """

    @staticmethod
    def get_birth_act_by_number(act_number):
        try:
            return BirthAct.objects.get(act_number=act_number)
        except BirthAct.DoesNotExist:
            return None