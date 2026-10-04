import io

import qrcode
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from accounts.mixins import RoleRequiredMixin
from .forms import EventForm
from .models import Event, Registration

MANAGER_ROLES = ("admin", "board", "head")  # ai được tạo/sửa sự kiện, xem QR


def is_manager(user):
    return user.is_superuser or getattr(user, "role", None) in MANAGER_ROLES


def require_manager(user):
    if not is_manager(user):
        raise PermissionDenied


class EventManagerMixin(RoleRequiredMixin):
    allowed_roles = MANAGER_ROLES


# ---------- DANH SÁCH & CHI TIẾT ----------
@login_required
def event_list(request):
    tab = request.GET.get("tab", "upcoming")
    now = timezone.now()
    events = Event.objects.select_related("department").annotate(n_registered=Count("registrations"))
    if tab == "past":
        events = events.filter(end_time__lt=now).order_by("-start_time")
    else:
        tab = "upcoming"
        events = events.filter(end_time__gte=now).order_by("start_time")

    my_ids = set(
        Registration.objects.filter(user=request.user).values_list("event_id", flat=True)
    )
    return render(request, "events/event_list.html", {
        "events": events, "tab": tab, "my_ids": my_ids,
        "can_manage": is_manager(request.user),
    })


class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["my_registration"] = self.object.registrations.filter(user=user).first()
        ctx["can_manage"] = is_manager(user)
        if ctx["can_manage"]:
            ctx["registrations"] = self.object.registrations.select_related("user")
        return ctx


# ---------- TẠO / SỬA / XÓA ----------
class EventCreateView(EventManagerMixin, SuccessMessageMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = "members/form.html"
    success_message = "Đã tạo sự kiện."
    extra_context = {"title": "Tạo sự kiện"}

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("events:detail", args=[self.object.pk])


class EventUpdateView(EventManagerMixin, SuccessMessageMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = "members/form.html"
    success_message = "Đã cập nhật sự kiện."
    extra_context = {"title": "Sửa sự kiện"}

    def get_success_url(self):
        return reverse("events:detail", args=[self.object.pk])


class EventDeleteView(EventManagerMixin, SuccessMessageMixin, DeleteView):
    model = Event
    template_name = "members/confirm_delete.html"
    success_url = reverse_lazy("events:list")
    success_message = "Đã xóa sự kiện."


# ---------- ĐĂNG KÝ ----------
@login_required
@require_POST
def register(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.status == "past":
        messages.error(request, "Sự kiện đã kết thúc.")
    elif event.is_full:
        messages.error(request, "Sự kiện đã đủ số lượng.")
    else:
        _, created = Registration.objects.get_or_create(event=event, user=request.user)
        if created:
            messages.success(request, "Đăng ký thành công!")
        else:
            messages.info(request, "Bạn đã đăng ký sự kiện này rồi.")
    return redirect("events:detail", pk=pk)


@login_required
@require_POST
def cancel_registration(request, pk):
    reg = Registration.objects.filter(event_id=pk, user=request.user).first()
    if not reg:
        messages.info(request, "Bạn chưa đăng ký sự kiện này.")
    elif reg.checked_in_at:
        messages.error(request, "Bạn đã điểm danh, không thể hủy đăng ký.")
    else:
        reg.delete()
        messages.success(request, "Đã hủy đăng ký.")
    return redirect("events:detail", pk=pk)


# ---------- QR ĐIỂM DANH ----------
def _checkin_url(request, event):
    path = reverse("events:checkin", args=[event.pk, event.checkin_token])
    return request.build_absolute_uri(path)


@login_required
def qr_page(request, pk):
    require_manager(request.user)
    event = get_object_or_404(Event, pk=pk)
    return render(request, "events/event_qr.html", {
        "event": event, "checkin_url": _checkin_url(request, event),
    })


@login_required
def qr_image(request, pk):
    require_manager(request.user)
    event = get_object_or_404(Event, pk=pk)
    img = qrcode.make(_checkin_url(request, event), box_size=10, border=2)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    response = HttpResponse(buf.getvalue(), content_type="image/png")
    response["Cache-Control"] = "no-store"
    return response


@login_required
@require_POST
def regenerate_qr(request, pk):
    require_manager(request.user)
    event = get_object_or_404(Event, pk=pk)
    event.regenerate_token()
    messages.success(request, "Đã đổi mã QR. Mã cũ không còn dùng được.")
    return redirect("events:qr", pk=pk)


@login_required
def checkin(request, pk, token):
    event = get_object_or_404(Event, pk=pk)
    ctx = {"event": event}
    if token != event.checkin_token:
        ctx["error"] = "Mã QR không hợp lệ hoặc đã được đổi. Hãy quét mã mới nhất."
    elif not event.checkin_open:
        ctx["error"] = "Chưa đến giờ điểm danh hoặc sự kiện đã kết thúc."
    else:
        reg, _ = Registration.objects.get_or_create(event=event, user=request.user)
        ctx["already"] = reg.checked_in_at is not None
        if not reg.checked_in_at:
            reg.checked_in_at = timezone.now()
            reg.save(update_fields=["checked_in_at"])
        ctx["ok"] = True
        ctx["registration"] = reg
    return render(request, "events/checkin_result.html", ctx)


@login_required
@require_POST
def toggle_attendance(request, pk, reg_id):
    """Ban điều hành điểm danh tay / bỏ điểm danh."""
    require_manager(request.user)
    reg = get_object_or_404(Registration, pk=reg_id, event_id=pk)
    reg.checked_in_at = None if reg.checked_in_at else timezone.now()
    reg.save(update_fields=["checked_in_at"])
    return redirect("events:detail", pk=pk)