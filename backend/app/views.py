from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.http import FileResponse
import os

from app.services.citizen_service import CitizenService
from app.services.otp_service import OTPService
from app.services.email_service import EmailService
from app.services.jwt_service import JWTService
from app.services.auth_service import AuthService
from app.services.bunec_service import BunecService
from app.services.pricing_service import PricingService
from app.services.qr_service import QRService
from app.services.stamp_service import StampService

from app.serializers import (ProLoginSerializer, ProVerifySerializer,RegionSerializer, 
                             InitCitizenSerializer, OTPVerifySerializer, BirthActSerializer,
                             CommuneSerializer,DepartmentSerializer,CertificationSerializer,
                             PriceSerializer,PaymentSerializer,GenerateCertificateSerializer)

from app.models import BirthAct,Region,Department,Commune
from app.permissions import IsCitoyen
from app.permissions import IsBunec

User = get_user_model()

from app.services.pdf_service import PDFService
from app.models import Certification, BirthAct, Commune


#AUTH
class InitCitizenLoginView(generics.GenericAPIView):
    """
    Gestion connexion citoyen :
    - matricule = numéro d’acte de naissance
    - vérification via BUNEC (simulation)
    - 1ère fois → matricule + email
    - après → matricule seulement
    """

    serializer_class = InitCitizenSerializer

    def post(self, request):
        # validation des données
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        matricule = serializer.validated_data['matricule']
        email = serializer.validated_data.get('email')

        # 🔥 1. Vérifier si acte existe dans BUNEC (simulation)
        from app.services.bunec_service import BunecService

        birth_act = BunecService.get_birth_act_by_number(matricule)

        if not birth_act:
            return Response(
                {"error": "Aucun acte trouvé avec ce numéro"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 🔥 2. Récupérer ou créer utilisateur
        user, created = CitizenService.get_or_create_citizen(
            matricule=matricule,
            email=email
        )

        #  sécurité (cas rare mais important)
        if not user:
            return Response(
                {"error": "Erreur lors de la récupération du citoyen"},
                status=status.HTTP_400_BAD_REQUEST
            )

        #  CAS 1 : première connexion sans email
        if created and not email:
            return Response(
                {"error": "Email requis pour la première connexion"},
                status=status.HTTP_400_BAD_REQUEST
            )

        #  CAS 2 : utilisateur existe mais pas d'email
        if not user.email:
            return Response(
                {"error": "Aucun email associé à ce matricule"},
                status=status.HTTP_400_BAD_REQUEST
            )

        #  3. Génération OTP
        otp = OTPService.create_otp(user)

        #  4. Envoi email
        EmailService.send_otp_email(user.email, otp.code)

        return Response(
            {
                "message": "OTP envoyé avec succès",
                "matricule": user.matricule,

                # 🔥 BONUS (optionnel mais puissant pour ton front)
                "citoyen": {
                    "nom": birth_act.child_lastname,
                    "prenom": birth_act.child_firstname,
                    "date_naissance": birth_act.date_of_birth,
                    "lieu": birth_act.place_of_birth,
                }
            },
            status=status.HTTP_200_OK
        )


class VerifyOTPView(generics.GenericAPIView):
    """
    Vérification OTP + génération JWT
    """

    serializer_class = OTPVerifySerializer

    def post(self, request):
        # validation des données
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        # récupération utilisateur
        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            return Response(
                {"error": "Utilisateur introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )

        # vérification OTP
        valid = OTPService.verify_otp(user, code)

        if not valid:
            return Response(
                {"error": "OTP invalide ou expiré"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # marquer email comme vérifié
        user.email_verified = True
        user.save()

        #  génération JWT
        tokens = JWTService.generate_tokens(user)

        return Response(
            {
                "message": "Connexion réussie",
                "user": {
                    "id": user.id,
                    "matricule": user.matricule,
                    "email": user.email,
                    "role": user.role,
                },
                "tokens": tokens
            },
            status=status.HTTP_200_OK
        )

class ProLoginView(generics.GenericAPIView):
    """
    Login mairie / bunec avec mot de passe
    """

    serializer_class = ProLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # 🔐 authentification
        user = AuthService.authenticate_user(username, password)

        if not user:
            return Response(
                {"error": "Identifiants invalides"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # vérifier email
        if not user.email:
            return Response(
                {"error": "Email non configuré"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # génération OTP
        otp = OTPService.create_otp(user)

        # envoi OTP
        EmailService.send_otp_email(user.email, otp.code)

        return Response(
            {"message": "OTP envoyé"},
            status=status.HTTP_200_OK
        )
class ProVerifyOTPView(generics.GenericAPIView):
    """
    Vérification OTP pour mairie / bunec
    """

    serializer_class = ProVerifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        code = serializer.validated_data['code']

        try:
            user = User.objects.get(username=username)

        except User.DoesNotExist:
            return Response(
                {"error": "Utilisateur introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )

        # vérifier rôle
        if user.role not in ["MAIRIE", "BUNEC"]:
            return Response(
                {"error": "Accès non autorisé"},
                status=status.HTTP_403_FORBIDDEN
            )

        # vérification OTP
        valid = OTPService.verify_otp(user, code)

        if not valid:
            return Response(
                {"error": "OTP invalide ou expiré"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # génération JWT
        tokens = JWTService.generate_tokens(user)

        return Response(
            {
                "message": "Connexion réussie",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                },
                "tokens": tokens
            },
            status=status.HTTP_200_OK
        )    
    

#from rest_framework import generics
#from rest_framework.response import Response

#from app.permissions import IsCitoyen
#from rest_framework.permissions import IsAuthenticated


#class CitizenTestDashboardView(generics.GenericAPIView):
    """
    Dashboard citoyen
    """

    #permission_classes = [IsAuthenticated, IsCitoyen]

    ## return Response({
           # "message": "Bienvenue citoyen",
           # "user": request.user.username
      #  })    
    

#from app.permissions import IsMairie


#class MairieTestDashboardView(generics.GenericAPIView):
    """
    Route de test RBAC mairie
    """

    #permission_classes = [IsAuthenticated, IsMairie]

    #def get(self, request):
       # return Response({
            #"message": "OK mairie accès autorisé",
            #"user": request.user.username,
           # "role": request.user.role
        #})    



#CRUD D'ACTE
class BirthActCreateView(generics.CreateAPIView):
    """
    Création d'un acte de naissance (BUNEC uniquement)
    """
    serializer_class = BirthActSerializer
    permission_classes = [IsAuthenticated, IsBunec]

class CitizenBirthActListView(generics.ListAPIView):
    """
    Liste des actes du citoyen connecté
    """
    serializer_class = BirthActSerializer
    permission_classes = [IsAuthenticated, IsCitoyen]

    def get_queryset(self):
        return BirthAct.objects.filter(citizen=self.request.user)        
    
class BirthActDetailView(generics.RetrieveAPIView):
    """
    Détail d'un acte
    """
    serializer_class = BirthActSerializer
    permission_classes = [IsAuthenticated, IsCitoyen]

    def get_queryset(self):
        return BirthAct.objects.filter(citizen=self.request.user)
    
class BirthActUpdateView(generics.UpdateAPIView):
    """
    Mise à jour acte (BUNEC)
    """

    serializer_class = BirthActSerializer
    permission_classes = [IsAuthenticated, IsBunec]
    queryset = BirthAct.objects.all()

class BirthActDeleteView(generics.DestroyAPIView):
    """
    Suppression acte (BUNEC)
    """

    permission_classes = [IsAuthenticated, IsBunec]
    queryset = BirthAct.objects.all()    

#CRUD BD MAIRIE
class RegionCreateView(generics.CreateAPIView):
    """
    Création d'une région
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
class RegionListView(generics.ListAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

class DepartmentCreateView(generics.CreateAPIView):
    """
    Création d'un département lié à une région
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
class DepartmentByRegionView(generics.ListAPIView):
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        return Department.objects.filter(region_id=self.kwargs['region_id'])

class CommuneCreateView(generics.CreateAPIView):
    """
    Création d'une commune (mairie)
    """
    queryset = Commune.objects.all()
    serializer_class = CommuneSerializer
class CommuneByDepartmentView(generics.ListAPIView):
    serializer_class = CommuneSerializer

    def get_queryset(self):
        return Commune.objects.filter(department_id=self.kwargs['department_id'])
    


#validation d'un acte
class SelectCommuneView(generics.GenericAPIView):

    def post(self, request):
        act_number = request.data["act_number"]
        commune_id = request.data["commune_id"]

        act = BunecService.get_birth_act_by_number(act_number)

        if not act:
            return Response({"error": "Acte invalide"}, status=400)

        certification = Certification.objects.create(
            user=request.user,
            act_number=act_number,
            commune_id=commune_id
        )

        return Response({
            "certification_id": certification.id,
            "message": "Mairie sélectionnée"
        })

#PAIEMENT SIMULATION
class CalculatePriceView(generics.GenericAPIView):
    """
    Calcul du prix de la certification
    """

    serializer_class = PriceSerializer  # 🔥 OBLIGATOIRE

    def post(self, request, pk):
        cert = Certification.objects.get(id=pk)

        # calcul du prix
        cert.amount = PricingService.calculate()
        cert.save()

        # retour avec serializer
        serializer = self.get_serializer({"amount": cert.amount})

        return Response(serializer.data)
    
class PaymentView(generics.GenericAPIView):
    """
    Simulation du paiement
    """

    serializer_class = PaymentSerializer  # 🔥 obligatoire

    def post(self, request, pk):
        cert = Certification.objects.get(id=pk)

        # on marque comme payé
        cert.status = "PAID"
        cert.save()

        serializer = self.get_serializer({
            "message": "Paiement effectué"
        })

        return Response(serializer.data)
    

#GENERATION DU DOC CERTIF
class CreateCertificationView(generics.CreateAPIView):
    """
    Création d'une demande de certification
    """

    serializer_class = CertificationSerializer

    # 🔐 oblige utilisateur connecté
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        # 🔥 on récupère automatiquement le matricule
        act_number = user.matricule

        serializer.save(
            user=user,
            act_number=act_number
        )

class GenerateCertificateView(generics.GenericAPIView):
    """
    Génération du certificat final avec QR + signature + timbre
    """
    serializer_class = GenerateCertificateSerializer  # 🔥 FIX OBLIGATOIRE

    def post(self, request, pk):

        cert = Certification.objects.get(id=pk)

        # 🔐 sécurité paiement
        if cert.status != "PAID":
            return Response({"error": "Paiement requis"}, status=400)

        act = BunecService.get_birth_act_by_number(cert.act_number)
        commune = cert.commune

        # 🧾 génération timbre
        cert.stamp_number = StampService.generate()

        # 🔳 QR code
        QRService.generate(cert)

        # 📄 génération PDF
        pdf = PDFService.generate(cert, act, commune)

        # 💾 sauvegarde PDF
        cert.pdf_file.save("acte_certifie.pdf", pdf)

        cert.status = "CERTIFIED"
        cert.save()

        return Response({
            "message": "Certificat généré",
            "pdf_url": cert.pdf_file.url,
            "qr_code": cert.qr_code.url
        })
    

 #DOWNLOAD CERTIFICATION    
class DownloadCertificateView(generics.GenericAPIView):
    """
    Téléchargement sécurisé du PDF (1 seule fois)
    """

    def get(self, request, pk):

        cert = Certification.objects.get(id=pk)

        # 🔐 sécurité user
        #if cert.user != request.user:
            #return Response({"error": "Accès refusé"}, status=403)

        # ❌ déjà téléchargé
       # if cert.download_count >= 1:
       #     return Response(
        #        {"error": "Téléchargement déjà effectué"},
         #       status=400
          #  )

        # 📄 vérifier existence PDF
        if not cert.pdf_file:
            return Response(
                {"error": "PDF non disponible"},
                status=404
            )

        # 🔥 incrémenter compteur
        cert.download_count += 1
        cert.save()

        return FileResponse(
            cert.pdf_file.open(),
            as_attachment=True,
            filename="acte_certifie.pdf"
        )    
    
class VerifyCertificateView(generics.GenericAPIView):
    """
    Endpoint public de vérification de certificat via QR code
    """

    authentication_classes = []  # 🔥 PUBLIC
    permission_classes = []      # 🔥 PUBLIC

    def get(self, request, code):
        """
        Vérifie l'authenticité d'un certificat
        """

        try:
            # 🔍 rechercher certification par code unique
            cert = Certification.objects.get(verification_code=code)

        except Certification.DoesNotExist:
            return Response({
                "valid": False,
                "message": "Certificat invalide"
            }, status=404)

        # 🔐 réponse sécurisée (on ne donne pas tout)
        return Response({
            "valid": True,
            "message": "Certificat authentique",
            "data": {
                "act_number": cert.act_number,
                "status": cert.status,
                "commune": cert.commune.name,
                "date": cert.created_at
            }
        })    