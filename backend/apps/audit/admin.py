from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'element_module', 'type_note', 'ancienne_valeur', 'nouvelle_valeur', 'auteur', 'date_modification')
    list_filter = ('date_modification', 'auteur', 'type_note')
    search_fields = ('element_module__code_element', 'auteur__matricule')
    readonly_fields = ('element_module', 'type_note', 'reclamation', 'ancienne_valeur', 'nouvelle_valeur',
                       'auteur', 'commentaire', 'date_modification')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False