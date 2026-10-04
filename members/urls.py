from django.urls import path

from . import views

app_name = "members"

urlpatterns = [
    path("", views.member_list, name="list"),
    path("departments/", views.department_list, name="departments"),
]