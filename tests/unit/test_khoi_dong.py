"""Kiem tra package app cai dat va import duoc."""

import re

from app import __version__


def test_app_co_so_phien_ban():
    assert re.fullmatch(r"\d+\.\d+\.\d+", __version__)
