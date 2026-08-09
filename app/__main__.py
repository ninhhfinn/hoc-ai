"""Diem vao dong lenh cua app.

Lop nay chi lam mot viec: chuyen doi so dong lenh thanh loi goi ham.
Khong chua logic nghiep vu nao.
"""

import argparse
import sys

from app import __version__
from app.core.doctor import chay_kiem_tra


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="app",
        description="App hoc tap de tro thanh AI Engineer",
    )
    parser.add_argument(
        "lenh",
        choices=["doctor", "version"],
        help="doctor: kiem tra moi truong may | version: in so phien ban",
    )
    args = parser.parse_args(argv)

    if args.lenh == "doctor":
        bao_cao = chay_kiem_tra()
        print(bao_cao.dinh_dang())
        return 0 if bao_cao.tat_ca_dat() else 1

    if args.lenh == "version":
        print(__version__)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
