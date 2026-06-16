from rest_framework import serializers
from .models import Eleve, LienFamille

class LienFamilleSerializer(serializers.ModelSerializer):
    parent_nom = serializers.CharField(source="parent.get_full_name", read_only=True)
    class Meta:
        model = LienFamille
        fields = ["id", "parent", "parent_nom", "type_lien", "est_responsable_financier", "est_contact_principal"]

class EleveListSerializer(serializers.ModelSerializer):
    """Sérialiseur léger pour la pagination 3G (CDC §3.2)"""
    classe_nom = serializers.CharField(source="classe_actuelle.nom", read_only=True)
    ecole_nom = serializers.CharField(source="ecole.nom", read_only=True)
    
    class Meta:
        model = Eleve
        fields = ["id", "matricule_mepsa", "nom", "prenom", "genre", "classe_nom", "ecole_nom", "statut", "est_redoublant"]

class EleveDetailSerializer(serializers.ModelSerializer):
    """Sérialiseur complet pour vue individuelle"""
    liens_familiaux = LienFamilleSerializer(many=True, read_only=True, source="lienfamille_set")
    
    class Meta:
        model = Eleve
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "historique_redoublements"]
        # notes_medicales présent mais protégé par permissions en vue