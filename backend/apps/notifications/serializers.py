from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'type_notification', 'contenu', 'est_lu', 'date_creation', 'date_lecture', 'reclamation')
        read_only_fields = ('id', 'date_creation', 'date_lecture')