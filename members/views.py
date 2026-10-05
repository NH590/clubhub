from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from accounts.mixins import RoleRequiredMixin
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
class MembershipCreateView(RoleRequiredMixin, SuccessMessageMixin, CreateView):
    model = Membership
    form_class = MembershipForm
    template_name = "members/form.html"
    success_url = reverse_lazy("members:list")
    success_message = "Đã thêm thành viên vào ban."
    extra_context = {"title": "Thêm thành viên"}


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