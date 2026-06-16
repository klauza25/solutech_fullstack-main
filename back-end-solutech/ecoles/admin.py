from django.contrib import admin
from .models import Ecole, SchoolType, EducationLevel, Classe

@admin.register(Ecole)
class EcoleAdmin(admin.ModelAdmin):
    list_display = ("nom", "code_mepsa", "type", "region", "is_active", "created_at")
    list_filter = ("type", "region", "is_active")
    search_fields = ("nom", "code_mepsa", "region")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Identification", {"fields": ("nom", "code_mepsa", "type", "cycles")}),
        ("Localisation", {"fields": ("region", "district", "adresse", "telephone", "email")}),
        ("État & Audit", {"fields": ("is_active", "date_ouverture", "created_at", "updated_at")}),
    )
    ordering = ("region", "nom")
    


class ClasseInline(admin.TabularInline):
    model = Classe
    extra = 1
    fields = ("nom", "niveau", "capacite_max", "is_active")
    ordering = ("niveau", "nom")



@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ("nom", "niveau", "ecole", "capacite_max", "is_active")
    list_filter = ("niveau", "ecole__region", "is_active")
    search_fields = ("nom", "ecole__nom")
    list_select_related = ("ecole",)  # ⚡ Optimise les requêtes DB
    ordering = ("ecole__nom", "niveau")