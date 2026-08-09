#!/usr/bin/env bash
# Chan moi no luc commit file .env. Chay tu dong truoc moi commit.
# Day la hang rao thu hai; hang rao thu nhat la .gitignore.
set -euo pipefail

# -z de git in ten file cach nhau bang byte 0: khong bi core.quotePath boc
# nhay va escape khi duong dan co ky tu tieng Viet.
# Chan .env va moi bien the .env.* (vi du .env.local), chi tha .env.example.
if git diff --cached --name-only -z | tr '\0' '\n' \
   | grep -vE '(^|/)\.env\.example$' \
   | grep -qE '(^|/)\.env(\.|$)'; then
    echo "LOI: dang co gang commit file .env - huy commit"
    echo "File .env chua khoa API that, khong bao gio duoc dua len git."
    echo "Muon chia se cau hinh thi sua .env.example."
    exit 1
fi
