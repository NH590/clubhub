def notifications(request):
    """Đưa số thông báo chưa đọc vào mọi template (chỉ cho Admin)."""
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}
    if not (user.is_superuser or getattr(user, "role", None) == "admin"):
        return {}
    from .models import Notification
    return {
        "show_bell": True,
        "unread_notifications": Notification.objects.filter(recipient=user, is_read=False).count(),
    }