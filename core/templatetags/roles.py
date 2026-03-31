from django import template

register = template.Library()


@register.filter
def has_role(user, role):
    return user.is_authenticated and getattr(user, "role", None) == role


@register.filter
def has_any_role(user, roles):
    if not user.is_authenticated:
        return False

    roles_list = [item.strip() for item in roles.split(",") if item.strip()]
    return getattr(user, "role", None) in roles_list


@register.simple_tag
def is_manager(user):
    if not user.is_authenticated:
        return False
    return getattr(user, "role", None) in {"admin", "management"}