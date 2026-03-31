from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.utils import safe_next_url

from .forms import (
    LoginForm,
    ProfileUpdateForm,
    RegistrationForm,
    UserPasswordChangeForm,
)


def user_login(request):
    if request.user.is_authenticated:
        return redirect("index")

    form = LoginForm(request=request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect(safe_next_url(request, default="index"))

    return render(
        request,
        "auth/login.html",
        {"form": form},
    )


@login_required
def user_logout(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")
    return redirect("index")


def register(request):
    if request.user.is_authenticated:
        return redirect("index")

    form = RegistrationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Регистрация прошла успешно.")
        return redirect("index")

    return render(
        request,
        "auth/register.html",
        {"form": form},
    )


@login_required
def profile(request):
    return render(
        request,
        "auth/profile.html",
        {
            "profile_form": ProfileUpdateForm(instance=request.user),
            "password_form": UserPasswordChangeForm(user=request.user),
        },
    )


@login_required
def profile_edit(request):
    form = ProfileUpdateForm(request.POST or None, instance=request.user)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Профиль обновлён.")
        return redirect("profile")

    return render(
        request,
        "auth/profile_edit.html",
        {"form": form},
    )


@login_required
def change_password(request):
    form = UserPasswordChangeForm(user=request.user, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Пароль успешно изменён.")
        return redirect("profile")

    return render(
        request,
        "auth/change_password.html",
        {"form": form},
    )