"""Kiem tra logic doctor.

Cac ham kiem tra nhan tham so thay vi tu doc trang thai he thong, nen test
duoc ca truong hop Python 3.14 ma khong can cai Python 3.14.
"""

from app.core.doctor import (
    BaoCao,
    KetQua,
    chay_kiem_tra,
    kiem_tra_lenh,
    kiem_tra_python,
)


def test_python_3_12_thi_dat():
    kq = kiem_tra_python((3, 12))
    assert kq.dat is True
    assert "3.12" in kq.chi_tiet


def test_python_3_14_thi_truot():
    kq = kiem_tra_python((3, 14))
    assert kq.dat is False
    assert "3.14" in kq.chi_tiet


def test_python_3_11_thi_truot():
    assert kiem_tra_python((3, 11)).dat is False


def test_kiem_tra_lenh_co_that_thi_dat():
    kq = kiem_tra_lenh("git")
    assert kq.dat is True


def test_kiem_tra_lenh_khong_ton_tai_thi_truot():
    kq = kiem_tra_lenh("lenh-chac-chan-khong-ton-tai-xyz")
    assert kq.dat is False
    assert kq.chi_tiet == "chua cai"


def test_bao_cao_bo_qua_muc_khong_bat_buoc():
    bc = BaoCao([
        KetQua("a", True, "ok", bat_buoc=True),
        KetQua("b", False, "chua cai", bat_buoc=False),
    ])
    assert bc.tat_ca_dat() is True


def test_bao_cao_truot_khi_muc_bat_buoc_truot():
    bc = BaoCao([KetQua("a", False, "hong", bat_buoc=True)])
    assert bc.tat_ca_dat() is False


def test_dinh_dang_hien_thi_moi_muc_tren_mot_dong():
    bc = BaoCao([
        KetQua("a", True, "ok"),
        KetQua("b", False, "chua cai"),
    ])
    dong = bc.dinh_dang().splitlines()
    assert len(dong) == 2
    assert "a" in dong[0]
    assert "b" in dong[1]


def test_chay_kiem_tra_tra_ve_bao_cao_khong_rong():
    bc = chay_kiem_tra()
    assert len(bc.ket_qua) > 0


def test_docker_khong_bat_buoc_o_chang_0():
    bc = chay_kiem_tra()
    docker = next(k for k in bc.ket_qua if k.ten == "docker")
    assert docker.bat_buoc is False


def test_cau_hinh_hong_thi_bao_cao_chu_khong_nem_loi(monkeypatch):
    """Lenh doctor ton tai de chan doan may hong nen no khong duoc chet vi may hong."""
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "")

    bc = chay_kiem_tra()

    cau_hinh = next(k for k in bc.ket_qua if k.ten == "Cau hinh")
    assert cau_hinh.dat is False
    assert "DEEPSEEK_API_KEY" in cau_hinh.chi_tiet
    assert bc.tat_ca_dat() is False


from app.__main__ import main


def test_main_lenh_doctor_tra_ve_0_khi_moi_thu_dat(capsys):
    ma_thoat = main(["doctor"])
    captured = capsys.readouterr()
    assert "Python" in captured.out
    assert ma_thoat == 0


def test_main_khong_co_lenh_thi_thoat_voi_loi(capsys):
    import pytest

    with pytest.raises(SystemExit) as e:
        main([])
    assert e.value.code != 0
