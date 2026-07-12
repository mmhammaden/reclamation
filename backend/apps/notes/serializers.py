from rest_framework import serializers
from .models import ResultatSemestre, Module, ElementModule


class ElementModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementModule
        fields = ('id', 'code_element', 'nom_element', 'note_continu', 'note_final', 'note_moyenne',
                  'credit', 'observation')
        read_only_fields = ('id',)


class ModuleSerializer(serializers.ModelSerializer):
    elements = ElementModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ('id', 'code_module', 'nom_module', 'moy_module', 'note_finale',
                  'credit', 'observation', 'elements')
        read_only_fields = ('id',)


class ResultatSemestreSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = ResultatSemestre
        fields = ('id', 'moy_semestre', 'observation', 'semestre',
                  'annee_academique', 'modules')
        read_only_fields = ('id',)


class ResultatSemestreListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list view without nested modules."""
    class Meta:
        model = ResultatSemestre
        fields = ('id', 'moy_semestre', 'observation', 'semestre', 'annee_academique')
        read_only_fields = ('id',)