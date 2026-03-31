from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "admin", "Администратор"
        MANAGEMENT = "management", "Менеджмент"
        ACCOUNTANT = "accountant", "Бухгалтер"
        EDITOR = "editor", "Редактор"
        EMPLOYEE = "employee", "Сотрудник"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE
    )

    department = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # 🔥 УДОБНЫЕ ХЕЛПЕРЫ

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_management(self):
        return self.role == self.Role.MANAGEMENT

    @property
    def is_accountant(self):
        return self.role == self.Role.ACCOUNTANT

    @property
    def is_editor(self):
        return self.role == self.Role.EDITOR