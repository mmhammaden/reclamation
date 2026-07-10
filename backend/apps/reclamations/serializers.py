from rest_framework import serializers
from django.utils import timezone
from .models import Reclamation, PieceJointe, HistoriqueStatut, StatutReclamation
from apps.notes.models import NoteElementaire


class PieceJointeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PieceJointe
        fields = ('id', 'fichier', 'nom_fichier', 'taille', 'date_ajout')
        read_only_fields = ('id', 'nom_fichier', 'taille', 'date_ajout')

    def validate_fichier(self, value):
        """
        Validate file type and size server-side.
        Allowed: PDF, PNG, JPG, JPEG (max 10MB).
        """
        import os
        ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg'}
        MAX_SIZE = 10 * 1024 * 1024  # 10MB

        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f"Format de fichier non autorisé: {ext}. "
                f"Formats acceptés: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        if value.size > MAX_SIZE:
            raise serializers.ValidationError(
                f"Fichier trop volumineux ({value.size / 1024 / 1024:.1f}MB). "
                f"Taille maximale: 10MB."
            )

        return value


class HistoriqueStatutSerializer(serializers.ModelSerializer):
    modifie_par_nom = serializers.SerializerMethodField()

    class Meta:
        model = HistoriqueStatut
        fields = ('id', 'statut_precedent', 'nouveau_statut', 'commentaire',
                  'modifie_par', 'modifie_par_nom', 'date_modification')
        read_only_fields = ('__all__',)

    def get_modifie_par_nom(self, obj):
        if obj.modifie_par:
            return obj.modifie_par.get_full_name() or obj.modifie_par.matricule
        return "Système"


class ReclamationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    etudiant_matricule = serializers.CharField(source='etudiant.matricule', read_only=True)
    etudiant_nom = serializers.SerializerMethodField()
    code_module = serializers.CharField(source='note_elementaire.code_module', read_only=True)
    est_en_retard = serializers.SerializerMethodField()

    class Meta:
        model = Reclamation
        fields = ('id', 'motif', 'statut', 'date_creation', 'date_limite_traitement',
                  'etudiant_matricule', 'etudiant_nom', 'code_module', 'est_en_retard')
        read_only_fields = ('__all__',)

    def get_etudiant_nom(self, obj):
        return obj.etudiant.get_full_name() or obj.etudiant.matricule

    def get_est_en_retard(self, obj):
        return obj.est_en_retard()


class ReclamationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single reclamation view."""
    pieces_jointes = PieceJointeSerializer(many=True, read_only=True)
    historique_statuts = HistoriqueStatutSerializer(many=True, read_only=True)
    etudiant_info = serializers.SerializerMethodField()
    est_en_retard = serializers.SerializerMethodField()

    class Meta:
        model = Reclamation
        fields = ('id', 'motif', 'statut', 'description', 'commentaire_decision',
                  'etudiant', 'etudiant_info', 'note_elementaire', 'coordonnateur',
                  'date_creation', 'date_limite_traitement', 'date_traitement',
                  'note_originale', 'nouvelle_note',
                  'pieces_jointes', 'historique_statuts', 'est_en_retard',
                  'enseignant_assigne', 'commentaire_professeur')
        read_only_fields = ('id', 'etudiant', 'date_creation', 'date_limite_traitement',
                           'date_traitement', 'note_originale', 'est_en_retard')

    def get_etudiant_info(self, obj):
        return {
            'matricule': obj.etudiant.matricule,
            'nom': obj.etudiant.get_full_name(),
            'email': obj.etudiant.email,
        }

    def get_est_en_retard(self, obj):
        return obj.est_en_retard()


class ReclamationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a reclamation.
    Validates RG-02 (unicité) and RG-03 (conflit) business rules.
    """
    pieces_jointes = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Reclamation
        fields = ('id', 'motif', 'description', 'note_elementaire', 'pieces_jointes')
        read_only_fields = ('id',)

    def validate_note_elementaire(self, value):
        """RG-02: Check if an active reclamation already exists for this note."""
        user = self.context['request'].user
        active_statuses = [StatutReclamation.EN_ATTENTE, StatutReclamation.EN_COURS]

        if Reclamation.objects.filter(
            etudiant=user,
            note_elementaire=value,
            statut__in=active_statuses
        ).exists():
            raise serializers.ValidationError(
                "Une réclamation active existe déjà pour cette note. (RG-02)"
            )

        # RG-03: Check if a reclamation was already accepted for this note
        if Reclamation.objects.filter(
            etudiant=user,
            note_elementaire=value,
            statut=StatutReclamation.ACCEPTEE
        ).exists():
            raise serializers.ValidationError(
                "Cette note a déjà fait l'objet d'une réclamation acceptée. "
                "Veuillez contacter la scolarité. (RG-03)"
            )

        return value

    def create(self, validated_data):
        pieces = validated_data.pop('pieces_jointes', [])
        user = self.context['request'].user

        # Get original note value
        note = validated_data.get('note_elementaire')
        if note:
            validated_data['note_originale'] = note.valeur_note

        # etudiant is already in validated_data from serializer.save(etudiant=...)
        validated_data['etudiant'] = user
        reclamation = Reclamation.objects.create(**validated_data)

        # Create status history entry
        HistoriqueStatut.objects.create(
            reclamation=reclamation,
            statut_precedent=None,
            nouveau_statut=StatutReclamation.EN_ATTENTE,
            modifie_par=user,
            commentaire="Création de la réclamation",
        )

        # Handle file uploads
        for fichier in pieces:
            PieceJointe.objects.create(
                reclamation=reclamation,
                fichier=fichier,
                nom_fichier=fichier.name,
                taille=fichier.size,
            )

        return reclamation


class ReclamationTraiterSerializer(serializers.ModelSerializer):
    """Serializer for coordinator to update reclamation status."""

    class Meta:
        model = Reclamation
        fields = ('statut', 'commentaire_decision')
        read_only_fields = ('statut',)

    def validate(self, data):
        if not data.get('commentaire_decision'):
            raise serializers.ValidationError(
                "Un commentaire de décision est obligatoire."
            )
        return data


class ReclamationDecisionSerializer(serializers.Serializer):
    """Serializer for accept/reject actions."""
    commentaire_decision = serializers.CharField(required=True)
    nouvelle_note = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True
    )

    def validate_commentaire_decision(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Le commentaire de décision est obligatoire."
            )
        return value