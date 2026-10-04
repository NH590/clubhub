from django.urls import path

from . import views

app_name = "finance"

urlpatterns = [
    path("", views.transaction_list, name="list"),
    path("add/", views.TransactionCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.TransactionUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.TransactionDeleteView.as_view(), name="delete"),
    path("<int:pk>/approve/", views.approve, name="approve"),
    path("<int:pk>/reject/", views.reject, name="reject"),
]
