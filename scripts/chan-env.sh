#!/usr/bin/env bash
# Chan moi no luc commit file .env. Chay tu dong truoc moi commit.
# Day la hang rao thu hai; hang rao thu nhat la .gitignore.
set -euo pipefail

if git diff --cached --name-only | grep -qE '(^|/)\.env$'; then
    echo "LOI: dang co gang commit file .env - huy commit"
    echo "File .env chua khoa API that, khong bao gio duoc dua len git."
    echo "Muon chia se cau hinh thi sua .env.example."
    exit 1
fi
