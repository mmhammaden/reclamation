from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('destinataire', 'type_notification', 'contenu_court', 'est_lu', 'date_creation')
    list_filter = ('type_notification', 'est_lu', 'date_creation')
    search_fields = ('destinataire__matricule', 'contenu')
    readonly_fields = ('date_creation',)

    def contenu_court(self, obj):
        return obj.contenu[:75] + '...' if len(obj.contenu) > 75 else obj.contenu
    contenu_court.short_description = "Contenu"