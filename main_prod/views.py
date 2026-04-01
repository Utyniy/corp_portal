from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db.models import Count, Q
from django.views.decorators.http import require_POST
from django.contrib import messages

from core.permissions import role_required
from core.services import (
    can_edit_news,
    filter_by_department,
    get_user_visible_tasks,
    is_manager,
)

from .forms import DocumentForm, EventForm, NewsForm, TaskForm
from .models import Document, Event, News, Task, WorkSession

import calendar
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from collections import defaultdict

User = get_user_model()

@login_required
def index(request):
    user = request.user
    today = timezone.localdate()
    now = timezone.now()

    news_qs = filter_by_department(
        News.objects.filter(is_published=True).select_related("author").order_by("-published_at"),
        user,
    )
    featured_news = news_qs.first()
    recent_news = list(news_qs[1:5] if featured_news else news_qs[:4])
    visible_news_count = news_qs.count()

    event_qs = filter_by_department(
        Event.objects.filter(date__gte=today).order_by("date", "start_time"),
        user,
    )
    event_list = list(event_qs[:5])
    upcoming_events_count = event_qs.count()

    tasks_qs = get_user_visible_tasks(
        Task.objects.select_related("assigned_to", "created_by").order_by("is_completed", "deadline", "-created_at"),
        user,
    )
    active_tasks_qs = tasks_qs.filter(is_completed=False)
    tasks = list(active_tasks_qs[:5])
    total_tasks = tasks_qs.count()
    completed_tasks = tasks_qs.filter(is_completed=True).count()
    report_progress = int((completed_tasks / total_tasks) * 100) if total_tasks else 0
    overdue_tasks_count = active_tasks_qs.filter(deadline__lt=now).count()
    due_soon_tasks_count = active_tasks_qs.filter(deadline__gte=now, deadline__lte=now + timedelta(days=3)).count()
    high_priority_tasks_count = active_tasks_qs.filter(priority=Task.Priority.HIGH).count()

    recent_docs_qs = filter_by_department(
        Document.objects.select_related("uploaded_by").order_by("-uploaded_at"),
        user,
    )
    recent_docs = list(recent_docs_qs[:4])
    visible_docs_count = recent_docs_qs.count()

    today_dt = datetime.today()
    year = int(request.GET.get("year", today_dt.year))
    month = int(request.GET.get("month", today_dt.month))

    months_ru = ["", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                 "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    month_name_ru = months_ru[month]

    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)
    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    today_day = today_dt.day if today_dt.year == year and today_dt.month == month else None

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    current_year = today_dt.year
    current_month = today_dt.month

    sessions = WorkSession.objects.filter(user=user, date=today).order_by("start_time")
    active_session = sessions.filter(end_time__isnull=True).first()

    total_seconds = 0
    for session in sessions:
        end = session.end_time or now
        total_seconds += max(0, int((end - session.start_time).total_seconds()))

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    worked_today_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    worked_percent = min(100, int((total_seconds / (8 * 3600)) * 100)) if total_seconds else 0

    department_value = getattr(user, "department", None)
    team_members_qs = User.objects.filter(is_active=True)
    if department_value and not is_manager(user):
        team_members_qs = team_members_qs.filter(department=department_value)
    team_members = list(team_members_qs.order_by("first_name", "last_name", "username")[:6])

    team_departments = list(
        User.objects.filter(is_active=True)
        .exclude(department__isnull=True)
        .exclude(department__exact="")
        .values("department")
        .annotate(total=Count("id"))
        .order_by("-total", "department")[:5]
    )
    if department_value and not is_manager(user):
        team_departments = [item for item in team_departments if item["department"] == department_value]

    task_status_items = [
        {"label": "Выполнено", "count": completed_tasks, "percent": report_progress, "tone": "success"},
        {"label": "В работе", "count": active_tasks_qs.count(), "percent": 100 - report_progress if total_tasks else 0, "tone": "primary"},
        {"label": "Просрочено", "count": overdue_tasks_count, "percent": int((overdue_tasks_count / total_tasks) * 100) if total_tasks else 0, "tone": "danger"},
    ]

    quick_actions = [
        {"label": "Новая задача", "url_name": "task_create", "icon": "fa-plus", "style": "primary"},
        {"label": "Новости", "url_name": "news", "icon": "fa-newspaper", "style": "secondary"},
        {"label": "Документы", "url_name": "documents", "icon": "fa-file-alt", "style": "secondary"},
    ]
    if is_manager(user):
        quick_actions.insert(1, {"label": "Создать событие", "url_name": "event_create", "icon": "fa-calendar-plus", "style": "secondary"})

    context = {
        "weekdays": weekdays,
        "month_days": month_days,
        "year": year,
        "month": month,
        "month_name_ru": month_name_ru,
        "today_day": today_day,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
        "current_year": current_year,
        "current_month": current_month,
        "featured_news": featured_news,
        "recent_news": recent_news,
        "event_list": event_list,
        "tasks": tasks,
        "report_progress": report_progress,
        "recent_docs": recent_docs,
        "worked_today_formatted": worked_today_formatted,
        "worked_percent": worked_percent,
        "active_session": active_session,
        "visible_news_count": visible_news_count,
        "upcoming_events_count": upcoming_events_count,
        "visible_docs_count": visible_docs_count,
        "overdue_tasks_count": overdue_tasks_count,
        "due_soon_tasks_count": due_soon_tasks_count,
        "high_priority_tasks_count": high_priority_tasks_count,
        "completed_tasks": completed_tasks,
        "total_tasks": total_tasks,
        "team_members": team_members,
        "team_departments": team_departments,
        "task_status_items": task_status_items,
        "quick_actions": quick_actions,
        "today": today,
        "department_title": department_value or "Все отделы",
    }
    return render(request, "main/index.html", context)

