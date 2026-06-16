from rest_framework import serializers
from .models import Ecole, Classe
import re

class EcoleSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les établissements scolaires"""
    class Meta:
        model = Ecole
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def validate_code_mepsa(self, value):
        """Valide et normalise le format MEPSA : REG-CEG-001"""
        value = value.strip().upper()
        pattern = r"^[A-Z]{2,4}-[A-Z]{2,5}-\d{2,4}$"
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Format invalide. Attendu : REGION-CYCLE-NUMERO (ex: BZV-CEG-042)"
            )
        return value

class ClasseSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les classes avec données liées optimisées"""
    ecole_nom = serializers.CharField(source="ecole.nom", read_only=True)
    niveau_display = serializers.CharField(source="get_niveau_display", read_only=True)

    class Meta:
        model = Classe
        fields = (
            "id", "nom", "niveau", "niveau_display", 
            "ecole", "ecole_nom", "capacite_max", 
            "is_active", "created_at", "updated_at"
        )
        read_only_fields = ("created_at", "updated_at")