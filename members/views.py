from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render

from .models import Department, Membership


@login_required
def member_list(request):
    q = request.GET.get("q", "").strip()
    dept_id = request.GET.get("department", "")

    memberships = Membership.objects.filter(is_active=True).select_related(
        "user", "department"
    )
    if q:
        memberships = memberships.filter(
            Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(user__username__icontains=q)
            | Q(user__mssv__icontains=q)
        )
    if dept_id:
        memberships = memberships.filter(department_id=dept_id)

    return render(
        request,
        "members/member_list.html",
        {
            "memberships": memberships,
            "departments": Department.objects.all(),
            "q": q,
            "dept_id": dept_id,
        },
    )


@login_required
def department_list(request):
    departments = Department.objects.select_related("head").annotate(
        total=Count("memberships", filter=Q(memberships__is_active=True))
    )
    return render(request, "members/department_list.html", {"departments": departments})