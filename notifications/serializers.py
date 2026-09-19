from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.user.get_full_name", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "customer",
            "customer_name",
            "title",
            "message",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["created_at"]
