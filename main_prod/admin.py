from django.contrib import admin
from .models import News, Task, Event, Document, WorkSession


class DepartmentFilteredAdminMixin:
    """
    Менеджмент и superuser видят всё.
    Остальные — только записи своего отдела и общие записи.
    """

    department_field = "department"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user

        if user.is_superuser or getattr(user, "is_management", False) or getattr(user, "is_admin", False):
            return qs

        department = getattr(user, "department", None)
        if not department:
            return qs.filter(**{f"{self.department_field}__isnull": True})

        return qs.filter(**{f"{self.department_field}__in": [department, None]})

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        return super().formfield_for_choice_field(db_field, request, **kwargs)


@admin.register(News)
class NewsAdmin(DepartmentFilteredAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "author",
        "department",
        "is_published",
        "published_at",
        "views_count",
    )
    list_filter = ("category", "is_published", "department", "published_at")
    search_fields = (
        "title",
        "content",
        "author__username",
        "author__first_name",
        "author__last_name",
        "author__email",
    )
    autocomplete_fields = ("author",)
    readonly_fields = ("views_count", "created_at")
    date_hierarchy = "published_at"
    ordering = ("-published_at",)
    list_editable = ("is_published",)

    fieldsets = (
        ("Основное", {
            "fields": ("title", "content", "category", "image"),
        }),
        ("Публикация", {
            "fields": ("author", "department", "is_published", "published_at"),
        }),
        ("Системное", {
            "fields": ("views_count", "created_at"),
        }),
    )

    actions = ("make_published", "make_unpublished")

    @admin.action(description="Опубликовать выбранные")
    def make_published(self, request, queryset):
        queryset.update(is_published=True)

    @admin.action(description="Снять с публикации")
    def make_unpublished(self, request, queryset):
        queryset.update(is_published=False)

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.author_id:
            obj.author = request.user
        if not getattr(request.user, "is_superuser", False) and not getattr(request.user, "is_management", False):
            if hasattr(request.user, "department"):
                obj.department = request.user.department
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or getattr(request.user, "is_management", False):
            return True
        if obj and obj.author_id == request.user.id:
            return True
        return False


@admin.register(Task)
class TaskAdmin(DepartmentFilteredAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "assigned_to",
        "created_by",
        "priority",
        "is_completed",
        "deadline",
        "created_at",
    )
    list_filter = ("priority", "is_completed", "assigned_to__department", "deadline")
    search_fields = (
        "title",
        "description",
        "assigned_to__username",
        "assigned_to__first_name",
        "assigned_to__last_name",
        "created_by__username",
    )
    autocomplete_fields = ("assigned_to", "created_by")
    readonly_fields = ("created_at",)
    ordering = ("is_completed", "deadline", "-created_at")
    list_editable = ("priority", "is_completed")

    fieldsets = (
        ("Основное", {
            "fields": ("title", "description"),
        }),
        ("Исполнение", {
            "fields": ("assigned_to", "created_by", "priority", "deadline", "is_completed"),
        }),
        ("Системное", {
            "fields": ("created_at",),
        }),
    )

    actions = ("mark_completed", "mark_uncompleted")

    @admin.action(description="Отметить выполненными")
    def mark_completed(self, request, queryset):
        queryset.update(is_completed=True)

    @admin.action(description="Отметить невыполненными")
    def mark_uncompleted(self, request, queryset):
        queryset.update(is_completed=False)

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user

        if user.is_superuser or getattr(user, "is_management", False) or getattr(user, "is_admin", False):
            return qs

        department = getattr(user, "department", None)
        if not department:
            return qs.filter(assigned_to=user)

        return qs.filter(assigned_to__department=department)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assigned_to":
            qs = db_field.remote_field.model.objects.filter(is_active=True)
            user = request.user
            if not (user.is_superuser or getattr(user, "is_management", False) or getattr(user, "is_admin", False)):
                department = getattr(user, "department", None)
                if department:
                    qs = qs.filter(department=department)
                else:
                    qs = qs.filter(pk=user.pk)
            kwargs["queryset"] = qs.order_by("first_name", "last_name", "username")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Event)
class EventsAdmin(DepartmentFilteredAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "date",
        "start_time",
        "end_time",
        "department",
        "created_by",
    )
    list_filter = ("date", "department")
    search_fields = (
        "title",
        "description",
        "department",
        "created_by__username",
        "created_by__first_name",
        "created_by__last_name",
    )
    autocomplete_fields = ("created_by",)
    ordering = ("date", "start_time")

    fieldsets = (
        ("Основное", {
            "fields": ("title", "description"),
        }),
        ("Дата и время", {
            "fields": ("date", "start_time", "end_time"),
        }),
        ("Доступ", {
            "fields": ("department", "created_by"),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.created_by_id:
            obj.created_by = request.user
        if not request.user.is_superuser and not getattr(request.user, "is_management", False):
            obj.department = getattr(request.user, "department", None)
        super().save_model(request, obj, form, change)


@admin.register(Document)
class DocumentAdmin(DepartmentFilteredAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "department",
        "uploaded_by",
        "uploaded_at",
    )
    list_filter = ("department", "uploaded_at")
    search_fields = (
        "title",
        "department",
        "uploaded_by__username",
        "uploaded_by__first_name",
        "uploaded_by__last_name",
    )
    autocomplete_fields = ("uploaded_by",)
    readonly_fields = ("uploaded_at",)
    ordering = ("-uploaded_at",)

    fieldsets = (
        ("Основное", {
            "fields": ("title", "file"),
        }),
        ("Доступ", {
            "fields": ("department", "uploaded_by"),
        }),
        ("Системное", {
            "fields": ("uploaded_at",),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.uploaded_by_id:
            obj.uploaded_by = request.user
        if not request.user.is_superuser and not getattr(request.user, "is_management", False):
            obj.department = getattr(request.user, "department", None)
        super().save_model(request, obj, form, change)


@admin.register(WorkSession)
class WorkSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "date", "start_time", "end_time")
    list_filter = ("date", "user__department")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
    )
    autocomplete_fields = ("user",)
    ordering = ("-date", "-start_time")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user

        if user.is_superuser or getattr(user, "is_management", False) or getattr(user, "is_admin", False):
            return qs

        department = getattr(user, "department", None)
        if not department:
            return qs.filter(user=user)

        return qs.filter(user__department=department)

    def has_add_permission(self, request):
        return request.user.is_superuser or getattr(request.user, "is_management", False)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or getattr(request.user, "is_management", False)