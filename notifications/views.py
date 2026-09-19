from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.permissions import IsActiveAuthenticated, IsOperationsStaff, is_customer

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(ModelViewSet):
    queryset = Notification.objects.select_related("customer", "customer__user")
    serializer_class = NotificationSerializer
    permission_classes = [IsActiveAuthenticated]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsOperationsStaff()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        if is_customer(self.request.user):
            return queryset.filter(customer__user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        return Response(NotificationSerializer(notification).data)
