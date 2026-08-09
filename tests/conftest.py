"""Lam cho test hermetic: ket qua khong duoc phu thuoc vao may dang chay.

Settings doc cau hinh tu hai nguon: bien moi truong, va file .env trong thu
muc lam viec hien tai. Ca hai nguon do deu la trang thai cua may, khong phai
cua test. Neu de nguyen, mot nguoi hoc lam dung theo README (cp .env.example
.env roi doi LLM_PROVIDER=deepseek truoc khi dan khoa) se thay test do ma
khong hieu vi sao - loi nam o file .env cua ho, khong nam o code.

CI khong bat duoc loi nay: .env bi .gitignore chan nen runner khong bao gio
co file do. CI xanh o day nghia la "moi truong CI ngheo hon may that", chu
khong phai "test da doc lap voi moi truong". Vi vay bo fixture nay di se tai
tao lai mot bug chi hien tren may nguoi hoc va an tren CI.

Fixture duoi day chay tu dong cho moi test: xoa het bien moi truong cua app,
roi chuyen thu muc lam viec sang mot thu muc tam rong (nen khong co .env).
Test nao can mot gia tri cu the thi tu dat lay bang monkeypatch.setenv.
"""

import pytest

BIEN_CUA_APP = (
    "LLM_PROVIDER",
    "DEEPSEEK_API_KEY",
    "DEEPSEEK_BASE_URL",
    "DEEPSEEK_MODEL",
    "OLLAMA_BASE_URL",
    "OLLAMA_MODEL",
    "EMBEDDING_MODEL",
    "EMBEDDING_DEVICE",
    "DATA_DIR",
    "SQLITE_PATH",
    "QDRANT_URL",
    "QDRANT_COLLECTION",
    "LOG_LEVEL",
)


@pytest.fixture(autouse=True)
def moi_truong_sach(monkeypatch, tmp_path):
    """Test khong duoc phu thuoc file .env hay bien moi truong cua may."""
    for ten in BIEN_CUA_APP:
        monkeypatch.delenv(ten, raising=False)
    monkeypatch.chdir(tmp_path)
