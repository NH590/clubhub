"""
Tạo dữ liệu demo cho ClubHub (~50 thành viên).

    python manage.py seed_demo          # tạo dữ liệu demo
    python manage.py seed_demo --reset  # xóa dữ liệu demo cũ rồi tạo lại
    python manage.py seed_demo --clear  # chỉ xóa dữ liệu demo

Mọi tài khoản demo có username bắt đầu bằng "demo_", mật khẩu chung: Demo@12345
Dữ liệu thật (tài khoản, ban... bạn tự tạo) KHÔNG bị xóa.
"""
import random
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import models, transaction
from django.utils import timezone

from comms.models import Announcement, MeetingMinute
from events.models import Event, Registration
from finance.models import Category, Transaction
from members.models import Department, Membership
from tasks.models import Task

PREFIX = "demo_"
PASSWORD = "Demo@12345"
N_USERS = 50

HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng",
      "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
DEM_NAM = ["Văn", "Minh", "Đức", "Quốc", "Gia", "Hoàng", "Thành", "Tuấn", "Anh", "Hữu"]
DEM_NU = ["Thị", "Ngọc", "Thu", "Thanh", "Phương", "Khánh", "Bảo", "Mai", "Hoài", "Diệu"]
TEN_NAM = ["An", "Bảo", "Cường", "Dũng", "Duy", "Đạt", "Huy", "Khang", "Khoa", "Long",
           "Nam", "Phát", "Phúc", "Quân", "Sơn", "Tài", "Thắng", "Trí", "Tùng", "Vinh"]
TEN_NU = ["Anh", "Chi", "Giang", "Hà", "Hân", "Hương", "Lan", "Linh", "My", "Ngân",
          "Nhi", "Như", "Quyên", "Tâm", "Thảo", "Trang", "Uyên", "Vy", "Yến", "Xuân"]
KHOA = ["CNTT", "CNTT", "Ngôn ngữ Anh", "Quản trị kinh doanh", "Kế toán", "Marketing",
        "Thiết kế đồ họa"]
NO_ACCENT = str.maketrans(
    "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ",
    "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd")

DEPARTMENTS = ["Truyền Thông", "Sự Kiện", "Hậu Đài", "Biên Tập", "Học Thuật", "Đối Ngoại"]

