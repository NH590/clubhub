@echo off
chcp 65001 >nul
echo === ClubHub - Cai dat moi truong ===
python --version || (echo Chua cai Python 3.12! & pause & exit /b)
if not exist .venv (
  echo [1/4] Tao moi truong ao .venv ...
  python -m venv .venv
)
call .venv\Scripts\activate.bat
echo [2/4] Cai thu vien ...
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist .env (
  echo [3/4] Tao file .env tu .env.example ...
  copy .env.example .env >nul
  for /f %%i in ('python -c "import secrets;print(secrets.token_urlsafe(50))"') do set SK=%%i
  powershell -Command "(Get-Content .env) -replace '^SECRET_KEY=.*', 'SECRET_KEY=%SK%' | Set-Content .env -Encoding UTF8"
  echo.
  echo  ^>^>^> Hay mo file .env va sua MATKHAU PostgreSQL trong DATABASE_URL,
  echo      sau do chay lai setup.bat
  pause
  exit /b
)
echo [4/4] Kiem tra ket noi va migrate ...
python manage.py check && python manage.py makemigrations && python manage.py migrate
echo.
echo === XONG! Tao tai khoan admin: python manage.py createsuperuser
echo === Chay server: python manage.py runserver
pause
