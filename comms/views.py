from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from accounts.mixins import RoleRequiredMixin
from ai_support import services as ai
from .forms import AnnouncementForm, MeetingMinuteForm
from .models import Announcement, MeetingMinute

MANAGERS = ("admin", "board", "head")
DRAFT_KEY = "ai_announcement_draft"


def is_manager(user):
    return user.is_superuser or getattr(user, "role", None) in MANAGERS


# ================= THÔNG BÁO =================
@login_required
def announcement_list(request):
    items = Announcement.objects.select_related("department", "event", "created_by")
    return render(request, "comms/announcement_list.html", {
        "items": items,
        "can_manage": is_manager(request.user),
        "ai_enabled": ai.is_enabled(),
    })


class AnnouncementDetailView(LoginRequiredMixin, DetailView):
    model = Announcement
    template_name = "comms/announcement_detail.html"
    context_object_name = "item"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["can_manage"] = is_manager(self.request.user)
        return ctx


class AnnouncementCreateView(RoleRequiredMixin, SuccessMessageMixin, CreateView):
    allowed_roles = MANAGERS
    model = Announcement
    form_class = AnnouncementForm
    template_name = "members/form.html"
    success_message = "Đã đăng thông báo."
    extra_context = {"title": "Đăng thông báo"}

    def get_initial(self):
        initial = super().get_initial()
        draft = self.request.session.get(DRAFT_KEY)
        if draft:
            initial.update(draft)  # bản nháp do AI viết
        return initial

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        if self.request.session.pop(DRAFT_KEY, None):
            form.instance.ai_generated = True
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("comms:announcement_detail", args=[self.object.pk])


class AnnouncementUpdateView(RoleRequiredMixin, SuccessMessageMixin, UpdateView):
    allowed_roles = MANAGERS
    model = Announcement
    form_class = AnnouncementForm
    template_name = "members/form.html"
    success_message = "Đã cập nhật thông báo."
    extra_context = {"title": "Sửa thông báo"}

    def get_success_url(self):
        return reverse("comms:announcement_detail", args=[self.object.pk])


class AnnouncementDeleteView(RoleRequiredMixin, SuccessMessageMixin, DeleteView):
    allowed_roles = MANAGERS
    model = Announcement
    template_name = "members/confirm_delete.html"
    success_url = reverse_lazy("comms:announcements")
    success_message = "Đã xóa thông báo."


# ================= BIÊN BẢN HỌP =================
@login_required
def minute_list(request):
    items = MeetingMinute.objects.prefetch_related("attendees")
    return render(request, "comms/minute_list.html", {
        "items": items,
        "can_manage": is_manager(request.user),
    })


class MinuteDetailView(LoginRequiredMixin, DetailView):
    model = MeetingMinute
    template_name = "comms/minute_detail.html"
    context_object_name = "item"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["can_manage"] = is_manager(self.request.user)
        ctx["ai_enabled"] = ai.is_enabled()
        return ctx


class MinuteCreateView(RoleRequiredMixin, SuccessMessageMixin, CreateView):
    allowed_roles = MANAGERS
    model = MeetingMinute
    form_class = MeetingMinuteForm
    template_name = "members/form.html"
    success_message = "Đã lưu biên bản."
    extra_context = {"title": "Thêm biên bản họp"}

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("comms:minute_detail", args=[self.object.pk])


class MinuteUpdateView(RoleRequiredMixin, SuccessMessageMixin, UpdateView):
    allowed_roles = MANAGERS
    model = MeetingMinute
    form_class = MeetingMinuteForm
    template_name = "members/form.html"
    success_message = "Đã cập nhật biên bản."
    extra_context = {"title": "Sửa biên bản họp"}

    def get_success_url(self):
        return reverse("comms:minute_detail", args=[self.object.pk])


class MinuteDeleteView(RoleRequiredMixin, SuccessMessageMixin, DeleteView):
    allowed_roles = MANAGERS
    model = MeetingMinute
    template_name = "members/confirm_delete.html"
    success_url = reverse_lazy("comms:minutes")
    success_message = "Đã xóa biên bản."


@login_required
@require_POST
def summarize_minute(request, pk):
    """AI tóm tắt biên bản họp."""
    if not is_manager(request.user):
        raise PermissionDenied
    minute = get_object_or_404(MeetingMinute, pk=pk)
    try:
        minute.summary = ai.summarize_minutes(minute)
        minute.ai_summarized_at = timezone.now()
        minute.save(update_fields=["summary", "ai_summarized_at"])
        messages.success(request, "AI đã tóm tắt biên bản. Hãy đọc lại và chỉnh sửa nếu cần.")
    except ai.AIError as e:
        messages.error(request, str(e))
    return redirect("comms:minute_detail", pk=pk)
