from django.contrib.auth.models import AbstractUser
from django.db import models

from django.conf import settings
import uuid


#MODELS AUTH
class User(AbstractUser):
    """
    Utilisateur principal du système
    """

    ROLE_CHOICES = [
        ("CITOYEN", "Citoyen"),
        ("MAIRIE", "Mairie"),
        ("BUNEC", "BUNEC"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # matricule unique pour citoyen
    matricule = models.CharField(max_length=100, unique=True, null=True, blank=True)

    # email obligatoire pour OTP
    email = models.EmailField(unique=True, null=True, blank=True)

    email_verified = models.BooleanField(default=False)

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    is_used = models.BooleanField(default=False)

    def is_expired(self):
        from django.utils import timezone
        return (timezone.now() - self.created_at).seconds > 300  # 5 min    
    

#MODELS BD ACTES
class BirthAct(models.Model):
    """
    Acte de naissance complet (format administratif Cameroun)
    """
    # ======================
    # IDENTITÉ ENFANT
    # ======================
    child_lastname = models.CharField(max_length=100)
    child_firstname = models.CharField(max_length=100)
    child_gender = models.CharField(max_length=10)

    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=255)
    time_of_birth = models.TimeField(null=True, blank=True)

    # ======================
    # PÈRE
    # ======================
    father_lastname = models.CharField(max_length=100)
    father_firstname = models.CharField(max_length=100)
    father_profession = models.CharField(max_length=100, null=True, blank=True)
    father_nationality = models.CharField(max_length=100, null=True, blank=True)
    father_address = models.CharField(max_length=255, null=True, blank=True)

    # ======================
    # MÈRE
    # ======================
    mother_lastname = models.CharField(max_length=100)
    mother_firstname = models.CharField(max_length=100)
    mother_profession = models.CharField(max_length=100, null=True, blank=True)
    mother_nationality = models.CharField(max_length=100, null=True, blank=True)
    mother_address = models.CharField(max_length=255, null=True, blank=True)

    # ======================
    # ADMINISTRATIF
    # ======================
    #liaison
    act_number = models.CharField(max_length=100, unique=True)
    registration_date = models.DateField()
    registration_place = models.CharField(max_length=255)
    civil_officer = models.CharField(max_length=255)
    # ======================
    # STATUT
    # ======================
    is_valid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


#MODELS BD MAIRIE
class Region(models.Model):
    name = models.CharField(max_length=100)

class Department(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

class Commune(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    # une commune = une mairie
    mayor_name = models.CharField(max_length=100)
    signature = models.ImageField(upload_to="signatures/", null=True, blank=True)


#MODELS SIGNATURE
class MayorSignature(models.Model):
    commune = models.OneToOneField(Commune, on_delete=models.CASCADE)

    signature_image = models.ImageField(upload_to="mayor_signatures/")
    uploaded_at = models.DateTimeField(auto_now_add=True)    


#MODEL DE CERTIFICATION
class Certification(models.Model):
    """
    Modèle représentant une demande de certification d'acte
    """

    STATUS = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("CERTIFIED", "Certified"),
    ]

    # utilisateur qui fait la demande
    user = models.ForeignKey("app.User", on_delete=models.CASCADE)

    # numéro d’acte (clé du système)
    act_number = models.CharField(max_length=100)

    # mairie choisie (commune)
    commune = models.ForeignKey("app.Commune", on_delete=models.CASCADE)

    # coût total
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # statut de la demande
    status = models.CharField(max_length=20, choices=STATUS, default="PENDING")

    # code unique pour vérifier le document
    verification_code = models.UUIDField(default=uuid.uuid4, editable=False)

    # fichier PDF généré
    pdf_file = models.FileField(upload_to="certificates/", null=True, blank=True)

    # QR code
    qr_code = models.ImageField(upload_to="qr/", null=True, blank=True)

    download_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    stamp_number = models.CharField(max_length=100, null=True, blank=True)