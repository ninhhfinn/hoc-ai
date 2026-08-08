"""Kiem tra package app cai dat va import duoc."""

from app import __version__


def test_app_co_so_phien_ban():
    assert __version__ == "0.1.0"
