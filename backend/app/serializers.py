from rest_framework import serializers
from app.models import BirthAct
from app.models import Region, Department, Commune


#AUTH
class InitCitizenSerializer(serializers.Serializer):
    """
    Serializer pour première connexion citoyen
    """

    matricule = serializers.CharField()
    email = serializers.EmailField(required=False)

class OTPVerifySerializer(serializers.Serializer):
    """
    Serializer pour vérifier OTPsss
    """
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

class ProLoginSerializer(serializers.Serializer):
    """
    Login mairie / bunec
    """
    username = serializers.CharField()
    password = serializers.CharField()

class ProVerifySerializer(serializers.Serializer):
    """
    Vérification OTP pro
    """
    username = serializers.CharField()
    code = serializers.CharField(max_length=6)



#BD ACTE
class BirthActSerializer(serializers.ModelSerializer):
    """
    Serializer pour les actes de naissance
    """

    class Meta:
        model = BirthAct
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

# MODELS MAIRIES
class RegionSerializer(serializers.ModelSerializer):
    """
    Serializer des régions
    """
    class Meta:
        model = Region
        fields = "__all__"

class DepartmentSerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)

    class Meta:
        model = Department
        fields = "__all__"

class CommuneSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = Commune
        fields = "__all__"       

from rest_framework import serializers
from app.models import Certification

#CERTIFICATION
class CertificationSerializer(serializers.ModelSerializer):
    """
    Serializer pour Certification
    """

    class Meta:
        model = Certification
        fields = "__all__"
        read_only_fields = [
            "user",
            "act_number",
            "status",
            "amount",
            "verification_code",
            "created_at",
            "qr_code",
            "pdf_file",
            "download_count",
            "stamp_number"
        ]
        

#PAIEMENT SIMULATION
class PriceSerializer(serializers.Serializer):
    """
    Serializer simple pour retour du prix
    """
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
        
class PaymentSerializer(serializers.Serializer):
    """
    Serializer pour le paiement (simulation)
    """

    message = serializers.CharField(read_only=True)

#GENARATE CERTIF
class GenerateCertificateSerializer(serializers.Serializer):
    """
    Serializer pour la génération du certificat
    """

    message = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)    