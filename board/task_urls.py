from django.urls import path
from .views import create_task, TaskClass, change_task_status, note_task

urlpatterns = [
    path("", TaskClass.as_view(), name="taskUrl"),
    path("create_task/", create_task),
    path("change_task_status/", change_task_status),
    path("note_task/", note_task),
]
