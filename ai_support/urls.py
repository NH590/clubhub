from django.urls import path

from . import views

app_name = "ai"

urlpatterns = [
    path("", views.hub, name="hub"),
    path("draft/", views.draft_announcement, name="draft"),
    path("suggest/", views.suggest_assignment, name="suggest"),
    path("engagement/", views.engagement, name="engagement"),
]
