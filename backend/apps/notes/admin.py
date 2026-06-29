from django.contrib import admin
from .models import NoteElementaire


@admin.register(NoteElementaire)
class NoteElementaireAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'code_module', 'valeur_note', 'semestre', 'annee_academique', 'est_verouillee')
    list_filter = ('annee_academique', 'semestre', 'code_module', 'est_verouillee')
    search_fields = ('etudiant__matricule', 'code_module', 'nom_module')
    readonly_fields = ('date_import',)

    actions = ['verrouiller_notes', 'deverrouiller_notes']

    def verrouiller_notes(self, request, queryset):
        queryset.update(est_verouillee=True)
        self.message_user(request, f"{queryset.count()} note(s) verrouillée(s).")
    verrouiller_notes.short_description = "Verrouiller les notes sélectionnées"

    def deverrouiller_notes(self, request, queryset):
        queryset.update(est_verouillee=False)
        self.message_user(request, f"{queryset.count()} note(s) déverrouillée(s).")
    deverrouiller_notes.short_description = "Déverrouiller les notes sélectionnées"