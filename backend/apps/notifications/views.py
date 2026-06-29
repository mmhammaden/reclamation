from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    """
    GET /api/notifications/
    Returns notifications for the current user.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(destinataire=self.request.user)


class NotificationMarkReadView(generics.UpdateAPIView):
    """
    PATCH /api/notifications/{id}/read/
    Mark a notification as read.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        try:
            notification = self.get_object()
            if notification.destinataire != request.user:
                return Response(
                    {"detail": "Vous ne pouvez pas modifier cette notification."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            notification.marquer_comme_lu()
            serializer = self.get_serializer(notification)
            return Response(serializer.data)
        except Notification.DoesNotExist:
            return Response(
                {"detail": "Notification introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )


class NotificationUnreadCountView(generics.GenericAPIView):
    """
    GET /api/notifications/unread-count/
    Returns the count of unread notifications.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        count = Notification.objects.filter(
            destinataire=request.user, est_lu=False
        ).count()
        return Response({"unread_count": count})