from django.urls import path
from .views import change_password, profile, profile_edit, register, user_login, user_logout

urlpatterns = [
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("register/", register, name="register"),
    path("profile/", profile, name="profile"),
    path("profile/edit/", profile_edit, name="profile_edit"),
    path("profile/password/", change_password, name="change_password"),
]