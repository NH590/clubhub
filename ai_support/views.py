from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.decorators import role_required
from . import services as ai
from .analytics import build_candidates, compute_engagement
from .forms import DraftAnnouncementForm, SuggestAssignmentForm

MANAGERS = ("admin", "board", "head")
DRAFT_KEY = "ai_announcement_draft"


@role_required(*MANAGERS)
def hub(request):
    return render(request, "ai_support/hub.html", {"ai_enabled": ai.is_enabled()})


@role_required(*MANAGERS)
def draft_announcement(request):
    form = DraftAnnouncementForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            title, content = ai.draft_announcement(
                event=form.cleaned_data["event"],
                key_points=form.cleaned_data["key_points"],
                tone=form.cleaned_data["tone"],
            )
            draft = {"title": title, "content": content}
            if form.cleaned_data["event"]:
                draft["event"] = form.cleaned_data["event"].pk
            request.session[DRAFT_KEY] = draft
            messages.info(request, "AI đã viết nháp. Hãy đọc lại, chỉnh sửa rồi bấm Lưu để đăng.")
            return redirect("comms:announcement_create")
        except ai.AIError as e:
            messages.error(request, str(e))
    return render(request, "ai_support/form_page.html", {
        "form": form, "ai_enabled": ai.is_enabled(),
        "title": "AI viết nháp thông báo",
        "intro": "Chọn sự kiện hoặc nhập vài ý chính, AI sẽ viết bản nháp. Bạn luôn được chỉnh sửa trước khi đăng.",
        "button": "Viết nháp",
    })


@role_required(*MANAGERS)
def suggest_assignment(request):
    form = SuggestAssignmentForm(request.POST or None)
    result, candidates = None, None
    if request.method == "POST" and form.is_valid():
        dept = form.cleaned_data["department"]
        candidates = build_candidates(department=dept)
        try:
            result = ai.suggest_assignment(form.cleaned_data["title"],
                                           form.cleaned_data["description"], dept, candidates)
        except ai.AIError as e:
            messages.error(request, str(e))
    return render(request, "ai_support/suggest.html", {
        "form": form, "result": result, "candidates": candidates, "ai_enabled": ai.is_enabled(),
    })


@role_required(*MANAGERS)
def engagement(request):
    days = 90
    rows = compute_engagement(days)
    analysis = None
    if request.method == "POST":
        try:
            analysis = ai.analyze_engagement(rows, days)
        except ai.AIError as e:
            messages.error(request, str(e))
    return render(request, "ai_support/engagement.html", {
        "rows": rows, "days": days, "analysis": analysis, "ai_enabled": ai.is_enabled(),
        "low_count": sum(1 for r in rows if r["level"] == "low"),
    })
