from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),

    path("news/", views.news_list, name="news"),
    path("news/<int:pk>/", views.news_detail, name="news_detail"),
    path("news/create/", views.news_create, name="news_create"),
    path("news/<int:pk>/edit/", views.news_edit, name="news_edit"),

    path("tasks/", views.task_list, name="task"),
    path("tasks/create/", views.task_create, name="task_create"),
    path("tasks/<int:pk>/edit/", views.task_edit, name="task_edit"),
    path("tasks/<int:pk>/complete/", views.task_complete, name="task_complete"),

    path("events/", views.events, name="events"),
    path("events/create/", views.event_create, name="event_create"),
    path("events/<int:pk>/edit/", views.event_edit, name="event_edit"),
    path("events/<int:pk>/delete/", views.event_delete, name="event_delete"),

    path("documents/", views.document_list, name="documents"),
    path("documents/create/", views.document_create, name="document_create"),
    path("documents/<int:pk>/", views.document_detail, name="document_detail"),
    path("documents/<int:pk>/edit/", views.document_edit, name="document_edit"),
    path("documents/<int:pk>/delete/", views.document_delete, name="document_delete"),

    path("work/start/", views.start_work, name="start_work"),
    path("work/end/", views.end_work, name="end_work"),
    path("work/time/", views.get_work_time, name="get_work_time"),

    path("org-structure/<slug:slug>/", views.department_page, name="department_page"),
]