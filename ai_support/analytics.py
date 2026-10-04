"""Tính toán dữ liệu thật bằng code (không để AI đoán số)."""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone

from members.models import Membership


def _departments_by_user():
    result = {}
    for m in Membership.objects.select_related("department"):
        result.setdefault(m.user_id, []).append(str(m.department))
    return result


def build_candidates(department=None, limit=30):
    User = get_user_model()
    users = (User.objects.filter(is_active=True)
             .annotate(open_tasks=Count("assigned_tasks", filter=~Q(assigned_tasks__status="done"), distinct=True),
                       done_tasks=Count("assigned_tasks", filter=Q(assigned_tasks__status="done"), distinct=True)))
    depts = _departments_by_user()
    rows = []
    for u in users:
        user_depts = depts.get(u.id, [])
        rows.append({
            "name": str(u),
            "role": u.get_role_display(),
            "departments": ", ".join(user_depts),
            "same_department": bool(department and str(department) in user_depts),
            "open_tasks": u.open_tasks,
            "done_tasks": u.done_tasks,
        })
    # Ưu tiên người cùng ban, rồi người ít việc
    rows.sort(key=lambda r: (not r["same_department"], r["open_tasks"]))
    return rows[:limit]


def compute_engagement(days=90):
    User = get_user_model()
    now = timezone.now()
    since = now - timedelta(days=days)
    users = User.objects.filter(is_active=True).annotate(
        registered=Count("event_registrations",
                         filter=Q(event_registrations__registered_at__gte=since), distinct=True),
        attended=Count("event_registrations",
                       filter=Q(event_registrations__checked_in_at__gte=since), distinct=True),
        done=Count("assigned_tasks",
                   filter=Q(assigned_tasks__status="done", assigned_tasks__completed_at__gte=since),
                   distinct=True),
        meetings=Count("meetings_attended",
                       filter=Q(meetings_attended__date__gte=since.date()), distinct=True),
    )
    depts = _departments_by_user()
    rows = []
    for u in users:
        score = u.attended * 3 + u.done * 3 + u.meetings * 2 + u.registered
        if u.last_login and u.last_login >= since:
            score += 1
        level = "low" if score < 3 else ("medium" if score < 8 else "high")
        rows.append({
            "name": str(u),
            "departments": ", ".join(depts.get(u.id, [])),
            "registered": u.registered,
            "attended": u.attended,
            "done": u.done,
            "meetings": u.meetings,
            "days_inactive": (now - u.last_login).days if u.last_login else None,
            "score": score,
            "level": level,
        })
    rows.sort(key=lambda r: r["score"])
    return rows
