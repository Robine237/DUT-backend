import uuid


class StampService:
    """
    Génère un numéro de timbre (simulation)
    """

    @staticmethod
    def generate():
        return f"STAMP-{uuid.uuid4().hex[:10].upper()}"