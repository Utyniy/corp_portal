from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def role_required(*roles, raise_exception=True, redirect_to=None):
    """
    Проверка роли для function-based views.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                if redirect_to:
                    return redirect(redirect_to)
                raise PermissionDenied

            if user.role not in roles:
                if raise_exception:
                    raise PermissionDenied
                if redirect_to:
                    return redirect(redirect_to)
                raise PermissionDenied

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper