"""
Toàn bộ phần gọi AI nằm ở file này.
Muốn đổi sang Claude/OpenAI chỉ cần viết lại hàm ask().
"""
import os
import re
import time

from django.utils import timezone

SYSTEM = (
    "Bạn là trợ lý vận hành cho một câu lạc bộ sinh viên ở Việt Nam. "
    "Luôn trả lời bằng tiếng Việt, ngắn gọn, rõ ràng, thân thiện. "
    "Chỉ dựa trên dữ liệu được cung cấp, không bịa thêm thông tin. "
    "Không dùng định dạng markdown như ** hay #; dùng gạch đầu dòng '-' khi liệt kê."
)

# Model dự phòng khi model chính quá tải / không dùng được
FALLBACK_MODELS = ["gemini-flash-latest", "gemini-flash-lite-latest"]
RETRY_CODES = ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "500", "INTERNAL")


class AIError(Exception):
    pass


def is_enabled():
    return bool(os.getenv("GEMINI_API_KEY"))


def _model_list():
    # GEMINI_MODEL có thể ghi nhiều model, cách nhau bằng dấu phẩy
    configured = [m.strip() for m in os.getenv("GEMINI_MODEL", "").split(",") if m.strip()]
    models = configured + [m for m in FALLBACK_MODELS if m not in configured]
    return models


def ask(prompt, system=SYSTEM):
    if not is_enabled():
        raise AIError("Chưa cấu hình GEMINI_API_KEY nên chưa dùng được tính năng AI.")
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise AIError("Chưa cài thư viện google-genai (pip install google-genai).")

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    config = types.GenerateContentConfig(system_instruction=system, temperature=0.6)

    errors = []
    for model in _model_list():
        for attempt in range(3):  # thử lại tối đa 3 lần nếu quá tải
            try:
                resp = client.models.generate_content(model=model, contents=prompt, config=config)
                text = (resp.text or "").strip()
                if text:
                    return text.replace("**", "")
                break
            except Exception as e:
                msg = str(e)
                errors.append(f"{model}: {msg[:120]}")
                if any(code in msg for code in RETRY_CODES) and attempt < 2:
                    time.sleep(2 * (attempt + 1))  # đợi 2s rồi 4s
                    continue
                break  # lỗi khác (vd 404) -> chuyển sang model tiếp theo

    joined = " | ".join(errors)
    if "503" in joined or "UNAVAILABLE" in joined:
        raise AIError("Máy chủ Gemini đang quá tải, bạn thử lại sau ít phút nhé.")
    if "429" in joined or "RESOURCE_EXHAUSTED" in joined:
        raise AIError("Đã hết lượt miễn phí của Gemini trong lúc này, hãy thử lại sau.")
    raise AIError(f"Không gọi được AI. Chi tiết: {errors[-1] if errors else 'không có phản hồi'}")


# ---------- 1. Viết nháp thông báo ----------
def draft_announcement(event=None, key_points="", tone="thân thiện"):
    info = []
    if event:
        start = timezone.localtime(event.start_time)  # đổi sang giờ Việt Nam
        end = timezone.localtime(event.end_time)
        info.append(f"Tên sự kiện: {event.title}")
        info.append(f"Thời gian: {start:%H:%M %d/%m/%Y} đến {end:%H:%M %d/%m/%Y}")
        info.append(f"Địa điểm: {event.location}")
        if event.capacity:
            info.append(f"Số lượng tối đa: {event.capacity} người")
        if event.description:
            info.append(f"Mô tả: {event.description}")
    if key_points:
        info.append(f"Ý chính cần truyền tải: {key_points}")

    prompt = (
        f"Viết một thông báo gửi thành viên CLB với giọng văn {tone}.\n"
        "Thông tin:\n" + "\n".join(info) + "\n\n"
        "Yêu cầu: khoảng 120-200 từ, có lời kêu gọi đăng ký/tham gia ở cuối.\n"
        "Trả lời ĐÚNG định dạng sau:\n"
        "TIÊU ĐỀ: <một dòng tiêu đề>\n"
        "NỘI DUNG:\n<nội dung thông báo>"
    )
    text = ask(prompt)
    title_match = re.search(r"TIÊU ĐỀ:\s*(.+)", text)
    content_match = re.search(r"NỘI DUNG:\s*(.*)", text, re.S)
    title = title_match.group(1).strip() if title_match else (event.title if event else "Thông báo")
    content = content_match.group(1).strip() if content_match else text
    return title[:200], content


# ---------- 2. Tóm tắt biên bản họp ----------
def summarize_minutes(minute):
    attendees = ", ".join(str(u) for u in minute.attendees.all()) or "không ghi"
    prompt = (
        f"Tóm tắt biên bản cuộc họp sau.\n"
        f"Cuộc họp: {minute.title} - ngày {minute.date:%d/%m/%Y}\n"
        f"Người tham dự: {attendees}\n"
        f"Ghi chép:\n{minute.raw_notes}\n\n"
        "Trình bày theo 3 phần, mỗi phần có tiêu đề viết hoa:\n"
        "NỘI DUNG CHÍNH: (3-5 gạch đầu dòng)\n"
        "QUYẾT ĐỊNH: (các điều đã thống nhất)\n"
        "VIỆC CẦN LÀM: (mỗi dòng: việc - người phụ trách - hạn, nếu ghi chép có nêu)"
    )
    return ask(prompt)


# ---------- 3. Đề xuất phân công task ----------
def suggest_assignment(title, description, department, candidates):
    lines = []
    for c in candidates:
        lines.append(
            f"- {c['name']} | vai trò: {c['role']} | ban: {c['departments'] or 'chưa vào ban'} "
            f"| đang làm: {c['open_tasks']} việc | đã hoàn thành: {c['done_tasks']} việc"
        )
    prompt = (
        "Cần giao một công việc trong CLB.\n"
        f"Công việc: {title}\n"
        f"Mô tả: {description or 'không có'}\n"
        f"Ban liên quan: {department or 'không chỉ định'}\n\n"
        "Danh sách thành viên có thể giao:\n" + "\n".join(lines) + "\n\n"
        "Hãy đề xuất 2-3 người phù hợp nhất, xếp theo thứ tự ưu tiên. "
        "Với mỗi người nêu lý do ngắn gọn (ưu tiên người cùng ban, có vai trò phù hợp "
        "và đang ít việc). Cuối cùng thêm một dòng lưu ý nếu ai đó đang quá tải."
    )
    return ask(prompt)


# ---------- 4. Phân tích thành viên ít tương tác ----------
def analyze_engagement(rows, days):
    low = [r for r in rows if r["level"] == "low"]
    lines = []
    for r in low[:20]:
        inactive = (f"{r['days_inactive']} ngày chưa đăng nhập"
                    if r["days_inactive"] is not None else "chưa từng đăng nhập")
        lines.append(
            f"- {r['name']} ({r['departments'] or 'chưa vào ban'}): điểm danh {r['attended']} sự kiện, "
            f"hoàn thành {r['done']} việc, dự {r['meetings']} cuộc họp, {inactive}"
        )
    prompt = (
        f"Dưới đây là các thành viên CLB có mức tương tác thấp trong {days} ngày qua:\n"
        + ("\n".join(lines) if lines else "(không có ai)") + "\n\n"
        "Hãy: (1) nhận xét ngắn về tình hình chung; "
        "(2) với từng người, gợi ý 1 cách cụ thể để kết nối lại (ví dụ mời phụ một việc nhỏ hợp ban, "
        "nhắn hỏi thăm, mời sự kiện sắp tới); "
        "(3) viết sẵn một tin nhắn mẫu ngắn, thân thiện để Ban điều hành gửi chung."
    )
    return ask(prompt)