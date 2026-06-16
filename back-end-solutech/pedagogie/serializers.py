from rest_framework import serializers
from decimal import Decimal
from .models import Evaluation, Presence

class EvaluationCreateSerializer(serializers.ModelSerializer):
    """Saisie stricte des notes (conforme MEPSA §2.1)"""
    class Meta:
        model = Evaluation
        fields = ["eleve", "matiere", "classe", "trimestre", "type_eval", "coefficient", "note_sur_20", "date_eval"]
        # est_validee absent → défaut False

    def validate_note_sur_20(self, value):
        if not (Decimal(0) <= value <= Decimal(20)):
            raise serializers.ValidationError("La note doit être comprise entre 0 et 20.")
        return value

class EvaluationReadSerializer(serializers.ModelSerializer):
    """Lecture optimisée avec moyenne calculée à la volée"""
    eleve_info = serializers.StringRelatedField(source="eleve", read_only=True)
    matiere_nom = serializers.CharField(source="matiere.nom", read_only=True)
    moyenne_trimestrielle = serializers.SerializerMethodField()

    class Meta:
        model = Evaluation
        fields = [
            "id", "eleve", "eleve_info", "matiere", "matiere_nom", 
            "trimestre", "type_eval", "coefficient", "note_sur_20", 
            "moyenne_trimestrielle", "date_eval", "est_validee"
        ]

    def get_moyenne_trimestrielle(self, obj):
        """Calcule la moyenne pondérée de l'élève pour cette matière & trimestre"""
        evals = Evaluation.objects.filter(
            eleve=obj.eleve, matiere=obj.matiere, trimestre=obj.trimestre
        )
        total_coef = sum(e.coefficient for e in evals)
        if total_coef == 0:
            return Decimal(0)
        return round(
            sum(e.note_sur_20 * e.coefficient for e in evals) / total_coef,
            2
        )


class PresenceSerializer(serializers.ModelSerializer):
    eleve_info = serializers.StringRelatedField(source="eleve", read_only=True)
    classe_nom = serializers.CharField(source="classe.nom", read_only=True)

    class Meta:
        model = Presence
        fields = ["id", "eleve", "eleve_info", "classe", "classe_nom", "date", "trimestre", "statut", "justification", "recorded_by", "created_at"]
        read_only_fields = ["recorded_by", "created_at"]
