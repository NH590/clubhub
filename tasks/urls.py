from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.task_board, name="board"),
    path("add/", views.TaskCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.TaskUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.TaskDeleteView.as_view(), name="delete"),
    path("<int:pk>/status/<str:status>/", views.change_status, name="change_status"),
]
