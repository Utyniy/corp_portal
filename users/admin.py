from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "department",
        )


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "department",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "role",
        "department",
        "is_staff",
        "is_superuser",
        "is_active",
    )
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "department",
    )
    ordering = ("id",)

    fieldsets = (
        ("Авторизация", {
            "fields": ("username", "password"),
        }),
        ("Личная информация", {
            "fields": ("first_name", "last_name", "email"),
        }),
        ("Роль и отдел", {
            "fields": ("role", "department"),
        }),
        ("Права доступа", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),
        ("Важные даты", {
            "fields": ("last_login", "date_joined"),
        }),
    )

    add_fieldsets = (
        ("Создание пользователя", {
            "classes": ("wide",),
            "fields": (
                "username",
                "first_name",
                "last_name",
                "email",
                "role",
                "department",
                "password1",
                "password2",
                "is_staff",
                "is_active",
            ),
        }),
    )