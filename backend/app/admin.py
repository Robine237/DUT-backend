from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from app.models import Region, Department, Commune,BirthAct, User,BirthAct


class CustomUserAdmin(UserAdmin):
    """
    Configuration avancée du modèle User dans l'admin
    """

    # champs visibles dans la liste
    list_display = ("id", "username", "email", "role", "matricule", "is_staff")

    # filtres à droite
    list_filter = ("role", "is_staff", "is_superuser")

    # champs recherchables
    search_fields = ("username", "email", "matricule")

    # organisation des champs dans la page utilisateur
    fieldsets = UserAdmin.fieldsets + (
        ("Informations supplémentaires", {
            "fields": ("role", "matricule", "email_verified")
        }),
    )

    # champs lors de la création
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Informations supplémentaires", {
            "fields": ("role", "matricule", "email"),
        }),
    )

admin.site.register(User, CustomUserAdmin)    



@admin.register(BirthAct)
class BirthActAdmin(admin.ModelAdmin):
    """
    Admin des actes de naissance (simulation BUNEC)
    """

    list_display = (
        "act_number",
        "child_lastname",
        "child_firstname",
        "date_of_birth",
        "registration_place",
        "is_valid"
    )

    list_filter = (
        "child_gender",
        "registration_place",
        "is_valid"
    )

    search_fields = (
        "act_number",
        "child_lastname",
        "child_firstname"
    )

    ordering = ("-created_at",)

    readonly_fields = ("created_at",)

    fieldsets = (

        ("👶 Informations de l'enfant", {
            "fields": (
                "child_lastname",
                "child_firstname",
                "child_gender",
                "date_of_birth",
                "place_of_birth",
                "time_of_birth"
            )
        }),

        ("👨 Père", {
            "fields": (
                "father_lastname",
                "father_firstname",
                "father_profession",
                "father_nationality",
                "father_address"
            )
        }),

        ("👩 Mère", {
            "fields": (
                "mother_lastname",
                "mother_firstname",
                "mother_profession",
                "mother_nationality",
                "mother_address"
            )
        }),

        ("🏛️ Informations administratives", {
            "fields": (
                "act_number",
                "registration_date",
                "registration_place",
                "civil_officer"
            )
        }),

        ("⚙️ Statut", {
            "fields": (
                "is_valid",
                "created_at"
            )
        }),
    )


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    """
    Admin des régions
    """

    list_display = ( "name",)
    search_fields = ("name",)
    ordering = ("name",)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "region")
@admin.register(Commune)    
class CommuneAdmin(admin.ModelAdmin):
    list_display = ("id","name", "department", "get_region", "mayor_name")

    def get_region(self, obj):
        return obj.department.region

    get_region.short_description = "Region"