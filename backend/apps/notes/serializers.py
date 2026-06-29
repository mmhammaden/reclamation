from rest_framework import serializers
from .models import NoteElementaire


class NoteElementaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteElementaire
        fields = ('id', 'code_module', 'nom_module', 'valeur_note',
                  'coefficient', 'semestre', 'annee_academique', 'est_verouillee')
        read_only_fields = ('id', 'date_import', 'est_verouillee')