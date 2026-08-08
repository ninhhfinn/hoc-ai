"""Kiem tra moi truong may co du dieu kien chay app khong.

Cac ham kiem tra nhan tham so dau vao thay vi tu doc trang thai he thong.
Do la ly do chung test duoc: muon thu truong hop Python 3.14 thi chi can
truyen (3, 14) vao, khong can cai Python 3.14 that.
"""

import platform
import shutil
import sys
from dataclasses import dataclass

from pydantic import ValidationError

from app.core.config import Settings

PYTHON_YEU_CAU = (3, 12)


@dataclass(frozen=True)
class KetQua:
    """Ket qua cua mot muc kiem tra."""

    ten: str
    dat: bool
    chi_tiet: str
    bat_buoc: bool = True


@dataclass(frozen=True)
class BaoCao:
    """Tap hop ket qua cua tat ca muc kiem tra."""

    ket_qua: list[KetQua]

    def tat_ca_dat(self) -> bool:
        """Chi tinh cac muc bat buoc."""
        return all(k.dat for k in self.ket_qua if k.bat_buoc)

    def dinh_dang(self) -> str:
        dong = []
        for k in self.ket_qua:
            if k.dat:
                nhan = "OK   "
            elif k.bat_buoc:
                nhan = "THIEU"
            else:
                nhan = "BO QUA"
            dong.append(f"{nhan} {k.ten}: {k.chi_tiet}")
        return "\n".join(dong)


def kiem_tra_python(phien_ban: tuple[int, int]) -> KetQua:
    """Xac nhan dang chay dung Python 3.12."""
    dat = phien_ban == PYTHON_YEU_CAU
    chi_tiet = f"dang chay {phien_ban[0]}.{phien_ban[1]}"
    if not dat:
        chi_tiet += f", can {PYTHON_YEU_CAU[0]}.{PYTHON_YEU_CAU[1]}"
    return KetQua("Python", dat, chi_tiet)


def kiem_tra_lenh(ten: str, bat_buoc: bool = True) -> KetQua:
    """Xac nhan mot lenh co ton tai trong PATH khong."""
    duong_dan = shutil.which(ten)
    return KetQua(ten, duong_dan is not None, duong_dan or "chua cai", bat_buoc)


def chay_kiem_tra(settings: Settings | None = None) -> BaoCao:
    """Chay toan bo muc kiem tra va tra ve bao cao.

    Neu cau hinh sai thi ghi thanh mot muc truot chu khong nem loi ra ngoai:
    lenh doctor ton tai de chan doan may hong, nen ban than no khong duoc
    chet vi may hong.
    """
    muc: list[KetQua] = [
        kiem_tra_python(sys.version_info[:2]),
        kiem_tra_lenh("git"),
        kiem_tra_lenh("docker", bat_buoc=False),
        KetQua("He dieu hanh", True, platform.platform()),
    ]

    s: Settings | None = settings
    if s is None:
        try:
            s = Settings()
        except ValidationError as loi:
            muc.append(KetQua("Cau hinh", False, str(loi).replace("\n", " ")))

    if s is not None:
        muc.append(KetQua("Cau hinh", True, "doc duoc"))
        muc.append(KetQua("LLM provider", True, s.llm_provider))
        muc.append(KetQua("Embedding device", True, s.embedding_device))

    return BaoCao(muc)
