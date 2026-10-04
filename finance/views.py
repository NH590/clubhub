from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, UpdateView

from accounts.mixins import RoleRequiredMixin
from .forms import TransactionForm
from .models import Transaction

MANAGERS = ("admin", "board")            # duyệt, sửa, xóa
PROPOSERS = ("admin", "board", "head")   # được thêm / đề xuất


def role_in(user, roles):
    return user.is_superuser or getattr(user, "role", None) in roles


def _total(qs, type_):
    return qs.filter(type=type_).aggregate(s=Sum("amount"))["s"] or Decimal(0)


@login_required
def transaction_list(request):
    qs = Transaction.objects.select_related("category", "created_by", "event")
    approved = qs.filter(status=Transaction.Status.APPROVED)
    income_total = _total(approved, "income")
    expense_total = _total(approved, "expense")

    # Bộ lọc
    f_type = request.GET.get("type", "")
    f_status = request.GET.get("status", "")
    f_month = request.GET.get("month", "")
    items = qs
    if f_type in ("income", "expense"):
        items = items.filter(type=f_type)
    if f_status in ("pending", "approved", "rejected"):
        items = items.filter(status=f_status)
    if f_month:
        try:
            y, m = map(int, f_month.split("-"))
            items = items.filter(date__year=y, date__month=m)
        except ValueError:
            f_month = ""

    # Thống kê 6 tháng gần nhất (chỉ khoản đã duyệt)
    monthly = []
    rows = (approved.annotate(m=TruncMonth("date")).values("m")
            .annotate(income=Sum("amount", filter=Q(type="income")),
                      expense=Sum("amount", filter=Q(type="expense")))
            .order_by("-m")[:6])
    for r in rows:
        inc, exp = r["income"] or Decimal(0), r["expense"] or Decimal(0)
        monthly.append({"month": r["m"], "income": inc, "expense": exp, "net": inc - exp})

    return render(request, "finance/transaction_list.html", {
        "items": items,
        "income_total": income_total,
        "expense_total": expense_total,
        "balance": income_total - expense_total,
        "pending_count": qs.filter(status="pending").count(),
        "monthly": monthly,
        "f_type": f_type, "f_status": f_status, "f_month": f_month,
        "can_propose": role_in(request.user, PROPOSERS),
        "can_manage": role_in(request.user, MANAGERS),
    })


class TransactionCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = PROPOSERS
    model = Transaction
    form_class = TransactionForm
    template_name = "members/form.html"
    success_url = reverse_lazy("finance:list")
    extra_context = {"title": "Thêm khoản thu / chi"}

    def form_valid(self, form):
        user = self.request.user
        form.instance.created_by = user
        if role_in(user, MANAGERS):
            form.instance.status = Transaction.Status.APPROVED
            form.instance.approved_by = user
            messages.success(self.request, "Đã ghi nhận khoản thu/chi.")
        else:
            form.instance.status = Transaction.Status.PENDING
            messages.info(self.request, "Đã gửi đề xuất, chờ Ban điều hành duyệt.")
        return super().form_valid(form)


class TransactionUpdateView(RoleRequiredMixin, SuccessMessageMixin, UpdateView):
    allowed_roles = MANAGERS
    model = Transaction
    form_class = TransactionForm
    template_name = "members/form.html"
    success_url = reverse_lazy("finance:list")
    success_message = "Đã cập nhật."
    extra_context = {"title": "Sửa khoản thu / chi"}


class TransactionDeleteView(RoleRequiredMixin, SuccessMessageMixin, DeleteView):
    allowed_roles = MANAGERS
    model = Transaction
    template_name = "members/confirm_delete.html"
    success_url = reverse_lazy("finance:list")
    success_message = "Đã xóa."


def _set_status(request, pk, status, text):
    if not role_in(request.user, MANAGERS):
        raise PermissionDenied
    t = get_object_or_404(Transaction, pk=pk)
    t.status = status
    t.approved_by = request.user
    t.save(update_fields=["status", "approved_by"])
    messages.success(request, text)
    return redirect("finance:list")


@login_required
@require_POST
def approve(request, pk):
    return _set_status(request, pk, Transaction.Status.APPROVED, "Đã duyệt.")


@login_required
@require_POST
def reject(request, pk):
    return _set_status(request, pk, Transaction.Status.REJECTED, "Đã từ chối.")
