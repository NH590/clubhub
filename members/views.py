from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from accounts.mixins import RoleRequiredMixin
from comms.models import Announcement
from .forms import DepartmentForm, MembershipForm
from .models import Department, Membership


# ---------- DANH SÁCH ----------
@login_required
def member_list(request):
    q = request.GET.get("q", "").strip()
    dept_id = request.GET.get("department", "")

    memberships = Membership.objects.select_related("user", "department")
    if q:
        memberships = memberships.filter(
            Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(user__username__icontains=q)
            | Q(user__mssv__icontains=q)
        )
    if dept_id.isdigit():
        memberships = memberships.filter(department_id=dept_id)

    return render(request, "members/member_list.html", {
        "memberships": memberships,
        "departments": Department.objects.all(),
        "q": q,
        "dept_id": dept_id,
    })


@login_required
def department_list(request):
    counts = dict(
        Membership.objects.values_list("department").annotate(n=Count("id"))
    )
    departments = list(Department.objects.all())
    for d in departments:
        d.member_count = counts.get(d.id, 0)
    return render(request, "members/department_list.html", {"departments": departments})


# ---------- BAN ----------
class DepartmentDetailView(LoginRequiredMixin, DetailView):
    model = Department
    template_name = "members/department_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["memberships"] = (
            Membership.objects.filter(department=self.object).select_related("user")
        )
        return ctx


class DepartmentCreateView(RoleRequiredMixin, SuccessMessageMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = "members/form.html"
    success_url = reverse_lazy("members:departments")
    success_message = "Đã tạo ban mới."
    extra_context = {"title": "Thêm ban"}


class DepartmentUpdateView(RoleRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = "members/form.html"
    success_url = reverse_lazy("members:departments")
    success_message = "Đã cập nhật ban."
    extra_context = {"title": "Sửa ban"}


class DepartmentDeleteView(RoleRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Department
    template_name = "members/confirm_delete.html"
    success_url = reverse_lazy("members:departments")
    success_message = "Đã xóa ban."


# ---------- THÀNH VIÊN TRONG BAN ----------
class MembershipCreateView(RoleRequiredMixin, CreateView):
    model = Membership
    form_class = MembershipForm
    template_name = "members/form.html"
    success_url = reverse_lazy("members:list")
    extra_context = {"title": "Thêm thành viên"}

    def form_valid(self, form):
        response = super().form_valid(form)          # 1. lưu thành viên vào ban
        m = self.object
        name = m.user.get_full_name() or m.user.username
        dept = m.department.name
        pos = m.get_position_display() if hasattr(m, "get_position_display") else m.position

        # 2. Tự đăng thông báo chào mừng vào Truyền thông, gửi riêng cho ban đó
        Announcement.objects.create(
            title=f"Chào mừng {name} gia nhập ban {dept}",
            content=(f"Ban {dept} chào đón thành viên mới {name}"
                     f"{' – chức vụ: ' + str(pos) if pos else ''}. "
                     f"Mọi người cùng hỗ trợ bạn ấy nhé!"),
            department=m.department,
            created_by=self.request.user,
        )

        # 3. Hiện hộp thông báo xanh trên màn hình
        messages.success(self.request,
                         f"Đã thêm {name} vào ban {dept} và đăng thông báo chào mừng.")
        return response


class MembershipUpdateView(RoleRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Membership
    form_class = MembershipForm
    template_name = "members/form.html"
    success_url = reverse_lazy("members:list")
    success_message = "Đã cập nhật thành viên."
    extra_context = {"title": "Sửa thành viên"}


class MembershipDeleteView(RoleRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Membership
    template_name = "members/confirm_delete.html"
    success_url = reverse_lazy("members:list")
    success_message = "Đã xóa thành viên khỏi ban."


# ---------- HỒ SƠ THÀNH VIÊN ----------
@login_required
def member_profile(request, pk):
    """Xem thông tin cá nhân của một thành viên."""
    person = get_object_or_404(get_user_model(), pk=pk)
    memberships = (Membership.objects.filter(user=person)
                   .select_related("department")
                   .order_by("-joined_at"))
    return render(request, "members/profile.html", {
        "person": person,
        "memberships": memberships,
        "is_me": person == request.user,
    })


@login_required
def my_profile(request):
    """Nút 'Hồ sơ của tôi' → mở hồ sơ của chính mình."""
    return redirect("members:profile", pk=request.user.pk)