from django.urls import path

from . import views

app_name = "events"

urlpatterns = [
    path("", views.event_list, name="list"),
    path("add/", views.EventCreateView.as_view(), name="create"),
    path("<int:pk>/", views.EventDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.EventUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.EventDeleteView.as_view(), name="delete"),
    path("<int:pk>/register/", views.register, name="register"),
    path("<int:pk>/cancel/", views.cancel_registration, name="cancel"),
    path("<int:pk>/qr/", views.qr_page, name="qr"),
    path("<int:pk>/qr.png", views.qr_image, name="qr_image"),
    path("<int:pk>/qr/regenerate/", views.regenerate_qr, name="qr_regenerate"),
    path("<int:pk>/checkin/<uuid:token>/", views.checkin, name="checkin"),
    path("<int:pk>/attendance/<int:reg_id>/", views.toggle_attendance, name="toggle_attendance"),
]