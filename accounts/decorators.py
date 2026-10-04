from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Dung: @role_required("admin", "board") tren view."""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles and not request.user.is_superuser:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
