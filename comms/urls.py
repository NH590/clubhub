from django.urls import path

from . import views

app_name = "comms"

urlpatterns = [
    path("", views.announcement_list, name="announcements"),
    path("add/", views.AnnouncementCreateView.as_view(), name="announcement_create"),
    path("<int:pk>/", views.AnnouncementDetailView.as_view(), name="announcement_detail"),
    path("<int:pk>/edit/", views.AnnouncementUpdateView.as_view(), name="announcement_update"),
    path("<int:pk>/delete/", views.AnnouncementDeleteView.as_view(), name="announcement_delete"),

    path("minutes/", views.minute_list, name="minutes"),
    path("minutes/add/", views.MinuteCreateView.as_view(), name="minute_create"),
    path("minutes/<int:pk>/", views.MinuteDetailView.as_view(), name="minute_detail"),
    path("minutes/<int:pk>/edit/", views.MinuteUpdateView.as_view(), name="minute_update"),
    path("minutes/<int:pk>/delete/", views.MinuteDeleteView.as_view(), name="minute_delete"),
    path("minutes/<int:pk>/summarize/", views.summarize_minute, name="minute_summarize"),
]
