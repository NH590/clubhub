# HƯỚNG DẪN CÀI ĐẶT MÔI TRƯỜNG – ClubHub

Ứng dụng quản lý câu lạc bộ sinh viên có AI hỗ trợ vận hành.
Công nghệ: Django + PostgreSQL + Celery/Redis + Claude/OpenAI, deploy trên Render.

---

## 1. Cài phần mềm cần thiết

| Phần mềm | Ghi chú |
|---|---|
| Python 3.12 | python.org. **Tick "Add python.exe to PATH"** khi cài |
| Git | git-scm.com, cài mặc định |
| PostgreSQL + pgAdmin | Đã có |
| PyCharm | Đã có |
| Redis (dùng từ tuần 6) | **Memurai** (memurai.com), hoặc Docker: `docker run -d --name redis -p 6379:6379 redis`, hoặc Upstash (cloud) |

Kiểm tra trong Command Prompt:
```
python --version
git --version
```
Nếu gõ `python` mà Microsoft Store bật lên, vào *Settings → Apps → Advanced app settings → App execution aliases* và tắt 2 mục python.

Cấu hình Git:
```
git config --global user.name "Ten Cua Ban"
git config --global user.email "email@gmail.com"
```

## 2. Tạo database

Trong pgAdmin, chạy Query Tool:
```sql
CREATE DATABASE clubhub;
```

## 3. Mở project bằng PyCharm

1. Giải nén `clubhub.zip`, ví dụ vào `D:\Projects\clubhub`.
2. Trong PyCharm: **File → Open** rồi chọn thư mục `clubhub`.
3. Vào **Settings → Project → Python Interpreter → Add Interpreter → Virtualenv → New**, chọn Base là Python 3.12 và Location là `.venv` trong project.

## 4. Cài đặt tự động (cách nhanh)

Chạy `setup.bat` bằng cách double-click hoặc gõ `setup.bat` trong Terminal của PyCharm:

1. **Lần 1**: script tạo `.venv`, cài thư viện và tạo file `.env` (đã có sẵn SECRET_KEY ngẫu nhiên).
   Mở `.env` và sửa `MATKHAU` thành mật khẩu PostgreSQL của bạn.
2. **Lần 2**: script kiểm tra kết nối và tạo bảng (migrate).

### Hoặc làm thủ công
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env        (rồi sửa .env)
python manage.py makemigrations
python manage.py migrate
```
Nếu `activate` báo lỗi *running scripts is disabled*, chạy:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## 5. Tạo admin và chạy thử

```
python manage.py createsuperuser
python manage.py runserver
```
- Trang chủ: http://127.0.0.1:8000
- Trang quản trị: http://127.0.0.1:8000/admin (có thể đổi *Vai trò* cho user ở đây)
- Đăng nhập: http://127.0.0.1:8000/accounts/login/

## 6. Chạy Celery (khi làm đến background jobs)

Mở thêm một Terminal (đã có `.venv`) và chạy:
```
celery -A config worker -l info --pool=solo
celery -A config beat -l info
```
Trên Windows **bắt buộc** có `--pool=solo`.

## 7. Đưa code lên GitHub

```
git init
git add .
git commit -m "Khoi tao project ClubHub"
git branch -M main
git remote add origin https://github.com/USERNAME/clubhub.git
git push -u origin main
```
Trước khi push, chạy `git status` để chắc chắn **file `.env` không bị đẩy lên**.

## 8. Lỗi thường gặp

| Lỗi | Cách sửa |
|---|---|
| `password authentication failed` | Sai mật khẩu trong `DATABASE_URL` |
| `database "clubhub" does not exist` | Chưa làm bước 2 |
| `No module named ...` | Chưa bật `.venv` hoặc chưa `pip install -r requirements.txt` |
| `connection refused` port 5432 | Mở `services.msc` và Start service `postgresql-x64-...` |
| Mật khẩu có `@ # /` | Mã hóa URL cho ký tự đó (ví dụ `@` viết thành `%40`) hoặc đổi mật khẩu |
| `Error 10061` khi chạy Celery | Redis chưa chạy |

---

## Cấu trúc project

```
clubhub/
├── config/          # settings.py, urls.py, celery.py
├── accounts/        # User tùy chỉnh (role, MSSV, SĐT, khoa) + decorator phân quyền
├── members/         # Thành viên, ban
├── events/          # Sự kiện, check-in QR
├── finance/         # Quỹ thu chi
├── tasks/           # Task nội bộ
├── comms/           # Thông báo, biên bản họp
├── ai_support/      # Tính năng AI
├── reports/         # Dashboard, báo cáo
├── templates/       # base.html, home.html, login.html
├── requirements.txt
├── .env.example     # mẫu biến môi trường
├── build.sh         # script build cho Render
└── setup.bat        # cài đặt tự động trên Windows
```

Phân quyền trong view dùng decorator có sẵn:
```python
from accounts.decorators import role_required

@role_required("admin", "board")
def tao_su_kien(request): ...
```
