from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import News, Task, Event, Document

User = get_user_model()


class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            current_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{current_class} form-control".strip()
            if field.label:
                field.widget.attrs.setdefault("placeholder", field.label)


class NewsForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = News
        fields = (
            "title",
            "content",
            "category",
            "department",
            "image",
            "is_published",
        )
        labels = {
            "title": "Заголовок",
            "content": "Текст новости",
            "category": "Категория",
            "department": "Отдел",
            "image": "Изображение",
            "is_published": "Опубликовать",
        }
        widgets = {
            "content": forms.Textarea(attrs={"rows": 6}),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 5:
            raise forms.ValidationError("Заголовок должен быть не короче 5 символов.")
        return title

    def clean_content(self):
        content = self.cleaned_data["content"].strip()
        if len(content) < 20:
            raise forms.ValidationError("Текст новости должен быть не короче 20 символов.")
        return content


class TaskForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            "title",
            "description",
            "assigned_to",
            "priority",
            "deadline",
            "is_completed",
        )
        labels = {
            "title": "Название",
            "description": "Описание",
            "assigned_to": "Исполнитель",
            "priority": "Приоритет",
            "deadline": "Срок",
            "is_completed": "Выполнено",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "deadline": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        qs = User.objects.filter(is_active=True).order_by("first_name", "last_name", "username")

        if self.user and not (self.user.is_superuser or self.user.is_management or self.user.is_admin):
            if self.user.department:
                qs = qs.filter(department=self.user.department)
            else:
                qs = qs.filter(pk=self.user.pk)

        self.fields["assigned_to"].queryset = qs

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 3:
            raise forms.ValidationError("Название задачи должно быть не короче 3 символов.")
        return title

    def clean_deadline(self):
        deadline = self.cleaned_data.get("deadline")
        if deadline and deadline < timezone.now():
            raise forms.ValidationError("Срок не может быть в прошлом.")
        return deadline


class EventForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = (
            "title",
            "description",
            "date",
            "start_time",
            "end_time",
            "department",
        )
        labels = {
            "title": "Название события",
            "description": "Описание",
            "date": "Дата",
            "start_time": "Время начала",
            "end_time": "Время окончания",
            "department": "Отдел",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 3:
            raise forms.ValidationError("Название события должно быть не короче 3 символов.")
        return title

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        date = cleaned_data.get("date")

        if start_time and end_time and end_time <= start_time:
            raise forms.ValidationError("Время окончания должно быть позже времени начала.")

        if date and date < timezone.now().date():
            raise forms.ValidationError("Нельзя создать событие в прошлом.")

        return cleaned_data


class DocumentForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Document
        fields = (
            "title",
            "file",
            "department",
        )
        labels = {
            "title": "Название документа",
            "file": "Файл",
            "department": "Отдел",
        }
        help_texts = {
            "title": "Например: Регламент отпусков, Инструкция по онбордингу, Отчёт за март",
            "file": "Максимальный размер файла — 10 МБ",
            "department": "Оставьте пустым, если документ общий",
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 3:
            raise forms.ValidationError("Название документа должно быть не короче 3 символов.")
        return title

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if not file:
            raise forms.ValidationError("Нужно выбрать файл.")

        max_size = 10 * 1024 * 1024
        if file.size > max_size:
            raise forms.ValidationError("Файл слишком большой. Максимум 10 МБ.")

        return file