from django.urls import path
from app.views import (
    BirthActCreateView, CitizenBirthActListView,ProVerifyOTPView,
    BirthActDetailView,BirthActUpdateView,ProLoginView, 
    BirthActDeleteView,RegionListView,DepartmentByRegionView,CommuneByDepartmentView,  #CitizenTestDashboardView, MairieTestDashboardView
    RegionCreateView,DepartmentCreateView,CommuneCreateView,InitCitizenLoginView, VerifyOTPView,
    GenerateCertificateView,CreateCertificationView,PaymentView,CalculatePriceView,
    DownloadCertificateView,VerifyCertificateView,MairieDashboardView
)


urlpatterns = [
    path('auth/citoyen/connexion/', InitCitizenLoginView.as_view()),
    path('auth/citoyen/verify-otp/', VerifyOTPView.as_view()),
    path('auth/pro/loginpro/', ProLoginView.as_view()),
    path('auth/pro/verify_otpPRO/', ProVerifyOTPView.as_view()),
   # path('test/citoyen/', CitizenTestDashboardView.as_view()),
   # path('test/mairie/', MairieTestDashboardView.as_view()),

    path('birth-acts/create/', BirthActCreateView.as_view()),
    path('birth-acts/', CitizenBirthActListView.as_view()),
    path('birth-acts/<int:pk>/', BirthActDetailView.as_view()),
    path('birth-acts/<int:pk>/update/', BirthActUpdateView.as_view()),
    path('birth-acts/<int:pk>/delete/', BirthActDeleteView.as_view()), 

    path("regions/create/", RegionCreateView.as_view()),
    path("departments/create/", DepartmentCreateView.as_view()),
    path("communes/create/", CommuneCreateView.as_view()),
    path("regions/", RegionListView.as_view()),
    path("departments/<int:region_id>/", DepartmentByRegionView.as_view()),
    path("communes/<int:department_id>/", CommuneByDepartmentView.as_view()),  

    path("certifications/create/", CreateCertificationView.as_view()),
    path("certifications/<int:pk>/price/", CalculatePriceView.as_view()),
    path("certifications/<int:pk>/pay/", PaymentView.as_view()),
    path("certifications/<int:pk>/generate/", GenerateCertificateView.as_view()),
    path("certifications/<int:pk>/download/",DownloadCertificateView.as_view(),name="download-certificate"),

    path("verify/<uuid:code>/", VerifyCertificateView.as_view()),

    path("dashboard/mairie/", MairieDashboardView.as_view()),
]