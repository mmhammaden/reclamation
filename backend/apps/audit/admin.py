from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'note_elementaire', 'ancienne_valeur', 'nouvelle_valeur', 'auteur', 'date_modification')
    list_filter = ('date_modification', 'auteur')
    search_fields = ('note_elementaire__code_module', 'auteur__matricule')
    readonly_fields = ('note_elementaire', 'reclamation', 'ancienne_valeur', 'nouvelle_valeur',
                       'auteur', 'commentaire', 'date_modification')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False