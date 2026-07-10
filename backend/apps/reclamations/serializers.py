from rest_framework import serializers
from django.utils import timezone
from .models import Reclamation, LigneReclamation, PieceJointe, HistoriqueStatut, StatutReclamation
from apps.notes.models import NoteElementaire


class PieceJointeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PieceJointe
        fields = ('id', 'fichier', 'nom_fichier', 'taille', 'date_ajout')
        read_only_fields = ('id', 'nom_fichier', 'taille', 'date_ajout')

    def validate_fichier(self, value):
        import os
        ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg'}
        MAX_SIZE = 10 * 1024 * 1024
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(f"Format non autorisé: {ext}.")
        if value.size > MAX_SIZE:
            raise serializers.ValidationError("Fichier trop volumineux (max 10MB).")
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


class LigneReclamationSerializer(serializers.ModelSerializer):
    code_module = serializers.CharField(source='note_elementaire.code_module', read_only=True)
    nom_module = serializers.CharField(source='note_elementaire.nom_module', read_only=True)
    pieces_jointes = serializers.SerializerMethodField()

    class Meta:
        model = LigneReclamation
        fields = ('id', 'note_elementaire', 'code_module', 'nom_module',
                  'motif', 'note_originale', 'nouvelle_note', 'description', 'pieces_jointes')
        read_only_fields = ('id', 'code_module', 'nom_module', 'note_originale')

    def get_pieces_jointes(self, obj):
        return PieceJointeSerializer(obj.pieces_jointes.all(), many=True).data


class LigneReclamationCreateSerializer(serializers.Serializer):
    note_elementaire = serializers.PrimaryKeyRelatedField(queryset=NoteElementaire.objects.all())
    motif = serializers.ChoiceField(choices=[
        ('ERREUR_SAISIE', 'Erreur de saisie'),
        ('OUBLI_NOTE', 'Oubli de note'),
        ('VERIFICATION_COPIE', 'Vérification de copie'),
        ('AUTRE', 'Autre motif'),
    ])
    description = serializers.CharField(required=False, allow_blank=True, default='')


class ReclamationListSerializer(serializers.ModelSerializer):
    etudiant_matricule = serializers.CharField(source='etudiant.matricule', read_only=True)
    etudiant_nom = serializers.SerializerMethodField()
    modules = serializers.SerializerMethodField()
    est_en_retard = serializers.SerializerMethodField()

    class Meta:
        model = Reclamation
        fields = ('id', 'statut', 'date_creation', 'date_limite_traitement',
                  'etudiant_matricule', 'etudiant_nom', 'modules', 'est_en_retard')
        read_only_fields = ('__all__',)

    def get_etudiant_nom(self, obj):
        return obj.etudiant.get_full_name() or obj.etudiant.matricule

    def get_modules(self, obj):
        result = []
        for l in obj.lignes.select_related('note_elementaire').all():
            if l.note_elementaire:
                result.append({'code': l.note_elementaire.code_module, 'motif': l.motif})
            else:
                result.append({'code': '(Note supprimée)', 'motif': l.motif})
        return result

    def get_est_en_retard(self, obj):
        return obj.est_en_retard()


class ReclamationDetailSerializer(serializers.ModelSerializer):
    pieces_jointes = PieceJointeSerializer(many=True, read_only=True)
    historique_statuts = HistoriqueStatutSerializer(many=True, read_only=True)
    lignes = LigneReclamationSerializer(many=True, read_only=True)
    etudiant_info = serializers.SerializerMethodField()
    est_en_retard = serializers.SerializerMethodField()

    class Meta:
        model = Reclamation
        fields = ('id', 'statut', 'description', 'commentaire_decision',
                  'etudiant', 'etudiant_info', 'coordonnateur',
                  'date_creation', 'date_limite_traitement', 'date_traitement',
                  'lignes', 'pieces_jointes', 'historique_statuts', 'est_en_retard',
                  'enseignant_assigne', 'commentaire_professeur')
        read_only_fields = ('id', 'etudiant', 'date_creation', 'date_limite_traitement',
                            'date_traitement', 'est_en_retard')

    def get_etudiant_info(self, obj):
        return {
            'matricule': obj.etudiant.matricule,
            'nom': obj.etudiant.get_full_name(),
            'email': obj.etudiant.email,
        }

    def get_est_en_retard(self, obj):
        return obj.est_en_retard()