EVENTS_PAST = [
    ("Workshop Git & GitHub cho người mới", "Phòng A101", 40, "Học Thuật"),
    ("Ngày hội chào tân thành viên", "Sân trường", 80, "Sự Kiện"),
    ("Talkshow: Định hướng nghề nghiệp IT", "Hội trường B", 100, "Đối Ngoại"),
    ("Chiến dịch Mùa hè xanh - họp xuất quân", "Phòng B203", 50, "Hậu Đài"),
    ("Cuộc thi thiết kế poster", "Online", 60, "Truyền Thông"),
    ("Workshop Python cơ bản", "Phòng A101", 40, "Học Thuật"),
    ("Giao lưu bóng đá giữa các CLB", "Sân bóng KTX", 30, "Sự Kiện"),
    ("Đêm nhạc gây quỹ từ thiện", "Hội trường A", 120, "Hậu Đài"),
]
EVENTS_UPCOMING = [
    ("Workshop Django & Deploy web", "Phòng A101", 40, "Học Thuật"),
    ("Hội thao CLB mùa thu", "Nhà thi đấu", 60, "Sự Kiện"),
    ("Tọa đàm: Kỹ năng thuyết trình", "Hội trường B", 80, "Đối Ngoại"),
]
TASK_TITLES = [
    ("Thiết kế poster workshop Django", "Truyền Thông"), ("Viết bài đăng fanpage tuần này", "Truyền Thông"),
    ("Quay video recap hội thao", "Truyền Thông"), ("Chụp ảnh sự kiện tọa đàm", "Truyền Thông"),
    ("Đặt phòng A101", "Hậu Đài"), ("Mua nước uống và bánh", "Hậu Đài"),
    ("Chuẩn bị âm thanh, máy chiếu", "Hậu Đài"), ("Kiểm kê vật dụng CLB", "Hậu Đài"),
    ("Lên kịch bản chương trình hội thao", "Sự Kiện"), ("Liên hệ trọng tài", "Sự Kiện"),
    ("Lập danh sách đội thi đấu", "Sự Kiện"), ("Chuẩn bị quà tặng", "Sự Kiện"),
    ("Biên tập bản tin tháng", "Biên Tập"), ("Soát lỗi bài viết tuyển thành viên", "Biên Tập"),
    ("Viết biên bản họp tổng kết", "Biên Tập"), ("Soạn slide workshop Django", "Học Thuật"),
    ("Chuẩn bị bài tập thực hành", "Học Thuật"), ("Tìm diễn giả cho tọa đàm", "Đối Ngoại"),
    ("Gửi thư mời nhà tài trợ", "Đối Ngoại"), ("Liên hệ CLB bạn giao lưu", "Đối Ngoại"),
    ("Cập nhật danh sách thành viên", "Biên Tập"), ("Tổng hợp phản hồi sau sự kiện", "Học Thuật"),
    ("Thiết kế banner hội thao", "Truyền Thông"), ("Mượn bàn ghế từ khoa", "Hậu Đài"),
    ("Dựng sân khấu đêm nhạc", "Hậu Đài"), ("Lập dự trù kinh phí quý IV", "Sự Kiện"),
]
MINUTES = [
    ("Họp ban điều hành tháng 7",
     "Tổng kết hoạt động tháng 6, số thành viên tham gia sự kiện tăng.\n"
     "Ban Truyền Thông đề xuất đăng bài đều đặn 3 bài mỗi tuần.\n"
     "Thống nhất tổ chức Mùa hè xanh, Ban Hậu Đài lo vật dụng.\n"
     "Kinh phí dự kiến 3 triệu, xin tài trợ thêm từ cựu thành viên."),
    ("Họp chuẩn bị Ngày hội chào tân thành viên",
     "Dự kiến 80 người tham gia, tổ chức tại sân trường.\n"
     "Ban Sự Kiện lên kịch bản, hạn nộp trước 1 tuần.\n"
     "Ban Truyền Thông làm poster và video giới thiệu CLB.\n"
     "Cần mượn loa và bàn ghế của khoa, Ban Hậu Đài phụ trách."),
    ("Họp tổng kết quý III",
     "Đã tổ chức 6 sự kiện, tỉ lệ điểm danh trung bình khoảng 75%.\n"
     "Quỹ còn dư, đề xuất trích một phần cho đêm nhạc gây quỹ.\n"
     "Một số thành viên ít tham gia, cần có kế hoạch kết nối lại.\n"
     "Thống nhất áp dụng điểm danh QR cho mọi sự kiện."),
    ("Họp chuẩn bị Workshop Django",
     "Workshop tổ chức tại phòng A101, giới hạn 40 người.\n"
     "Ban Học Thuật soạn slide và bài tập, hạn thứ 6 tuần sau.\n"
     "Ban Truyền Thông đăng thông báo và mở đăng ký trên ClubHub.\n"
     "Chi phí nước uống khoảng 400 nghìn."),
]


def at(days_ago, hour=0, minute=0):
    """Thời điểm (có múi giờ VN) cách hôm nay `days_ago` ngày."""
    d = timezone.localdate() - timedelta(days=days_ago)
    return timezone.make_aware(datetime.combine(d, time(hour, minute)))


class Command(BaseCommand):
    help = "Tạo dữ liệu demo (~50 thành viên, sự kiện, quỹ, công việc, truyền thông)."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Xóa dữ liệu demo cũ rồi tạo lại")
        parser.add_argument("--clear", action="store_true", help="Chỉ xóa dữ liệu demo")

    # ------------------------------------------------------------------
    def handle(self, *args, **opts):
        User = get_user_model()
        has_demo = User.objects.filter(username__startswith=PREFIX).exists()

        if opts["clear"] or opts["reset"]:
            self.clear()
            if opts["clear"]:
                return
        elif has_demo:
            self.stdout.write(self.style.WARNING(
                "Đã có dữ liệu demo. Dùng --reset để tạo lại hoặc --clear để xóa."))
            return

        random.seed(2026)
        with transaction.atomic():
            self.seed()
        self.stdout.write(self.style.SUCCESS(
            f"Xong! Tài khoản demo: demo_... / mật khẩu: {PASSWORD}"))

    # ------------------------------------------------------------------
    def clear(self):
        User = get_user_model()
        demo = User.objects.filter(username__startswith=PREFIX)
        with transaction.atomic():
            n_events = Event.objects.filter(created_by__in=demo).delete()[0]
            Transaction.objects.filter(created_by__in=demo).delete()
            Task.objects.filter(created_by__in=demo).delete()
            Announcement.objects.filter(created_by__in=demo).delete()
            MeetingMinute.objects.filter(created_by__in=demo).delete()
            n_users = demo.count()
            demo.delete()
        self.stdout.write(self.style.SUCCESS(f"Đã xóa {n_users} tài khoản demo và dữ liệu liên quan."))

    # ------------------------------------------------------------------
    def seed(self):
        self.users = self.make_users()
        self.depts = self.make_departments()
        self.make_memberships()
        past, upcoming = self.make_events()
        self.make_finance(past)
        self.make_tasks(past + upcoming)
        self.make_comms(upcoming)
        self.stdout.write(f"  - {len(self.users)} thành viên, {len(self.depts)} ban, "
                          f"{len(past) + len(upcoming)} sự kiện")

    # ---------- Thành viên ----------
    def make_users(self):
        User = get_user_model()
        role_field = {c[0] for c in User._meta.get_field("role").choices}
        pw = make_password(PASSWORD)  # băm 1 lần, dùng chung cho nhanh
        used, users = set(), []
        for i in range(N_USERS):
            female = random.random() < 0.55
            while True:
                ho = random.choice(HO)
                dem = random.choice(DEM_NU if female else DEM_NAM)
                ten = random.choice(TEN_NU if female else TEN_NAM)
                if (ho, dem, ten) not in used:
                    used.add((ho, dem, ten))
                    break
            slug = f"{ten}{ho[0]}{dem[0]}".lower().translate(NO_ACCENT)
            username = f"{PREFIX}{slug}{i + 1:02d}"

            # mức độ hoạt động: quyết định đăng ký, điểm danh, đăng nhập...
            activity = random.choices(["high", "medium", "low"], weights=[30, 40, 30])[0]
            if i < 4:
                role, activity = "board", "high"
            elif i < 10:
                role = "head"
                activity = "high" if activity == "low" else activity
            else:
                role = "member"
            if role not in role_field:
                role = "member"

            last_login = {
                "high": at(random.randint(0, 6), random.randint(7, 22)),
                "medium": at(random.randint(7, 40), random.randint(7, 22)),
                "low": at(random.randint(60, 150), random.randint(7, 22)) if random.random() < 0.7 else None,
            }[activity]

            u = User(username=username, first_name=ten, last_name=f"{ho} {dem}",
                     email=f"{username.replace(PREFIX, '')}@student.edu.vn",
                     password=pw, role=role, is_active=True,
                     mssv=f"24315{41000 + i:05d}", faculty=random.choice(KHOA),
                     phone=f"09{random.randint(10000000, 99999999)}",
                     last_login=last_login,
                     date_joined=at(random.randint(120, 400)))
            u.activity = activity
            users.append(u)
        User.objects.bulk_create(users)
        created = list(User.objects.filter(username__startswith=PREFIX).order_by("username"))
        by_name = {u.username: u for u in users}
        for u in created:
            u.activity = by_name[u.username].activity
        return created

    # ---------- Ban ----------
    def make_departments(self):
        fields = {f.name for f in Department._meta.get_fields()}
        depts = {}
        for name in DEPARTMENTS:
            d = Department.objects.filter(name__iexact=name).first()
            if not d:
                kwargs = {"name": name}
                if "description" in fields:
                    kwargs["description"] = f"Ban {name} của CLB"
                d = Department.objects.create(**kwargs)
            depts[name] = d
        return depts

    def make_memberships(self):
        fields = {f.name: f for f in Membership._meta.get_fields()}
        dept_fields = {f.name: f for f in Department._meta.get_fields()}
        head_label = member_label = None
        if "position" in fields and fields["position"].choices:
            choices = list(fields["position"].choices)
            head_label = next((v for v, l in choices if "trưởng" in str(l).lower()), choices[0][0])
            member_label = next((v for v, l in choices if "thành viên" in str(l).lower()), choices[-1][0])

        names = list(self.depts)
        heads = [u for u in self.users if u.role == "head"]
        self.user_depts = {}
        for idx, u in enumerate(self.users):
            if u.role == "head":
                dname = names[heads.index(u) % len(names)]
            else:
                dname = names[idx % len(names)]
            dept = self.depts[dname]
            kwargs = {}
            if head_label is not None:
                kwargs["position"] = head_label if u.role == "head" else member_label
            m, _ = Membership.objects.get_or_create(user=u, department=dept, defaults=kwargs)
            self.user_depts[u.id] = dname

            if "joined_at" in fields and getattr(fields["joined_at"], "concrete", False):
                f = fields["joined_at"]
                value = at(random.randint(30, 300))
                if not isinstance(f, models.DateTimeField):
                    value = value.date()
                Membership.objects.filter(pk=m.pk).update(joined_at=value)

            # gán trưởng ban nếu ban chưa có
            if u.role == "head" and "head" in dept_fields and getattr(dept_fields["head"], "concrete", False):
                if getattr(dept, "head_id", None) is None:
                    dept.head = u
                    dept.save(update_fields=["head"])

    # ---------- Sự kiện ----------
    def make_events(self):
        board = [u for u in self.users if u.role == "board"]
        prob_reg = {"high": 0.75, "medium": 0.4, "low": 0.08}
        prob_att = {"high": 0.9, "medium": 0.7, "low": 0.4}
        past, upcoming = [], []

        # 8 sự kiện trong ~5 tháng qua
        for k, (title, place, cap, dname) in enumerate(EVENTS_PAST):
            days_ago = 150 - k * 18 - random.randint(0, 5)
            start = at(days_ago, random.choice([8, 14, 18]))
            ev = Event.objects.create(
                title=title, location=place, capacity=cap,
                description=f"{title} do Ban {dname} phụ trách. Mời các thành viên tham gia!",
                start_time=start, end_time=start + timedelta(hours=3),
                department=self.depts[dname], created_by=random.choice(board))
            past.append(ev)
            regs = [u for u in self.users if random.random() < prob_reg[u.activity]][:cap]
            for u in regs:
                checked = start + timedelta(minutes=random.randint(-20, 40)) \
                    if random.random() < prob_att[u.activity] else None
                r = Registration.objects.create(event=ev, user=u, checked_in_at=checked)
                Registration.objects.filter(pk=r.pk).update(
                    registered_at=start - timedelta(days=random.randint(1, 10), hours=random.randint(0, 12)))

        # 3 sự kiện sắp tới
        for k, (title, place, cap, dname) in enumerate(EVENTS_UPCOMING):
            start = at(-(5 + k * 7), random.choice([14, 18]))
            ev = Event.objects.create(
                title=title, location=place, capacity=cap,
                description=f"{title} do Ban {dname} phụ trách. Đăng ký sớm để giữ chỗ!",
                start_time=start, end_time=start + timedelta(hours=3),
                department=self.depts[dname], created_by=random.choice(board))
            upcoming.append(ev)
            for u in [u for u in self.users if random.random() < prob_reg[u.activity] * 0.6][:cap]:
                Registration.objects.create(event=ev, user=u)
        return past, upcoming

    # ---------- Quỹ ----------
    def make_finance(self, past_events):
        board = [u for u in self.users if u.role == "board"]
        heads = [u for u in self.users if u.role == "head"]

        def cat(name, type_):
            return Category.objects.get_or_create(name=name, type=type_)[0]

        dues, sponsor = cat("Quỹ thành viên", "income"), cat("Tài trợ", "income")
        logistics, printing = cat("Hậu cần sự kiện", "expense"), cat("In ấn", "expense")
        stationery = cat("Văn phòng phẩm", "expense")

        rows = []
        today = timezone.localdate()
        for m in range(6):  # 6 tháng gần nhất
            d = (today.replace(day=1) - timedelta(days=30 * m)).replace(day=random.randint(3, 8))
            if d > today:
                d = today
            payers = random.randint(30, 45)
            rows.append(dict(type="income", category=dues, amount=payers * 50000,
                             description=f"Thu quỹ thành viên tháng {d.month:02d}/{d.year} ({payers} bạn)",
                             date=d))
            if m in (1, 4):
                rows.append(dict(type="income", category=sponsor,
                                 amount=random.choice([2000000, 3000000, 5000000]),
                                 description="Tài trợ từ doanh nghiệp đối tác", date=min(d + timedelta(days=5), today)))
            rows.append(dict(type="expense", category=stationery, amount=random.randint(2, 6) * 50000,
                             description="Mua văn phòng phẩm", date=min(d + timedelta(days=10), today)))

        for ev in past_events:
            d = timezone.localtime(ev.start_time).date()
            rows.append(dict(type="expense", category=logistics, amount=random.randint(6, 20) * 100000,
                             description=f"Nước uống, hậu cần - {ev.title}", date=d, event=ev))
            rows.append(dict(type="expense", category=printing, amount=random.randint(2, 6) * 50000,
                             description=f"In poster, banner - {ev.title}", date=d - timedelta(days=5), event=ev))

        for r in rows:
            approver = random.choice(board)
            Transaction.objects.create(status="approved", created_by=approver, approved_by=approver,
                                       amount=Decimal(r.pop("amount")), **r)

        # vài khoản chờ duyệt / bị từ chối để demo luồng duyệt
        Transaction.objects.create(type="expense", category=logistics, amount=Decimal(450000),
                                   description="Đề xuất mua nước cho Workshop Django", date=today,
                                   status="pending", created_by=random.choice(heads))
        Transaction.objects.create(type="expense", category=printing, amount=Decimal(300000),
                                   description="Đề xuất in banner Hội thao", date=today,
                                   status="pending", created_by=random.choice(heads))
        Transaction.objects.create(type="expense", category=stationery, amount=Decimal(1200000),
                                   description="Mua loa mini cho CLB", date=today - timedelta(days=12),
                                   status="rejected", created_by=random.choice(heads),
                                   approved_by=random.choice(board))

    # ---------- Công việc ----------
    def make_tasks(self, events):
        board = [u for u in self.users if u.role == "board"]
        by_dept = {}
        for u in self.users:
            by_dept.setdefault(self.user_depts[u.id], []).append(u)
        today = timezone.localdate()
        statuses = ["done"] * 10 + ["doing"] * 8 + ["todo"] * 8
        random.shuffle(statuses)
        for (title, dname), status in zip(TASK_TITLES, statuses):
            pool = [u for u in by_dept[dname] if u.activity != "low"] or by_dept[dname]
            assignee = random.choice(pool)
            if status == "done":
                due = today - timedelta(days=random.randint(5, 60))
            elif random.random() < 0.3:
                due = today - timedelta(days=random.randint(1, 5))  # quá hạn
            else:
                due = today + timedelta(days=random.randint(2, 20))
            t = Task.objects.create(
                title=title, description=f"Công việc của Ban {dname}.",
                assignee=assignee, department=self.depts[dname],
                event=random.choice(events) if random.random() < 0.5 else None,
                priority=random.choice(["low", "medium", "medium", "high"]),
                status=status, due_date=due, created_by=random.choice(board))
            if status == "done":
                Task.objects.filter(pk=t.pk).update(
                    completed_at=timezone.make_aware(datetime.combine(due, time(17, 0))))

    # ---------- Truyền thông ----------
    def make_comms(self, upcoming):
        board = [u for u in self.users if u.role == "board"]
        active = [u for u in self.users if u.activity != "low"]
        for k, (title, notes) in enumerate(MINUTES):
            m = MeetingMinute.objects.create(
                title=title, date=timezone.localdate() - timedelta(days=120 - k * 35),
                location="Phòng sinh hoạt CLB", raw_notes=notes, created_by=random.choice(board))
            m.attendees.set(random.sample(active, min(len(active), random.randint(8, 15))))

        texts = [
            ("Mở đăng ký " + upcoming[0].title, upcoming[0], True),
            ("Thông báo lịch " + upcoming[1].title, upcoming[1], False),
            ("Tuyển cộng tác viên Ban Truyền Thông", None, False),
            ("Nhắc nhở đóng quỹ thành viên tháng này", None, False),
        ]
        for title, ev, pinned in texts:
            body = (f"Chào các bạn,\n\n{title}. "
                    + (f"Thời gian: {timezone.localtime(ev.start_time):%H:%M %d/%m/%Y}, địa điểm: {ev.location}. "
                       if ev else "")
                    + "Mọi thắc mắc vui lòng liên hệ Ban điều hành.\n\nThân mến!")
            Announcement.objects.create(title=title, content=body, event=ev, pinned=pinned,
                                        created_by=random.choice(board))
