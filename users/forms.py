from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm

User = get_user_model()


class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css} form-control".strip()
            if field.label:
                field.widget.attrs.setdefault("placeholder", field.label)


class LoginForm(StyledFormMixin, forms.Form):
    username = forms.CharField(label="Логин")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    error_messages = {
        "invalid_login": "Неверный логин или пароль.",
        "inactive": "Учетная запись отключена.",
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password,
            )
            if self.user_cache is None:
                raise forms.ValidationError(self.error_messages["invalid_login"])
            if not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages["inactive"])

        return cleaned_data

    def get_user(self):
        return self.user_cache


class RegistrationForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "department",
            "password1",
            "password2",
        )
        labels = {
            "username": "Логин",
            "first_name": "Имя",
            "last_name": "Фамилия",
            "department": "Отдел",
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email уже используется.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].strip().lower()
        user.role = User.Role.EMPLOYEE
        if commit:
            user.save()
        return user


class ProfileUpdateForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "department")
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Email",
            "department": "Отдел",
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Email уже используется.")
        return email


class UserPasswordChangeForm(StyledFormMixin, PasswordChangeForm):
    old_password = forms.CharField(label="Текущий пароль", widget=forms.PasswordInput)
    new_password1 = forms.CharField(label="Новый пароль", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput)