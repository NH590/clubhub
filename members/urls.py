from django.urls import path

from . import views

app_name = "members"

urlpatterns = [
    path("add/", views.MembershipCreateView.as_view(), name="membership_create"),
    path("<int:pk>/edit/", views.MembershipUpdateView.as_view(), name="membership_update"),
    path("<int:pk>/delete/", views.MembershipDeleteView.as_view(), name="membership_delete"),

    path("departments/add/", views.DepartmentCreateView.as_view(), name="department_create"),
    path("departments/<int:pk>/", views.DepartmentDetailView.as_view(), name="department_detail"),
    path("departments/<int:pk>/edit/", views.DepartmentUpdateView.as_view(), name="department_update"),
    path("departments/<int:pk>/delete/", views.DepartmentDeleteView.as_view(), name="department_delete"),
    path("", views.member_list, name="list"),
    path("departments/", views.department_list, name="departments"),

]