class ReclamationCreateSerializer(serializers.Serializer):
    """
    Crée une réclamation avec une ou plusieurs matières (lignes).
    RG-02: Blocage si une réclamation active existe déjà pour l'étudiant.
    """
    description = serializers.CharField(required=False, allow_blank=True, default='')
    lignes = LigneReclamationCreateSerializer(many=True, min_length=1)
    pieces_jointes = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False,
    )

    def validate_lignes(self, lignes):
        user = self.context['request'].user
        active_statuses = [StatutReclamation.EN_ATTENTE, StatutReclamation.EN_COURS]

        # RG-02: une seule réclamation active à la fois
        if Reclamation.objects.filter(etudiant=user, statut__in=active_statuses).exists():
            raise serializers.ValidationError(
                "Vous avez déjà une réclamation active en cours de traitement. (RG-02)"
            )

        # Vérifier les doublons de notes dans la même soumission
        note_ids = [l['note_elementaire'].id for l in lignes]
        if len(note_ids) != len(set(note_ids)):
            raise serializers.ValidationError("Une même matière ne peut pas apparaître deux fois.")

        # RG-03: vérifier que les notes ne sont pas déjà acceptées
        for ligne in lignes:
            note = ligne['note_elementaire']
            if LigneReclamation.objects.filter(
                note_elementaire=note,
                reclamation__etudiant=user,
                reclamation__statut=StatutReclamation.ACCEPTEE,
            ).exists():
                raise serializers.ValidationError(
                    f"La note {note.code_module} a déjà fait l'objet d'une réclamation acceptée. (RG-03)"
                )

        return lignes

    def create(self, validated_data):
        from .models import HistoriqueStatut
        lignes_data = validated_data.pop('lignes')
        pieces_globales = validated_data.pop('pieces_jointes', [])
        user = self.context['request'].user
        request = self.context['request']

        reclamation = Reclamation.objects.create(
            etudiant=user,
            description=validated_data.get('description', ''),
        )

        for i, ligne_data in enumerate(lignes_data):
            note = ligne_data['note_elementaire']
            ligne = LigneReclamation.objects.create(
                reclamation=reclamation,
                note_elementaire=note,
                motif=ligne_data['motif'],
                note_originale=note.valeur_note,
                description=ligne_data.get('description', ''),
            )
            # fichiers spécifiques à cette ligne
            for fichier in request.FILES.getlist(f'pieces_jointes_{i}'):
                PieceJointe.objects.create(
                    reclamation=reclamation,
                    ligne=ligne,
                    fichier=fichier,
                    nom_fichier=fichier.name,
                    taille=fichier.size,
                )

        HistoriqueStatut.objects.create(
            reclamation=reclamation,
            statut_precedent=None,
            nouveau_statut=StatutReclamation.EN_ATTENTE,
            modifie_par=user,
            commentaire="Création de la réclamation",
        )

        for fichier in pieces_globales:
            PieceJointe.objects.create(
                reclamation=reclamation,
                fichier=fichier,
                nom_fichier=fichier.name,
                taille=fichier.size,
            )

        return reclamation


class ReclamationDecisionSerializer(serializers.Serializer):
    commentaire_decision = serializers.CharField(required=True)
    # nouvelle_note par ligne : { note_elementaire_id: nouvelle_valeur }
    nouvelles_notes = serializers.DictField(
        child=serializers.DecimalField(max_digits=5, decimal_places=2),
        required=False,
        default=dict,
    )

    def validate_commentaire_decision(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Le commentaire de décision est obligatoire.")
        return value