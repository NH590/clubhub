# sync_neon.ps1 - Chep du lieu tu may len Neon (ban online)
if (-not (Test-Path neon.txt)) { Write-Host "Chua co file neon.txt" -ForegroundColor Red; exit 1 }
$neon = (Get-Content neon.txt -Raw).Trim()
if (-not $neon.StartsWith("postgresql://")) { Write-Host "neon.txt sai noi dung" -ForegroundColor Red; exit 1 }

Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
Write-Host "1/4 Xuat du lieu tu database tren may..." -ForegroundColor Cyan
.venv\Scripts\python -X utf8 manage.py dumpdata --natural-foreign --natural-primary --exclude contenttypes --exclude auth.permission --exclude admin.logentry --exclude sessions --exclude django_celery_beat --indent 2 -o data.json
if ($LASTEXITCODE -ne 0) { Write-Host "Loi khi xuat du lieu" -ForegroundColor Red; exit 1 }

$env:DATABASE_URL = $neon
try {
    Write-Host "2/4 Cap nhat bang tren Neon..." -ForegroundColor Cyan
    .venv\Scripts\python manage.py migrate
    if ($LASTEXITCODE -ne 0) { throw "migrate loi" }
    Write-Host "3/4 Xoa du lieu cu tren Neon..." -ForegroundColor Cyan
    .venv\Scripts\python manage.py flush --no-input
    if ($LASTEXITCODE -ne 0) { throw "flush loi" }
    Write-Host "4/4 Nap du lieu len Neon..." -ForegroundColor Cyan
    .venv\Scripts\python manage.py loaddata data.json
    if ($LASTEXITCODE -ne 0) { throw "loaddata loi" }
    Write-Host "XONG! Ban online da giong du lieu tren may." -ForegroundColor Green
}
catch { Write-Host "Co loi: $_" -ForegroundColor Red }
finally {
    Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
    Remove-Item data.json -ErrorAction SilentlyContinue
}