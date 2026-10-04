from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from reports.views import dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("members/", include("members.urls")),
    path("events/", include("events.urls")),
    path("finance/", include("finance.urls")),
    path("tasks/", include("tasks.urls")),
    path("comms/", include("comms.urls")),
    path("ai/", include("ai_support.urls")),
    path("reports/", include("reports.urls")),
    path("", dashboard, name="home"),  # Trang chủ = Dashboard
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
