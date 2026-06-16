from django.contrib import admin
from .models import Eleve, LienFamille

class LienFamilleInline(admin.TabularInline):
    model = LienFamille
    extra = 1
    fields = ("parent", "type_lien", "est_responsable_financier", "est_contact_principal")
    autocomplete_fields = ("parent",)  # Performance si >1000 users

@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    list_display = ("matricule_mepsa", "nom", "prenom", "classe_actuelle", "statut", "est_redoublant", "is_active")
    list_filter = ("statut", "genre", "est_redoublant", "ecole__region")
    search_fields = ("matricule_mepsa", "nom", "prenom")
    readonly_fields = ("created_at", "updated_at")
    inlines = [LienFamilleInline]
    fieldsets = (
        ("Identité", {"fields": ("matricule_mepsa", "nom", "prenom", "genre", "date_naissance", "lieu_naissance")}),
        ("Scolarité", {"fields": ("ecole", "classe_actuelle", "statut", "est_redoublant", "historique_redoublements")}),
        ("Santé (Préscolaire/Primaire)", {"fields": ("groupe_sanguin", "vaccinations_a_jour", "notes_medicales")}),
        ("Audit", {"fields": ("is_active", "created_at", "updated_at")}),
    )
    ordering = ("nom", "prenom")