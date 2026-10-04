from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, UpdateView

from accounts.mixins import RoleRequiredMixin
from members.models import Department
from .forms import TaskForm
from .models import Task

MANAGERS = ("admin", "board", "head")  # tạo / sửa / xóa / giao việc


def is_manager(user):
    return user.is_superuser or getattr(user, "role", None) in MANAGERS


@login_required
def task_board(request):
    tasks = Task.objects.select_related("assignee", "department", "event")

    mine = request.GET.get("mine") == "1"
    dept = request.GET.get("department", "")
    assignee = request.GET.get("assignee", "")
    if mine:
        tasks = tasks.filter(assignee=request.user)
    if dept.isdigit():
        tasks = tasks.filter(department_id=dept)
    if assignee.isdigit():
        tasks = tasks.filter(assignee_id=assignee)

    columns = []
    for value, label in Task.Status.choices:
        columns.append({
            "value": value,
            "label": label,
            "tasks": [t for t in tasks if t.status == value],
        })

    return render(request, "tasks/task_board.html", {
        "columns": columns,
        "departments": Department.objects.all(),
        "users": get_user_model().objects.filter(is_active=True).order_by("first_name", "username"),
        "mine": mine, "dept": dept, "assignee": assignee,
        "can_manage": is_manager(request.user),
        "query": request.GET.urlencode(),
    })


class TaskCreateView(RoleRequiredMixin, SuccessMessageMixin, CreateView):
    allowed_roles = MANAGERS
    model = Task
    form_class = TaskForm
    template_name = "members/form.html"
    success_url = reverse_lazy("tasks:board")
    success_message = "Đã tạo công việc."
    extra_context = {"title": "Tạo công việc"}

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class TaskUpdateView(RoleRequiredMixin, SuccessMessageMixin, UpdateView):
    allowed_roles = MANAGERS
    model = Task
    form_class = TaskForm
    template_name = "members/form.html"
    success_url = reverse_lazy("tasks:board")
    success_message = "Đã cập nhật công việc."
    extra_context = {"title": "Sửa công việc"}


class TaskDeleteView(RoleRequiredMixin, SuccessMessageMixin, DeleteView):
    allowed_roles = MANAGERS
    model = Task
    template_name = "members/confirm_delete.html"
    success_url = reverse_lazy("tasks:board")
    success_message = "Đã xóa công việc."


@login_required
@require_POST
def change_status(request, pk, status):
    """Người phụ trách hoặc quản lý chuyển cột (Cần làm / Đang làm / Hoàn thành)."""
    task = get_object_or_404(Task, pk=pk)
    if status not in Task.Status.values:
        raise Http404
    if not (is_manager(request.user) or task.assignee_id == request.user.id):
        raise PermissionDenied
    task.set_status(status)
    messages.success(request, f"“{task.title}” → {task.get_status_display()}")
    back = request.POST.get("query", "")
    url = reverse_lazy("tasks:board")
    return redirect(f"{url}?{back}" if back else url)