def news_list(request):
    qs = filter_by_department(
        News.objects.filter(is_published=True).select_related("author"),
        request.user,
    )

    search_query = request.GET.get("search", "").strip()
    if search_query:
        qs = qs.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    current_category = request.GET.get("category", "all")
    if current_category != "all":
        qs = qs.filter(category=current_category)

    current_sort = request.GET.get("sort", "newest")
    if current_sort == "oldest":
        qs = qs.order_by("published_at")
    elif current_sort == "popular":
        qs = qs.order_by("-views_count", "-published_at")
    else:
        qs = qs.order_by("-published_at")

    featured_news = qs.first()
    recent_news = qs.exclude(pk=featured_news.pk)[:3] if featured_news else qs[:3]
    news_list_data = qs.exclude(
        pk__in=[item.pk for item in recent_news]
    )
    if featured_news:
        news_list_data = news_list_data.exclude(pk=featured_news.pk)

    context = {
        "featured_news": featured_news,
        "recent_news": recent_news,
        "news_list": news_list_data,
        "search_query": search_query,
        "current_category": current_category,
        "current_sort": current_sort,
        "category_choices": News.Category.choices,
        "now": timezone.now(),
    }
    return render(request, "main/news.html", context)


def news_detail(request, pk):
    news = get_object_or_404(News.objects.select_related("author"), pk=pk)

    visible_qs = filter_by_department(News.objects.filter(pk=pk), request.user)
    if not visible_qs.exists():
        return redirect("news")

    news.views_count += 1
    news.save(update_fields=["views_count"])

    return render(request, "main/news_detail.html", {"news": news})


@login_required
@role_required("editor", "management", "admin")
def news_create(request):
    form = NewsForm(request.POST or None, request.FILES or None, user=request.user)

    if request.method == "POST" and form.is_valid():
        news = form.save(commit=False)
        news.author = request.user
        news.save()
        return redirect("news_detail", pk=news.pk)

    return render(
        request,
        "main/news_edit.html",
        {
            "form": form,
            "title": "Создать новость",
        },
    )


