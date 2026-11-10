@echo off
title Fintrust EWS - Windows Setup

echo =======================================================================
echo * HE THONG CANH BAO SOM EWS FINTRUST - CAI DAT MOI TRUONG WINDOWS *
echo =======================================================================
echo.

rem 1. Kiem tra su hien huu cua Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Khong tim thay Python tren may tinh cua ban!
    echo Vui long tai va cai dat Python 3.10 hoac moi hon tu trang chu:
    echo https://www.python.org/downloads/
    echo Luu y: Hay tich chon "Add Python to PATH" trong qua trinh cai dat.
    echo.
    pause
    exit /b
)
echo [OK] Da tim thay Python.

rem 2. Khoi tao moi truong ao Python (Venv)
if not exist "venv" (
    echo [*] Dang tao moi truong ao Python [venv]...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Khong the khoi tao moi truong ao.
        pause
        exit /b
    )
)
echo [OK] Da chuan bi moi truong ao.

rem 3. Kich hoat moi truong ao va cai dat thu vien
echo [*] Dang kich hoat moi truong ao va kiem tra thu vien...
call venv\Scripts\activate

if not exist "venv\.installed" (
    echo [*] Dang cai dat thu vien lan dau...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Cai dat thu vien that bai! Vui long kiem tra lai ket noi mang.
        pause
        exit /b
    )
    type nul > "venv\.installed"
    echo [OK] Da cai dat day du thu vien trong requirements.txt.
) else (
    echo [OK] Thu vien da san sang (khoi dong tuc thi).
)
echo.

rem 4. Huong dan cai dat Tesseract OCR cho bao cao dang anh quet (PDF Scan)
echo -----------------------------------------------------------------------
echo * YEU CAU BO SUNG: HE THONG OCR (TESSERACT)
echo -----------------------------------------------------------------------
echo De quet cac tai lieu PDF dang hinh anh chup, ban can cai dat Tesseract OCR:
echo 1. Tai bo cai Tesseract OCR cho Windows tai:
echo    https://github.com/UB-Mannheim/tesseract/wiki
echo 2. Cai dat vao may va ghi nho thu muc cai dat (vi du: C:\Program Files\Tesseract-OCR\)
echo 3. Phan mem Fintrust EWS se tu dong do tim duong dan chuan nay khi quet.
echo -----------------------------------------------------------------------
echo.

rem 5. Menu lua chon tac vu
:menu
echo Vui long lua chon tac vu ban muon thuc hien:
echo [1] Chay ung dung Fintrust EWS o che do Desktop
echo [2] Dong goi phan mem thanh tep Fintrust_EWS.exe doc lap (su dung PyInstaller)
echo [3] Thoat
echo.
set /p choice="Nhap lua chon cua ban (1/2/3): "

if "%choice%"=="1" (
    echo.
    echo [*] Dang khoi chay Fintrust EWS Desktop...
    python desktop_wrapper.py
    goto end
)
if "%choice%"=="2" (
    echo.
    echo [*] Dang tien hanh dong goi ung dung [qua trinh nay co the mat vai phut]...
    python build_app.py
    goto end
)
if "%choice%"=="3" (
    goto end
)
echo Lua chon khong hop le, vui loang thu lai.
echo.
goto menu

:end
echo.
echo Cam on ban da su dung Fintrust EWS.
pause
