"""Kiem tra module cau hinh."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings, lay_cau_hinh


def test_mac_dinh_dung_provider_fake():
    """Mac dinh phai la fake de test khong bao gio goi mang that."""
    s = Settings(_env_file=None)
    assert s.llm_provider == "fake"


def test_doc_duoc_tu_bien_moi_truong(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-123")
    s = Settings(_env_file=None)
    assert s.llm_provider == "deepseek"
    assert s.deepseek_api_key.get_secret_value() == "sk-test-123"


def test_bao_loi_khi_chon_deepseek_ma_thieu_khoa():
    with pytest.raises(ValidationError, match="DEEPSEEK_API_KEY"):
        Settings(_env_file=None, llm_provider="deepseek", deepseek_api_key="")


def test_bao_loi_khi_chon_provider_khong_ton_tai():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, llm_provider="chatgpt")


def test_lay_cau_hinh_tra_ve_doi_tuong_settings():
    assert isinstance(lay_cau_hinh(), Settings)


def test_secretstr_khong_lo_khoa_trong_repr(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-khoa-bi-mat-abc")
    s = Settings(_env_file=None)
    assert "sk-khoa-bi-mat-abc" not in repr(s)
    assert "sk-khoa-bi-mat-abc" not in str(s)


def test_lay_cau_hinh_cache_tra_cung_object():
    a = lay_cau_hinh()
    b = lay_cau_hinh()
    assert a is b


def test_lay_cau_hinh_cache_clear_thay_gia_tri_moi(monkeypatch):
    s1 = lay_cau_hinh()
    assert s1.log_level == "INFO"
    lay_cau_hinh.cache_clear()
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    s2 = lay_cau_hinh()
    assert s2.log_level == "DEBUG"
    assert s1 is not s2
