@echo off
title Fintrust EWS - Docker Launcher

echo =======================================================================
echo * HE THONG CANH BAO SOM EWS FINTRUST - KHOI DONG DOCKER CONTAINER *
echo =======================================================================
echo.

rem 1. Kiem tra xem Docker Desktop co dang chay khong
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Desktop chua duoc khoi dong hoac chua duoc cai dat!
    echo Vui long mo Docker Desktop tren may cua ban va doi den khi no san sang,
    echo sau do chay lai file nay.
    echo.
    pause
    exit /b
)

rem 2. Khoi chay Docker Container ngam
echo [*] Dang khoi dong Docker container (khoi dong nhanh)...
docker-compose up -d
if %errorlevel% neq 0 (
    echo [ERROR] Khoi dong Docker container that bai!
    pause
    exit /b
)
echo [OK] Docker container dang chay ngam thanh cong.

rem 3. Tu dong mo trinh duyet web
echo [*] Dang mo trinh duyet den dia chi: http://localhost:8501
start http://localhost:8501

echo.
echo =======================================================================
echo [SUCCESS] FINTRUST EWS KHOI DONG THANH CONG!
echo - ung dung dang chay tai: http://localhost:8501
echo - Database va tệp cache duoc luu an toan tai thu muc: ./data/
echo =======================================================================
echo.
pause
