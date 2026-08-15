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

    # Champs de santé : réservés à la direction et aux parents de l'élève (CDC §7.2)
    MEDICAL_FIELDS = ("groupe_sanguin", "vaccinations_a_jour", "notes_medicales")

    class Meta:
        model = Eleve
        fields = "__all__"
        # `ecole` est déduite de l'utilisateur en vue : l'accepter du client
        # permettrait de rattacher/déplacer un élève vers un autre établissement.
        read_only_fields = ["created_at", "updated_at", "historique_redoublements", "ecole"]

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is None or user.is_superuser:
            return fields
        if user.role in ("ADMIN", "DIRECTEUR") or user.role == "PARENT":
            return fields
        for name in self.MEDICAL_FIELDS:
            fields.pop(name, None)
        return fields