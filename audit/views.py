from rest_framework.viewsets import ReadOnlyModelViewSet

from users.permissions import IsBankStaff

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related("user", "user__role")
    serializer_class = AuditLogSerializer
    permission_classes = [IsBankStaff]
