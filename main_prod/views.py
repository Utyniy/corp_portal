from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.contrib import messages

from core.permissions import role_required
from core.services import (
    can_edit_news,
    filter_by_department,
    get_user_visible_tasks,
)

from .forms import DocumentForm, EventForm, NewsForm, TaskForm
from .models import Document, Event, News, Task, WorkSession

import calendar
from datetime import datetime
from django.utils import timezone

@login_required
def index(request):
    user = request.user

    news_qs = filter_by_department(
        News.objects.filter(is_published=True).select_related("author").order_by("-published_at"),
        user,
    )
    featured_news = news_qs.first()
    recent_news = news_qs[1:4] if featured_news else news_qs[:3]

    event_list = filter_by_department(
        Event.objects.filter(date__gte=timezone.now().date()).order_by("date", "start_time"),
        user,
    )[:4]

    tasks_qs = get_user_visible_tasks(
        Task.objects.select_related("assigned_to", "created_by").order_by("is_completed", "deadline", "-created_at"),
        user,
    )
    tasks = tasks_qs.filter(is_completed=False)[:4]

    recent_docs = filter_by_department(
        Document.objects.select_related("uploaded_by").order_by("-uploaded_at"),
        user,
    )[:3]

    total_tasks = tasks_qs.count()
    completed_tasks = tasks_qs.filter(is_completed=True).count()
    report_progress = int((completed_tasks / total_tasks) * 100) if total_tasks else 0

    today = datetime.today()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    months_ru = ["", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                 "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    month_name_ru = months_ru[month]

    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)
    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    today_day = today.day if today.year == year and today.month == month else None

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    current_year = today.year
    current_month = today.month

    today_date = timezone.now().date()
    sessions = WorkSession.objects.filter(user=user, date=today_date).order_by("start_time")

    total_seconds = 0
    now = timezone.now()
    for session in sessions:
        end = session.end_time or now
        total_seconds += max(0, int((end - session.start_time).total_seconds()))

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    worked_today_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    worked_percent = min(100, int((total_seconds / (8 * 3600)) * 100)) if total_seconds else 0

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