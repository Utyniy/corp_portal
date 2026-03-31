from django.conf import settings
from django.db import models
from django.utils import timezone


class DepartmentScopedModel(models.Model):
    department = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Отдел",
        help_text="Если пусто — запись доступна всем отделам.",
    )

    class Meta:
        abstract = True


class News(DepartmentScopedModel):
    class Category(models.TextChoices):
        GENERAL = "general", "Общее"
        HR = "hr", "HR"
        IT = "it", "IT"
        FINANCE = "finance", "Финансы"
        EVENTS = "events", "События"

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержимое")
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.GENERAL,
        verbose_name="Категория",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="news_items",
        verbose_name="Автор",
    )
    image = models.ImageField(
        upload_to="news/",
        blank=True,
        null=True,
        verbose_name="Изображение",
    )
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")
    published_at = models.DateTimeField(default=timezone.now, verbose_name="Дата публикации")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ("-published_at", "-id")

    def __str__(self):
        return self.title


class Event(DepartmentScopedModel):
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    date = models.DateField(verbose_name="Дата")
    start_time = models.TimeField(blank=True, null=True, verbose_name="Время начала")
    end_time = models.TimeField(blank=True, null=True, verbose_name="Время окончания")
    location = models.CharField(max_length=255, blank=True, verbose_name="Место")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_events",
        verbose_name="Создал",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"
        ordering = ("date", "start_time", "id")

    def __str__(self):
        return f"{self.title} ({self.date})"


class Task(DepartmentScopedModel):
    class Priority(models.TextChoices):
        LOW = "low", "Низкий"
        MEDIUM = "medium", "Средний"
        HIGH = "high", "Высокий"

    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="Исполнитель",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tasks",
        verbose_name="Создатель",
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name="Приоритет",
    )
    deadline = models.DateTimeField(blank=True, null=True, verbose_name="Срок")
    is_completed = models.BooleanField(default=False, verbose_name="Выполнено")
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата выполнения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ("is_completed", "-created_at", "-id")

    def __str__(self):
        return self.title

    def mark_completed(self):
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save(update_fields=["is_completed", "completed_at", "updated_at"])


class Document(DepartmentScopedModel):
    title = models.CharField(max_length=255, verbose_name="Название")
    file = models.FileField(upload_to="documents/", verbose_name="Файл")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_documents",
        verbose_name="Загрузил",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Загружено")

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ("-uploaded_at", "-id")

    def __str__(self):
        return self.title


class WorkSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="work_sessions",
        verbose_name="Пользователь",
    )
    date = models.DateField(default=timezone.localdate, verbose_name="Дата")
    start_time = models.DateTimeField(verbose_name="Начало")
    end_time = models.DateTimeField(blank=True, null=True, verbose_name="Окончание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        verbose_name = "Рабочая сессия"
        verbose_name_plural = "Рабочие сессии"
        ordering = ("-date", "-start_time", "-id")

    def __str__(self):
        return f"{self.user} — {self.date}"

    @property
    def duration_seconds(self):
        end = self.end_time or timezone.now()
        return max(0, int((end - self.start_time).total_seconds()))
