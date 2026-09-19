from audit.models import AuditLog


def client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def write_audit_log(request, action, table_name, record_id, description=""):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return None

    return AuditLog.objects.create(
        user=user,
        action=action,
        table_name=table_name,
                record_id=record_id,
        description=description,
        ip_address=client_ip(request),
    )
