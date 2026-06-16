from django.contrib import admin
from .models import Matiere, Evaluation, Presence

@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ("code", "nom", "coefficient_defaut", "est_obligatoire")
    search_fields = ("nom", "code")

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ("eleve", "matiere", "trimestre", "type_eval", "note_sur_20", "coefficient", "est_validee")
    list_filter = ("trimestre", "type_eval", "est_validee", "matiere")
    search_fields = ("eleve__nom", "eleve__prenom")
    date_hierarchy = "date_eval"
    readonly_fields = ("created_at", "updated_at")

@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    list_display = ("eleve", "date", "trimestre", "statut", "recorded_by")
    list_filter = ("statut", "trimestre")
    date_hierarchy = "date"
    search_fields = ("eleve__nom", "eleve__prenom")
