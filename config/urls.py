from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),  # login, logout, doi mat khau
    path("members/", include("members.urls")),
    path("events/", include("events.urls")),
    path("finance/", include("finance.urls")),
    path("tasks/", include("tasks.urls")),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
