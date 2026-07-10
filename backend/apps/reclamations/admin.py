from django.contrib import admin
from django.utils import timezone
from .models import Reclamation, LigneReclamation, PieceJointe, HistoriqueStatut


class LigneReclamationInline(admin.TabularInline):
    model = LigneReclamation
    extra = 0
    readonly_fields = ('note_originale',)
    can_delete = True


class PieceJointeInline(admin.TabularInline):
    model = PieceJointe
    extra = 0
    readonly_fields = ('nom_fichier', 'taille', 'date_ajout')


class HistoriqueStatutInline(admin.TabularInline):
    model = HistoriqueStatut
    extra = 0
    readonly_fields = ('statut_precedent', 'nouveau_statut', 'modifie_par', 'date_modification')
    can_delete = False


@admin.register(Reclamation)
class ReclamationAdmin(admin.ModelAdmin):
    list_display = ('id', 'etudiant', 'statut', 'date_creation', 'date_limite_traitement', 'est_en_retard')
    list_filter = ('statut', 'date_creation')
    search_fields = ('etudiant__matricule', 'etudiant__email', 'description')
    readonly_fields = ('date_creation', 'date_limite_traitement', 'date_traitement')
    inlines = [LigneReclamationInline, PieceJointeInline, HistoriqueStatutInline]

    fieldsets = (
        ('Informations générales', {
            'fields': ('etudiant', 'description', 'statut')
        }),
        ('Traitement', {
            'fields': ('coordonnateur', 'commentaire_decision', 'date_traitement')
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_limite_traitement')
        }),
    )

    actions = ['marquer_en_cours', 'marquer_acceptee', 'marquer_rejetee']

    def marquer_en_cours(self, request, queryset):
        queryset.update(statut='EN_COURS')
    marquer_en_cours.short_description = "Marquer comme 'En cours'"

    def marquer_acceptee(self, request, queryset):
        queryset.update(statut='ACCEPTEE', date_traitement=timezone.now())
    marquer_acceptee.short_description = "Marquer comme 'Acceptée'"

    def marquer_rejetee(self, request, queryset):
        queryset.update(statut='REJETEE', date_traitement=timezone.now())
    marquer_rejetee.short_description = "Marquer comme 'Rejetée'"


@admin.register(PieceJointe)
class PieceJointeAdmin(admin.ModelAdmin):
    list_display = ('nom_fichier', 'reclamation', 'taille', 'date_ajout')
    search_fields = ('nom_fichier', 'reclamation__id')


@admin.register(HistoriqueStatut)
class HistoriqueStatutAdmin(admin.ModelAdmin):
    list_display = ('reclamation', 'statut_precedent', 'nouveau_statut', 'modifie_par', 'date_modification')
    list_filter = ('date_modification',)
    readonly_fields = ('statut_precedent', 'nouveau_statut', 'modifie_par', 'date_modification')