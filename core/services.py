from django.db.models import Q


def has_role(user, *roles):
    return user.is_authenticated and user.role in roles


def is_admin(user):
    return user.is_authenticated and getattr(user, "role", None) == user.Role.ADMIN


def is_management(user):
    return user.is_authenticated and getattr(user, "role", None) == user.Role.MANAGEMENT


def is_accountant(user):
    return user.is_authenticated and getattr(user, "role", None) == user.Role.ACCOUNTANT


def is_editor(user):
    return user.is_authenticated and getattr(user, "role", None) == user.Role.EDITOR


def is_employee(user):
    return user.is_authenticated and getattr(user, "role", None) == user.Role.EMPLOYEE


def is_manager(user):
    return user.is_authenticated and getattr(user, "role", None) in {
        user.Role.ADMIN,
        user.Role.MANAGEMENT,
    }


def can_manage_news(user):
    return user.is_authenticated and getattr(user, "role", None) in {
        user.Role.ADMIN,
        user.Role.MANAGEMENT,
        user.Role.EDITOR,
    }


def can_edit_news(user, news):
    if not user.is_authenticated:
        return False

    if is_manager(user):
        return True

    if is_editor(user) and news.author_id == user.id:
        return True

    return False


def can_manage_tasks(user):
    return user.is_authenticated and getattr(user, "role", None) in {
        user.Role.ADMIN,
        user.Role.MANAGEMENT,
    }


def can_access_accounting(user):
    return user.is_authenticated and getattr(user, "role", None) in {
        user.Role.ADMIN,
        user.Role.MANAGEMENT,
        user.Role.ACCOUNTANT,
    }


def can_view_department(user, obj):
    """
    Проверка доступа к объекту по отделу.
    Ожидается, что у obj есть поле department.
    """
    if not user.is_authenticated:
        return getattr(obj, "department", None) in (None, "")

    if is_manager(user) or is_accountant(user):
        return True

    obj_department = getattr(obj, "department", None)
    user_department = getattr(user, "department", None)

    return obj_department in (None, "", user_department)


def filter_by_department(queryset, user, department_field="department"):
    """
    Фильтрация queryset по отделу пользователя.
    Для management/admin/accountant — всё.
    Для остальных — свой отдел + общие записи.
    """
    if not user.is_authenticated:
        return queryset.filter(**{f"{department_field}__isnull": True})

    if is_manager(user) or is_accountant(user):
        return queryset

    user_department = getattr(user, "department", None)

    if user_department:
        return queryset.filter(
            Q(**{department_field: user_department}) |
            Q(**{f"{department_field}__isnull": True})
        )

    return queryset.filter(**{f"{department_field}__isnull": True})


def get_user_visible_tasks(queryset, user):
    """
    Обычный сотрудник видит свои задачи.
    Менеджмент/admin — все.
    """
    if not user.is_authenticated:
        return queryset.none()

    if is_manager(user):
        return queryset

    return queryset.filter(assigned_to=user)