@login_required
def news_edit(request, pk):
    news = get_object_or_404(News, pk=pk)

    if not can_edit_news(request.user, news):
        return redirect("news")

    form = NewsForm(
        request.POST or None,
        request.FILES or None,
        instance=news,
        user=request.user,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("news_detail", pk=news.pk)

    return render(
        request,
        "main/news_edit.html",
        {
            "form": form,
            "title": "Редактировать новость",
        },
    )


@login_required
def task_list(request):
    tasks_qs = get_user_visible_tasks(
        Task.objects.select_related("assigned_to", "created_by").order_by("is_completed", "deadline", "-created_at"),
        request.user,
    )

    docs = filter_by_department(
        Document.objects.select_related("uploaded_by").order_by("-uploaded_at"),
        request.user,
    )[:8]

    total = tasks_qs.count()
    completed = tasks_qs.filter(is_completed=True).count()
    report_progress = int((completed / total) * 100) if total else 0

    context = {
        "tasks": tasks_qs.filter(is_completed=False),
        "archived_tasks": tasks_qs.filter(is_completed=True),
        "docs": docs,
        "report_progress": report_progress,
        "now": timezone.now(),
    }
    return render(request, "main/task.html", context)

@login_required
@require_POST
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk)

    allowed = (
        request.user.is_superuser or
        task.created_by_id == request.user.id or
        task.assigned_to_id == request.user.id
    )
    if not allowed:
        return JsonResponse({"status": "error", "message": "Нет доступа"}, status=403)

    if task.is_completed:
        return JsonResponse({"status": "success", "message": "Задача уже выполнена"})

    task.is_completed = True
    task.save(update_fields=["is_completed"])

    return JsonResponse({
        "status": "success",
        "message": "Задача завершена",
        "task_id": task.id,
    })

@login_required
def task_create(request):
    form = TaskForm(request.POST or None, user=request.user)

    if request.method == "POST" and form.is_valid():
        task = form.save(commit=False)
        task.created_by = request.user
        task.save()
        return redirect("task")

    return render(
        request,
        "main/task_form.html",
        {
            "form": form,
            "title": "Создать задачу",
        },
    )


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)

    allowed = (
        request.user.is_superuser or
        task.created_by_id == request.user.id or
        task.assigned_to_id == request.user.id
    )
    if not allowed:
        return redirect("task")

    form = TaskForm(request.POST or None, instance=task, user=request.user)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("task")

    return render(
        request,
        "main/task_form.html",
        {
            "form": form,
            "title": "Редактировать задачу",
        },
    )


def events(request):
    event_list = filter_by_department(
        Event.objects.order_by("date", "start_time"),
        request.user,
    )
    return render(request, "main/events.html", {"event_list": event_list})


@login_required
@role_required("management", "admin")
def event_create(request):
    form = EventForm(request.POST or None, user=request.user)

    if request.method == "POST" and form.is_valid():
        event = form.save(commit=False)
        event.created_by = request.user
        event.save()
        return redirect("events")

    return render(
        request,
        "main/event_form.html",
        {
            "form": form,
            "title": "Создать событие",
        },
    )
@login_required
@role_required("management", "admin")
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)

    form = EventForm(request.POST or None, instance=event, user=request.user)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Событие обновлено.")
        return redirect("events")

    return render(
        request,
        "main/event_form.html",
        {
            "form": form,
            "title": "Редактировать событие",
        },
    )


@login_required
@role_required("management", "admin")
@require_POST
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.delete()
    messages.success(request, "Событие удалено.")
    return redirect("events")

@login_required
@role_required("management", "admin")
def document_create(request):
    form = DocumentForm(request.POST or None, request.FILES or None, user=request.user)

    if request.method == "POST" and form.is_valid():
        document = form.save(commit=False)
        document.uploaded_by = request.user
        document.save()
        return redirect("task")

    return render(
        request,
        "main/document_form.html",
        {
            "form": form,
            "title": "Загрузить документ",
        },
    )

@login_required
def document_list(request):
    documents = filter_by_department(
        Document.objects.select_related("uploaded_by").order_by("-uploaded_at"),
        request.user,
    )

    search_query = request.GET.get("search", "").strip()
    if search_query:
        documents = documents.filter(
            Q(title__icontains=search_query) |
            Q(file__icontains=search_query) |
            Q(department__icontains=search_query)
        )

    current_department = request.GET.get("department", "").strip()
    if current_department:
        documents = documents.filter(department=current_department)

    departments = (
        Document.objects.exclude(department__isnull=True)
        .exclude(department__exact="")
        .values_list("department", flat=True)
        .distinct()
        .order_by("department")
    )

    context = {
        "documents": documents,
        "search_query": search_query,
        "current_department": current_department,
        "departments": departments,
    }
    return render(request, "main/documents.html", context)


