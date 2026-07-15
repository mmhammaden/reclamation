from rest_framework import serializers
from .models import ResultatSemestre, ElementModule


class ElementModuleSerializer(serializers.ModelSerializer):
    # Computed properties - DRF will serialize these from @property methods
    note_moyenne = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    observation = serializers.CharField(read_only=True)

    class Meta:
        model = ElementModule
        fields = ('id', 'code_element', 'nom_matiere', 'note_continu', 'note_final', 'note_moyenne',
                  'credit', 'observation')
        read_only_fields = ('id', 'note_moyenne', 'observation')


class ResultatSemestreSerializer(serializers.ModelSerializer):
    # Computed properties - DRF will serialize these from @property methods
    moy_semestre = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    observation = serializers.CharField(read_only=True)
    elements = ElementModuleSerializer(many=True, read_only=True)

    class Meta:
        model = ResultatSemestre
        fields = ('id', 'moy_semestre', 'observation', 'semestre',
                  'annee_academique', 'elements')
        read_only_fields = ('id', 'moy_semestre', 'observation')


class ResultatSemestreListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list view without nested elements."""
    # Computed properties
    moy_semestre = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    observation = serializers.CharField(read_only=True)

    class Meta:
        model = ResultatSemestre
        fields = ('id', 'moy_semestre', 'observation', 'semestre', 'annee_academique')
        read_only_fields = ('id', 'moy_semestre', 'observation')