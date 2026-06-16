from django.contrib import admin
from .models import SessionExamen, CandidatExamen, NoteExamen, ResultatFinal

class NoteExamenInline(admin.TabularInline):
	model = NoteExamen
	extra = 0
	fields = ("matiere", "coefficient", "note", "saisie_par")


class ResultatInline(admin.StackedInline):
	model = ResultatFinal
	extra = 0
	readonly_fields = ("moyenne_generale", "mention", "est_admis", "date_proclamation")


@admin.register(SessionExamen)
class SessionExamenAdmin(admin.ModelAdmin):
	list_display = ("annee_scolaire", "type_examen", "serie", "statut", "est_proclame", "date_debut")
	list_filter = ("type_examen", "statut", "est_proclame")
	search_fields = ("annee_scolaire",)
	date_hierarchy = "date_debut"


@admin.register(CandidatExamen)
class CandidatExamenAdmin(admin.ModelAdmin):
	list_display = ("numero_candidat", "session", "eleve", "centre_examen")
	list_filter = ("session__type_examen", "session__statut")
	search_fields = ("numero_candidat", "eleve__nom", "eleve__prenom")
	inlines = [NoteExamenInline, ResultatInline]
