from rest_framework import serializers
from .models import SessionExamen, NoteExamen, ResultatFinal, CandidatExamen

class NoteExamenWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteExamen
        fields = ["candidat", "matiere", "coefficient", "note"]

    def validate_note(self, value):
        from decimal import Decimal
        if not (Decimal(0) <= value <= Decimal(20)):
            raise serializers.ValidationError("Note comprise entre 0 et 20.")
        return value

    def validate_coefficient(self, value):
        from decimal import Decimal
        if value <= 0:
            raise serializers.ValidationError("Le coefficient doit être > 0.")
        return value


class ResultatFinalSerializer(serializers.ModelSerializer):
    candidat_numero = serializers.CharField(source="candidat.numero_candidat", read_only=True)
    class Meta:
        model = ResultatFinal
        fields = ["candidat_numero", "moyenne_generale", "mention", "est_admis", "date_proclamation"]


class SessionExamenSerializer(serializers.ModelSerializer):
    total_candidats = serializers.SerializerMethodField()
    class Meta:
        model = SessionExamen
        fields = "__all__"
        read_only_fields = ["est_proclame", "created_at"]

    def get_total_candidats(self, obj):
        return obj.candidats.count()