@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document.objects.select_related("uploaded_by"), pk=pk)

    visible_qs = filter_by_department(Document.objects.filter(pk=pk), request.user)
    if not visible_qs.exists():
        return redirect("documents")

    return render(request, "main/document_detail.html", {"document": document})


@login_required
@role_required("management", "admin")
def document_edit(request, pk):
    document = get_object_or_404(Document, pk=pk)

    form = DocumentForm(
        request.POST or None,
        request.FILES or None,
        instance=document,
        user=request.user,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Документ обновлён.")
        return redirect("document_detail", pk=document.pk)

    return render(
        request,
        "main/document_form.html",
        {
            "form": form,
            "title": "Редактировать документ",
        },
    )

@login_required
@role_required("management", "admin")
@require_POST
def document_delete(request, pk):
    document = get_object_or_404(Document, pk=pk)
    document.delete()
    messages.success(request, "Документ удалён.")
    return redirect("documents")

@login_required
def start_work(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Метод не поддерживается"}, status=405)

    today = timezone.now().date()

    active_session = WorkSession.objects.filter(
        user=request.user,
        date=today,
        end_time__isnull=True,
    ).first()

    if active_session:
        return JsonResponse({"status": "error", "message": "Рабочий день уже начат"}, status=400)

    WorkSession.objects.create(
        user=request.user,
        date=today,
        start_time=timezone.now(),
    )
    return JsonResponse({"status": "success", "message": "Рабочий день начат"})


@login_required
def end_work(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Метод не поддерживается"}, status=405)

    session = WorkSession.objects.filter(
        user=request.user,
        end_time__isnull=True,
    ).order_by("-start_time").first()

    if not session:
        return JsonResponse({"status": "error", "message": "Нет активной сессии"}, status=400)

    session.end_time = timezone.now()
    session.save(update_fields=["end_time"])

    return JsonResponse({"status": "success", "message": "Рабочий день завершён"})

@login_required
def get_work_time(request):
    today = timezone.now().date()
    sessions = WorkSession.objects.filter(user=request.user, date=today).order_by("start_time")

    total_seconds = 0
    now = timezone.now()
    for session in sessions:
        end = session.end_time or now
        total_seconds += max(0, int((end - session.start_time).total_seconds()))

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return JsonResponse({
        "status": "success",
        "worked_today": {
            "total_seconds": total_seconds,
            "formatted": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
        }
    })

DEPARTMENT_CONFIG = {
    "management": {
        "title": "Управление",
        "department_name": "Управление",
        "icon": "📈",
        "description": "Руководящий состав компании и ключевые управленческие роли.",
    },
    "development": {
        "title": "Разработка",
        "department_name": "Разработка",
        "icon": "💻",
        "description": "Команда разработки, отвечающая за создание и поддержку продукта.",
    },
    "marketing": {
        "title": "Маркетинг",
        "department_name": "Маркетинг",
        "icon": "📣",
        "description": "Отдел продвижения, рекламы и коммуникаций с аудиторией.",
    },
    "accounting": {
        "title": "Бухгалтерия",
        "department_name": "Бухгалтерия",
        "icon": "🧾",
        "description": "Финансовый учет, отчетность и сопровождение платежей.",
    },
    "hr": {
        "title": "HR",
        "department_name": "HR",
        "icon": "👥",
        "description": "Подбор, адаптация и развитие сотрудников компании.",
    },
}

def department_page(request, slug):
    department = DEPARTMENT_CONFIG.get(slug)
    if not department:
        raise Http404("Отдел не найден")

    employees = User.objects.filter(
        department=department["department_name"]
    ).order_by("username")

    context = {
        "department_slug": slug,
        "department_title": department["title"],
        "department_name": department["department_name"],
        "department_icon": department["icon"],
        "department_description": department["description"],
        "employees": employees,
        "employees_count": employees.count(),
        "department_menu": DEPARTMENT_CONFIG,
    }
    return render(request, "main/department_page.html", context)