#!/bin/bash

# Thiet lap tieu de console
echo -e "\033]0;Fintrust EWS - Docker Launcher\007"

echo "======================================================================="
echo "* HE THONG CANH BAO SOM EWS FINTRUST - KHOI DONG DOCKER CONTAINER *"
echo "======================================================================="
echo ""

# 1. Kiem tra xem Docker co dang chay khong
docker info >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[ERROR] Docker Desktop chua duoc khoi dong hoac chua duoc cai dat!"
    echo "Vui long mo ung dung Docker Desktop tren may Mac cua ban va doi den khi san sang,"
    echo "sau do chay lai script nay."
    echo ""
    read -p "Nhan [Enter] de thoat..."
    exit 1
fi

# 2. Khoi chay Docker Container
echo "[*] Dang khoi dong Docker container (khoi dong nhanh)..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "[ERROR] Khoi dong Docker container that bai!"
    read -p "Nhan [Enter] de thoat..."
    exit 1
fi
echo "[OK] Docker container dang chay ngam thanh cong."

# 3. Tu dong mo trinh duyet web tren macOS
echo "[*] Dang mo trinh duyet den dia chi: http://localhost:8501"
open "http://localhost:8501" 2>/dev/null || xdg-open "http://localhost:8501" 2>/dev/null

echo ""
echo "======================================================================="
echo "[SUCCESS] FINTRUST EWS KHOI DONG THANH CONG!"
echo "- ung dung dang chay tai: http://localhost:8501"
echo "- Database va tep cache duoc luu tai thu muc: ./data/"
echo "======================================================================="
echo ""
read -p "Nhan [Enter] de thoat..."
