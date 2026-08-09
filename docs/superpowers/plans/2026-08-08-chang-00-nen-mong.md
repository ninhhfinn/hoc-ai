# Chặng 0 — Nền móng: Kế hoạch triển khai

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dựng nền móng kỹ thuật của dự án — môi trường Python 3.12 ghim bằng `uv`, module cấu hình có kiểu, lệnh `doctor` kiểm tra máy, lint/type-check tự động, hàng rào chặn lộ khoá API, CI xanh trên GitHub, và một Pull Request hoàn chỉnh.

**Architecture:** Package `app/` cài ở chế độ editable qua `uv`. `app/core/config.py` đọc biến môi trường thành đối tượng Pydantic có kiểu — mọi chặng sau đều dùng nó. `app/core/doctor.py` chứa các hàm thuần (nhận tham số, không đọc trạng thái toàn cục) để kiểm tra môi trường, nên test được mà không cần giả lập hệ thống. `app/__main__.py` chỉ là lớp mỏng chuyển đối số dòng lệnh thành lời gọi hàm.

**Tech Stack:** Python 3.12 (qua `uv`), Pydantic 2 + pydantic-settings, pytest, ruff, mypy, pre-commit, GitHub Actions.

**Spec nguồn:** `docs/superpowers/specs/2026-08-08-app-hoc-ai-engineering-design.md` — Chặng 0 trong §13, quyết định §9.1 và §9.3.

**Thời lượng dự kiến:** ~20 giờ (2 tuần × 10h). Task 1 khoảng 3h đọc, Task 2–7 khoảng 17h.

## Global Constraints

- **Python 3.12** — bắt buộc. Không dùng Python 3.14.4 có sẵn trên máy: `torch` và `sentence-transformers` chưa có wheel cho 3.12+. `requires-python = ">=3.12,<3.13"`.
- **Tất cả tên hàm, biến, comment, docstring, thông báo lỗi viết bằng tiếng Việt không dấu** (ví dụ `kiem_tra_python`, `bat_buoc`). Lý do: người học đọc code của chính mình dễ hơn, và tránh lỗi encoding trên console. Nội dung trong `docs/lessons/` thì viết **tiếng Việt có dấu**.
- **Viết test trước, luôn luôn** (spec §9.3). Mỗi task đều theo vòng đỏ → xanh → commit.
- **Không bao giờ commit `.env`.** File `.gitignore` đã chặn; Task 5 thêm hàng rào thứ hai.
- **`llm_provider` mặc định là `"fake"`** — để không có test nào vô tình gọi mạng hay tốn tiền.
- **Mỗi task kết thúc bằng một commit.** Thông điệp commit theo Conventional Commits (`feat:`, `test:`, `chore:`, `docs:`, `ci:`).
- **Repo hiện có:** nhánh `main`, commit `d3252d8`, chứa `.gitignore` và spec. Kế hoạch này xây tiếp lên đó.
- **Chưa có remote GitHub.** Task 7 tạo remote.

---

## Cấu trúc file sau khi xong Chặng 0

| File | Trách nhiệm |
|---|---|
| `.python-version` | Ghim Python 3.12 cho `uv` |
| `pyproject.toml` | Khai báo phụ thuộc + cấu hình pytest, ruff, mypy |
| `uv.lock` | Khoá phiên bản chính xác (commit vào git) |
| `.env.example` | Mẫu biến môi trường, an toàn để commit |
| `.pre-commit-config.yaml` | Hook chạy trước mỗi commit |
| `scripts/chan-env.sh` | Hàng rào thứ hai chặn commit `.env` |
| `.github/workflows/ci.yml` | Chạy lint + type-check + test trên GitHub |
| `README.md` | Giới thiệu, cách chạy |
| `app/__init__.py` | Số phiên bản |
| `app/core/config.py` | Đọc biến môi trường → đối tượng `Settings` có kiểu |
| `app/core/doctor.py` | Các hàm thuần kiểm tra môi trường |
| `app/__main__.py` | Điểm vào dòng lệnh, lớp mỏng |
| `tests/unit/test_khoi_dong.py` | Kiểm tra package import được |
| `tests/unit/test_config.py` | Kiểm tra `Settings` |
| `tests/unit/test_doctor.py` | Kiểm tra logic doctor |
| `docs/lessons/lesson-00-nen-mong.md` | Lý thuyết Chặng 0 |

Ranh giới cố ý: `doctor.py` **không** tự đọc `sys.version_info` bên trong hàm kiểm tra — nó nhận phiên bản làm tham số. Nhờ vậy test kiểm tra được cả trường hợp Python 3.14 mà không cần cài Python 3.14.

---

### Task 1: Viết và đọc bài học lesson-00

**Files:**
- Create: `docs/lessons/lesson-00-nen-mong.md`

**Interfaces:**
- Consumes: nội dung spec §9.1, §9.3, §9.6
- Produces: tài liệu Markdown; Chặng 3 sẽ nạp file này vào app làm tài liệu RAG đầu tiên, nên phải có tiêu đề `##` rõ ràng để chunker cắt theo mục

- [ ] **Step 1: Tạo thư mục**

```bash
mkdir -p docs/lessons
```

- [ ] **Step 2: Viết bài học với đúng 6 mục sau**

Tạo `docs/lessons/lesson-00-nen-mong.md`. Viết tiếng Việt có dấu. Mỗi mục là một `##`.

**Mục 1 — `## AI Engineer khác ML Researcher chỗ nào`**
Phải chứa bảng so sánh train vs inference, lấy nguyên số liệu từ spec §9.6:

```
Train (mixed-precision Adam), model N tham so:
  trong so fp16 2N + gradient 2N + ban fp32 4N + Adam m 4N + Adam v 4N = 16N byte
  -> model 7B can ~112 GB VRAM

Inference (luong tu hoa 4-bit):
  trong so ~0.5N + ngu canh
  -> model 7B can ~5 GB VRAM
```

Kết luận phải viết rõ: **dự án này không train gì cả**, và RTX 4060 8GB thừa sức chạy
`multilingual-e5-base` (~0.6 GB) lẫn Qwen2.5-7B 4-bit (~5 GB).

**Mục 2 — `## RAG tồn tại để làm gì`**
Nêu hai đường dạy model biết tài liệu của bạn: train lại (112GB VRAM, hàng nghìn đô, vài tuần)
so với RAG (tìm đoạn liên quan, dán vào prompt, 5 giây, 0 đồng). RAG là câu trả lời cho
*"dạy model thứ nó chưa biết mà không cần train"*.

**Mục 3 — `## Vì sao phải ghim phiên bản Python`**
Máy đang có Python 3.14.4. `torch` chưa có wheel cho 3.14. Giải thích wheel là gì, vì sao
build từ nguồn thất bại. Giới thiệu `uv` và file `.python-version`. Nêu rõ: `uv` tải Python
riêng cho project, không đụng Python hệ thống.

**Mục 4 — `## Môi trường ảo và khoá phụ thuộc`**
Vì sao mỗi project cần môi trường riêng. `pyproject.toml` khai báo *muốn gì*, `uv.lock` ghi
*chính xác cái gì đã cài*. Vì sao phải commit `uv.lock` (để CI và máy khác cài y hệt).

**Mục 5 — `## Vì sao viết test trước`**
Ba lý do trong spec §9.3: học một mình không ai review; code AI sai âm thầm (retrieval trả
đoạn sai mà câu trả lời vẫn nghe xuôi tai); CI xanh là bằng chứng nhà tuyển dụng nhìn thấy.
Giải thích vòng đỏ → xanh → refactor.

**Mục 6 — `## Git: nhánh, commit, Pull Request`**
Vì sao không commit thẳng lên `main`. Nhánh là gì. Pull Request là gì và vì sao tự review PR
của mình vẫn có ích. Đối chiếu: GitLab gọi là Merge Request, cùng khái niệm — JD ghi cả hai.
Conventional Commits: `feat:`, `fix:`, `test:`, `docs:`, `chore:`, `ci:`.

**Mục 7 — `## Terminal Linux và cách đọc log`**
JD ghi "Docker, Linux, đọc log". Mục này lo phần Linux nền và thói quen đọc log; Docker để
Chặng 4.

Các lệnh tối thiểu, mỗi lệnh một câu giải thích *khi nào cần đến nó*:
`pwd`, `ls -la`, `cd`, `cat`, `less`, `tail -f`, `grep -n`, `find`, `chmod +x`, `which`,
`echo $PATH`, `df -h`, `free -h`, `nvidia-smi`.

Ba khái niệm phải nêu rõ:

1. **`PATH` là gì** — vì sao gõ `git` thì máy tìm thấy mà gõ `docker` thì không. Nối với hàm
   `kiem_tra_lenh` sẽ viết ở Task 4: nó chỉ đang tra `PATH` hộ bạn.
2. **stdout và stderr là hai luồng khác nhau** — vì sao `lenh > file.txt` vẫn thấy lỗi hiện
   ra màn hình, và `2>&1` giải quyết ra sao.
3. **Mã thoát (exit code)** — `0` là thành công, khác `0` là thất bại. `echo $?` để xem. Đây
   là cơ chế CI dùng để biết build đỏ hay xanh, và cũng là lý do hàm `main` ở Task 4 phải
   trả về số nguyên.

Thói quen đọc log — viết thành ba bước:

1. Đọc **dòng lỗi đầu tiên**, không phải dòng cuối. Dòng cuối thường chỉ là hệ quả.
2. Tìm tên file và số dòng trong stack trace — đó là chỗ cần mở ra xem.
3. Không đoán. Nếu log chưa đủ thông tin thì thêm log, chạy lại, rồi mới sửa.

- [ ] **Step 3: Đọc lại toàn bộ bài học**

Đọc từ đầu đến cuối. Với mỗi mục, tự trả lời miệng câu hỏi tương ứng:

1. Vì sao 8GB VRAM đủ cho dự án này?
2. RAG thay thế cho việc gì?
3. Vì sao không dùng Python 3.14 có sẵn?
4. Vì sao phải commit `uv.lock`?
5. Vì sao code AI cần test hơn code thường?
6. Merge Request và Pull Request khác nhau thế nào?
7. Mã thoát khác `0` nghĩa là gì, và CI dùng nó để làm gì?

Chỗ nào không trả lời được thì hỏi lại trước khi sang Task 2.

- [ ] **Step 4: Commit**

```bash
git add docs/lessons/lesson-00-nen-mong.md
git commit -m "docs: them bai hoc lesson-00 nen mong"
```

---

### Task 2: Môi trường Python 3.12 và package import được

**Files:**
- Create: `.python-version`
- Create: `pyproject.toml`
- Create: `app/__init__.py`
- Create: `tests/unit/test_khoi_dong.py`
- Sinh ra: `uv.lock` (do `uv sync` tạo, phải commit)

**Interfaces:**
- Consumes: không có
- Produces: package `app` import được từ bất kỳ đâu; `app.__version__` kiểu `str`; lệnh `uv run pytest` chạy được

- [ ] **Step 1: Ghim Python 3.12**

```bash
echo "3.12" > .python-version
uv python install 3.12
```

Kiểm tra: `uv run python --version` phải in `Python 3.12.x`.

- [ ] **Step 2: Viết `pyproject.toml`**

```toml
[project]
name = "hoc-ai"
version = "0.1.0"
description = "App hoc tap de tro thanh AI Engineer"
requires-python = ">=3.12,<3.13"
dependencies = [
    "pydantic>=2.9",
    "pydantic-settings>=2.6",
]

[dependency-groups]
dev = [
    "pytest>=8.3",
    "pytest-cov>=6.0",
    "ruff>=0.8",
    "mypy>=1.13",
    "pre-commit>=4.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["app"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --strict-markers"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.12"
strict = true
files = ["app"]
```

Ghi chú: `files = ["app"]` nghĩa là mypy chỉ kiểm tra code chính, không kiểm tra test. Cố ý —
để không phải chú thích kiểu cho từng hàm test khi mới bắt đầu.

- [ ] **Step 3: Tạo thư mục và file rỗng cho package**

`hatchling` cần thư mục `app/` tồn tại trước khi cài, nên tạo file rỗng trước:

```bash
mkdir -p app/core tests/unit
touch app/__init__.py app/core/__init__.py
```

- [ ] **Step 4: Cài phụ thuộc**

```bash
uv sync
```

Kết quả mong đợi: tạo `.venv/` và `uv.lock`, in danh sách package đã cài.

- [ ] **Step 5: Viết test thất bại**

Tạo `tests/unit/test_khoi_dong.py`:

```python
"""Kiem tra package app cai dat va import duoc."""

from app import __version__


def test_app_co_so_phien_ban():
    assert __version__ == "0.1.0"
```

- [ ] **Step 6: Chạy test để xác nhận nó đỏ**

Run: `uv run pytest tests/unit/test_khoi_dong.py -v`
Expected: FAIL với `ImportError: cannot import name '__version__' from 'app'`

- [ ] **Step 7: Viết code tối thiểu cho test xanh**

Ghi vào `app/__init__.py`:

```python
"""App hoc tap de tro thanh AI Engineer."""

__version__ = "0.1.0"
```

- [ ] **Step 8: Chạy lại test**

Run: `uv run pytest tests/unit/test_khoi_dong.py -v`
Expected: PASS — `1 passed`

- [ ] **Step 9: Commit**

```bash
git add .python-version pyproject.toml uv.lock app/ tests/
git commit -m "feat: dung moi truong Python 3.12 va package app"
```

---

### Task 3: Module cấu hình có kiểu

**Files:**
- Create: `app/core/config.py`
- Create: `tests/unit/test_config.py`
- Create: `.env.example`

**Interfaces:**
- Consumes: `app` package từ Task 2
- Produces:
  - `class Settings(BaseSettings)` với các trường: `llm_provider: Literal["deepseek","ollama","fake"]`, `deepseek_api_key: str`, `deepseek_base_url: str`, `deepseek_model: str`, `ollama_base_url: str`, `ollama_model: str`, `embedding_model: str`, `embedding_device: Literal["cuda","cpu"]`, `data_dir: Path`, `sqlite_path: Path`, `qdrant_url: str`, `qdrant_collection: str`, `log_level: Literal["DEBUG","INFO","WARNING","ERROR"]`
  - `def lay_cau_hinh() -> Settings` — hàm mọi module khác gọi để lấy cấu hình
  - Mọi chặng sau đều import từ đây. Không chặng nào được đọc `os.environ` trực tiếp.

- [ ] **Step 1: Viết test thất bại**

Tạo `tests/unit/test_config.py`:

```python
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
    assert s.deepseek_api_key == "sk-test-123"


def test_bao_loi_khi_chon_deepseek_ma_thieu_khoa():
    with pytest.raises(ValidationError, match="DEEPSEEK_API_KEY"):
        Settings(_env_file=None, llm_provider="deepseek", deepseek_api_key="")


def test_bao_loi_khi_chon_provider_khong_ton_tai():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, llm_provider="chatgpt")


def test_lay_cau_hinh_tra_ve_doi_tuong_settings():
    assert isinstance(lay_cau_hinh(), Settings)
```

- [ ] **Step 2: Chạy test để xác nhận nó đỏ**

Run: `uv run pytest tests/unit/test_config.py -v`
Expected: FAIL với `ModuleNotFoundError: No module named 'app.core.config'`

- [ ] **Step 3: Viết `app/core/config.py`**

```python
"""Cau hinh toan app, doc tu bien moi truong hoac file .env.

Moi module khac phai lay cau hinh qua ham lay_cau_hinh(), khong duoc doc
os.environ truc tiep. Nho vay moi thiet lap deu co kieu va duoc kiem tra
ngay luc khoi dong thay vi hong am tham luc chay.
"""

from pathlib import Path
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Toan bo thiet lap cua app."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- LLM ---
    llm_provider: Literal["deepseek", "ollama", "fake"] = "fake"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"

    # --- Embedding ---
    embedding_model: str = "intfloat/multilingual-e5-base"
    embedding_device: Literal["cuda", "cpu"] = "cuda"

    # --- Luu tru ---
    data_dir: Path = Path("data")
    sqlite_path: Path = Path("data/hocai.db")
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "lessons"

    # --- Van hanh ---
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    @model_validator(mode="after")
    def _kiem_tra_khoa_api(self) -> "Settings":
        if self.llm_provider == "deepseek" and not self.deepseek_api_key:
            raise ValueError(
                "Chon LLM_PROVIDER=deepseek thi phai dat DEEPSEEK_API_KEY trong file .env"
            )
        return self


def lay_cau_hinh() -> Settings:
    """Tra ve cau hinh doc tu moi truong hien tai."""
    return Settings()
```

- [ ] **Step 4: Chạy test để xác nhận nó xanh**

Run: `uv run pytest tests/unit/test_config.py -v`
Expected: PASS — `5 passed`

- [ ] **Step 5: Tạo `.env.example`**

File này **an toàn để commit** vì không chứa giá trị thật. `.gitignore` đã có dòng
`!.env.example` để không bị chặn nhầm.

```bash
# Sao chep file nay thanh .env roi dien gia tri that:
#   cp .env.example .env
# File .env KHONG BAO GIO duoc commit.

# --- LLM ---
# fake = khong goi mang (dung cho test)
# deepseek = goi API that
# ollama = chay model tren may
LLM_PROVIDER=fake

DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

# --- Embedding ---
EMBEDDING_MODEL=intfloat/multilingual-e5-base
EMBEDDING_DEVICE=cuda

# --- Luu tru ---
DATA_DIR=data
SQLITE_PATH=data/hocai.db
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=lessons

# --- Van hanh ---
LOG_LEVEL=INFO
```

- [ ] **Step 6: Xác nhận `.env.example` không bị `.gitignore` chặn**

Run: `git check-ignore .env.example; echo "exit=$?"`
Expected: `exit=1` (nghĩa là **không** bị chặn — đúng ý)

Nếu ra `exit=0` thì `.gitignore` đang chặn nhầm, kiểm tra lại dòng `!.env.example`.

**Chú ý — đừng thêm cờ `-v` vào lệnh này.** Với một file chưa commit khớp pattern phủ định
(`!.env.example`), `git check-ignore -v` in ra pattern đó và trả về **exit 0**, dù file thật
sự *không* bị chặn. Không có `-v` thì mã thoát mới phản ánh đúng "có bị chặn hay không".
Kiểm chứng trên git 2.53:

```
git check-ignore -v .env.example   ->  .gitignore:2:!.env.example   .env.example   exit=0
git check-ignore    .env.example   ->  (khong in gi)                              exit=1
```

Đây là một ví dụ đúng nghĩa cho Mục 7 của bài học: mã thoát là hợp đồng, và một cờ tưởng
như chỉ để "in chi tiết hơn" lại đổi luôn hợp đồng đó.

- [ ] **Step 7: Commit**

```bash
git add app/core/config.py tests/unit/test_config.py .env.example
git commit -m "feat: them module cau hinh co kieu"
```

---

### Task 4: Lệnh `doctor` kiểm tra môi trường

**Files:**
- Create: `app/core/doctor.py`
- Create: `app/__main__.py`
- Create: `tests/unit/test_doctor.py`

**Interfaces:**
- Consumes: `Settings` và `lay_cau_hinh()` từ Task 3
- Produces:
  - `@dataclass(frozen=True) class KetQua` — trường `ten: str`, `dat: bool`, `chi_tiet: str`, `bat_buoc: bool = True`
  - `@dataclass(frozen=True) class BaoCao` — trường `ket_qua: list[KetQua]`; phương thức `tat_ca_dat() -> bool`, `dinh_dang() -> str`
  - `def kiem_tra_python(phien_ban: tuple[int, int]) -> KetQua`
  - `def kiem_tra_lenh(ten: str, bat_buoc: bool = True) -> KetQua`
  - `def chay_kiem_tra(settings: Settings | None = None) -> BaoCao`
  - `def main(argv: list[str] | None = None) -> int` trong `app/__main__.py`

- [ ] **Step 1: Viết test thất bại**

Tạo `tests/unit/test_doctor.py`:

```python
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
    bc = BaoCao(
        [
            KetQua("a", True, "ok", bat_buoc=True),
            KetQua("b", False, "chua cai", bat_buoc=False),
        ]
    )
    assert bc.tat_ca_dat() is True


def test_bao_cao_truot_khi_muc_bat_buoc_truot():
    bc = BaoCao([KetQua("a", False, "hong", bat_buoc=True)])
    assert bc.tat_ca_dat() is False


def test_dinh_dang_hien_thi_moi_muc_tren_mot_dong():
    bc = BaoCao(
        [
            KetQua("a", True, "ok"),
            KetQua("b", False, "chua cai"),
        ]
    )
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
```

- [ ] **Step 2: Chạy test để xác nhận nó đỏ**

Run: `uv run pytest tests/unit/test_doctor.py -v`
Expected: FAIL với `ModuleNotFoundError: No module named 'app.core.doctor'`

- [ ] **Step 3: Viết `app/core/doctor.py`**

```python
"""Kiem tra moi truong may co du dieu kien chay app khong.

Cac ham kiem tra nhan tham so dau vao thay vi tu doc trang thai he thong.
Do la ly do chung test duoc: muon thu truong hop Python 3.14 thi chi can
truyen (3, 14) vao, khong can cai Python 3.14 that.
"""

import platform
import shutil
import sys
from dataclasses import dataclass

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
```

Thêm import ở đầu file, ngay trên dòng `from app.core.config import Settings`:

```python
from pydantic import ValidationError
```

- [ ] **Step 4: Chạy test để xác nhận nó xanh**

Run: `uv run pytest tests/unit/test_doctor.py -v`
Expected: PASS — `11 passed`

- [ ] **Step 5: Viết test cho điểm vào dòng lệnh**

Làm hai việc trong `tests/unit/test_doctor.py`.

**Việc 1 — thêm dòng import vào khối import ở ĐẦU file**, ngay trên `from app.core.doctor import (`:

```python
from app.__main__ import main
```

Đặt ở đầu file chứ không phải giữa file. Python cho phép `import` ở bất cứ đâu, nhưng quy ước
là gom hết lên đầu, và ruff sẽ báo lỗi `E402 module level import not at top of file` nếu
không — Task 5 sẽ bật ruff và bắt được ngay.

**Việc 2 — thêm hai hàm test vào cuối file:**

```python
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
```

- [ ] **Step 6: Chạy test để xác nhận nó đỏ**

Run: `uv run pytest tests/unit/test_doctor.py -v`
Expected: FAIL với `ModuleNotFoundError: No module named 'app.__main__'`

Vì import nằm ở đầu file, đây là **lỗi thu thập test** (collection error) — pytest không chạy
được file nào cả, kể cả 11 test đã xanh trước đó. Đó là màu đỏ đúng: module chưa tồn tại thì
cả file không import nổi.

- [ ] **Step 7: Viết `app/__main__.py`**

```python
"""Diem vao dong lenh cua app.

Lop nay chi lam mot viec: chuyen doi so dong lenh thanh loi goi ham.
Khong chua logic nghiep vu nao.
"""

import argparse
import sys

from app.core.doctor import chay_kiem_tra


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="app",
        description="App hoc tap de tro thanh AI Engineer",
    )
    parser.add_argument(
        "lenh",
        choices=["doctor"],
        help="doctor: kiem tra moi truong may",
    )
    args = parser.parse_args(argv)

    if args.lenh == "doctor":
        bao_cao = chay_kiem_tra()
        print(bao_cao.dinh_dang())
        return 0 if bao_cao.tat_ca_dat() else 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 8: Chạy toàn bộ test**

Run: `uv run pytest -v`
Expected: PASS — `19 passed` (1 khởi động + 5 config + 13 doctor)

- [ ] **Step 9: Chạy thử lệnh thật**

Run: `uv run python -m app doctor`

Expected: in ra bảng tương tự

```
OK    Python: dang chay 3.12
OK    git: /usr/bin/git
BO QUA docker: chua cai
OK    He dieu hanh: Linux-7.0.0-29-generic-x86_64-with-glibc2.41
OK    Cau hinh: doc duoc
OK    LLM provider: fake
OK    Embedding device: cuda
```

Dòng `docker` hiện `BO QUA` là đúng — Chặng 4 mới cần.

Kiểm tra mã thoát, nối với Mục 7 của bài học:

```bash
uv run python -m app doctor; echo "ma thoat = $?"
```

Expected: `ma thoat = 0`

- [ ] **Step 10: Commit**

```bash
git add app/core/doctor.py app/__main__.py tests/unit/test_doctor.py
git commit -m "feat: them lenh doctor kiem tra moi truong"
```

---

### Task 5: Lint, kiểm tra kiểu, và hàng rào chặn lộ khoá

**Files:**
- Create: `.pre-commit-config.yaml`
- Modify: các file `app/**.py` nếu ruff hoặc mypy báo lỗi

**Interfaces:**
- Consumes: cấu hình `[tool.ruff]` và `[tool.mypy]` đã đặt trong `pyproject.toml` ở Task 2
- Produces: lệnh `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy` đều sạch; hook `pre-commit` chạy tự động mỗi lần commit

- [ ] **Step 1: Chạy ruff lần đầu và sửa hết lỗi**

```bash
uv run ruff check . --fix
uv run ruff format .
uv run ruff check .
```

Expected sau cùng: `All checks passed!`

- [ ] **Step 2: Chạy mypy và sửa hết lỗi**

```bash
uv run mypy
```

Expected: `Success: no issues found in N source files`

Nếu báo lỗi thiếu stub cho `pydantic_settings`, thêm vào `pyproject.toml`:

```toml
[[tool.mypy.overrides]]
module = "pydantic_settings.*"
ignore_missing_imports = true
```

- [ ] **Step 3: Viết script chặn `.env`**

Tách ra file riêng thay vì nhồi lệnh bash vào YAML — lồng dấu nháy trong YAML rất dễ vỡ, và
file riêng thì đọc được, sửa được, chạy tay để thử được.

Tạo `scripts/chan-env.sh`:

```bash
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
```

Cấp quyền chạy:

```bash
mkdir -p scripts
chmod +x scripts/chan-env.sh
```

Thử tay để chắc nó chạy được (chưa có gì trong vùng chờ nên phải im lặng và trả về 0):

```bash
./scripts/chan-env.sh; echo "ma thoat = $?"
```

Expected: `ma thoat = 0`

- [ ] **Step 4: Viết `.pre-commit-config.yaml`**

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-merge-conflict
      - id: check-added-large-files
        args: ["--maxkb=1000"]
      - id: detect-private-key

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: local
    hooks:
      - id: chan-file-env
        name: Chan commit file .env
        entry: scripts/chan-env.sh
        language: script
        pass_filenames: false
```

Ghi chú: mypy **không** đặt trong pre-commit vì nó chạy trong môi trường cô lập riêng và hay
báo lỗi giả về phụ thuộc. Mypy chạy ở CI (Task 6) và chạy tay bằng `uv run mypy`.

- [ ] **Step 5: Cài hook**

```bash
uv run pre-commit install
```

Expected: `pre-commit installed at .git/hooks/pre-commit`

- [ ] **Step 6: Chạy hook trên toàn bộ file hiện có**

```bash
uv run pre-commit run --all-files
```

Lần đầu có thể sửa khoảng trắng thừa và dòng cuối file. Nếu hook sửa file thì chạy lại cho
đến khi tất cả `Passed`.

- [ ] **Step 7: Kiểm chứng hàng rào chặn khoá riêng tư thật sự hoạt động**

Tạo file giả và cố tình commit:

```bash
printf -- "-----BEGIN RSA PRIVATE KEY-----\ngiadinhthoi\n" > /tmp/khoa-gia.pem
cp /tmp/khoa-gia.pem ./khoa-gia.pem
git add khoa-gia.pem
git commit -m "test: thu commit khoa rieng tu"
```

Expected: commit **bị chặn**, hook `detect-private-key` báo `Failed`.

Dọn sạch:

```bash
git reset HEAD khoa-gia.pem
rm khoa-gia.pem /tmp/khoa-gia.pem
```

- [ ] **Step 8: Kiểm chứng hàng rào chặn file `.env` thật sự hoạt động**

```bash
cp .env.example .env
git add -f .env
git commit -m "test: thu commit file .env"
```

Expected: commit **bị chặn** với thông báo `LOI: dang co gang commit file .env - huy commit`.

Dọn sạch (giữ lại `.env` để dùng, chỉ bỏ khỏi vùng chờ commit):

```bash
git reset HEAD .env
git status --short
```

Expected: `.env` **không** xuất hiện trong `git status` (vì `.gitignore` chặn).

- [ ] **Step 9: Commit**

```bash
git add .pre-commit-config.yaml scripts/chan-env.sh pyproject.toml
git commit -m "chore: them ruff, mypy va pre-commit chan lo khoa"
```

Nếu hook sửa file lúc commit, chạy `git add -u` rồi commit lại — đó là hoạt động bình thường.

---

### Task 6: CI trên GitHub Actions

**Files:**
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: `uv.lock` từ Task 2, cấu hình ruff/mypy từ Task 2 và 5
- Produces: workflow tên `CI` với job `kiem-tra`, chạy trên mọi push vào `main` và mọi pull request

- [ ] **Step 1: Tạo thư mục**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Viết `.github/workflows/ci.yml`**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  kiem-tra:
    runs-on: ubuntu-latest
    steps:
      - name: Lay ma nguon
        uses: actions/checkout@v4

      - name: Cai uv
        uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true

      - name: Cai Python 3.12
        run: uv python install 3.12

      - name: Cai phu thuoc dung uv.lock
        run: uv sync --locked

      - name: Lint
        run: uv run ruff check .

      - name: Kiem tra dinh dang
        run: uv run ruff format --check .

      - name: Kiem tra kieu
        run: uv run mypy

      - name: Chay test
        run: uv run pytest --cov=app --cov-report=term-missing
```

`uv sync --locked` bắt CI dùng đúng phiên bản ghi trong `uv.lock`. Nếu ai đó sửa
`pyproject.toml` mà quên cập nhật lock, CI sẽ đỏ — đúng ý.

- [ ] **Step 3: Chạy thử toàn bộ chuỗi CI ở máy trước khi đẩy lên**

Chạy đúng thứ tự CI sẽ chạy:

```bash
uv sync --locked && \
uv run ruff check . && \
uv run ruff format --check . && \
uv run mypy && \
uv run pytest --cov=app --cov-report=term-missing
```

Expected: cả 5 lệnh đều thành công, pytest in bảng độ phủ.

Nếu `uv sync --locked` báo lock lệch, chạy `uv lock` rồi thử lại.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/ci.yml uv.lock
git commit -m "ci: them workflow chay lint, mypy va test"
```

---

### Task 7: Đẩy lên GitHub và làm Pull Request đầu tiên

**Files:**
- Create: `README.md`

**Interfaces:**
- Consumes: toàn bộ kết quả Task 1–6
- Produces: repo GitHub `ninhhfinn/hoc-ai` có CI xanh; một PR đã merge; nhánh `main` được bảo vệ khỏi commit trực tiếp bằng thói quen làm việc

- [ ] **Step 1: Viết `README.md`**

````markdown
# hoc-ai

App học tập cá nhân để trở thành AI Engineer — vừa là công cụ học, vừa là dự án portfolio.

Nạp tài liệu (PDF, Markdown, URL) vào app; app trả lời câu hỏi kèm trích nguồn, sinh quiz,
chấm bài, phỏng vấn thử, và tự đo chất lượng của chính nó bằng một bộ eval.

## Trạng thái

Đang ở **Chặng 0 — Nền móng**. Xem lộ trình 9 chặng trong
[spec thiết kế](docs/superpowers/specs/2026-08-08-app-hoc-ai-engineering-design.md).

## Yêu cầu

- Python 3.12 (cài tự động qua `uv`)
- [uv](https://docs.astral.sh/uv/)
- Git

## Chạy thử

```bash
uv sync
cp .env.example .env
uv run python -m app doctor
```

## Phát triển

```bash
uv run pytest                  # chay test
uv run ruff check .            # lint
uv run mypy                    # kiem tra kieu
uv run pre-commit install      # cai hook (chi lam mot lan)
```

## Tài liệu

- [Spec thiết kế](docs/superpowers/specs/2026-08-08-app-hoc-ai-engineering-design.md)
- [Bài học](docs/lessons/)
````

- [ ] **Step 2: Commit README lên `main`**

```bash
git add README.md
git commit -m "docs: them README"
```

- [ ] **Step 3: Tạo repo trên GitHub và đẩy lên**

```bash
gh repo create hoc-ai --public --source=. --remote=origin --push
```

Expected: in ra URL dạng `https://github.com/ninhhfinn/hoc-ai`.

Ghi chú: chọn `--public` để lịch sử commit và CI xanh trở thành bằng chứng nhà tuyển dụng
xem được. Hàng rào chặn lộ khoá đã dựng ở Task 5 nên an toàn. Muốn đổi thành riêng tư:
`gh repo edit --visibility private`.

- [ ] **Step 4: Xác nhận CI chạy và xanh**

```bash
gh run watch
```

Expected: job `kiem-tra` kết thúc với dấu ✓.

Nếu đỏ: đọc log bằng `gh run view --log-failed`, sửa, commit, đẩy lại. Đây chính là kỹ năng
"đọc log" mà JD nhắc — đừng đoán, hãy đọc.

- [ ] **Step 5: Tạo nhánh cho thay đổi tiếp theo**

```bash
git switch -c them-lenh-phien-ban
```

- [ ] **Step 6: Viết test thất bại cho tính năng mới**

Thêm vào `tests/unit/test_doctor.py`:

```python
def test_main_lenh_version_in_so_phien_ban(capsys):
    from app import __version__

    ma_thoat = main(["version"])
    captured = capsys.readouterr()
    assert __version__ in captured.out
    assert ma_thoat == 0
```

- [ ] **Step 7: Chạy test để xác nhận nó đỏ**

Run: `uv run pytest tests/unit/test_doctor.py::test_main_lenh_version_in_so_phien_ban -v`
Expected: FAIL — argparse từ chối `version` vì chưa nằm trong `choices`

- [ ] **Step 8: Sửa `app/__main__.py` cho test xanh**

Đổi dòng `choices` và thêm nhánh xử lý:

```python
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
```

Thêm import ở đầu file:

```python
from app import __version__
```

- [ ] **Step 9: Chạy toàn bộ test**

Run: `uv run pytest -v`
Expected: tất cả PASS, `0 failed`

- [ ] **Step 10: Commit và đẩy nhánh**

```bash
git add app/__main__.py tests/unit/test_doctor.py
git commit -m "feat: them lenh version"
git push -u origin them-lenh-phien-ban
```

- [ ] **Step 11: Mở Pull Request**

```bash
gh pr create \
  --title "Them lenh version" \
  --body "Them lenh \`python -m app version\` in so phien ban.

Kem test cho ca truong hop thanh cong.

Doi chieu: JD yeu cau Git workflow va Merge Request. Day la PR dau tien cua du an."
```

- [ ] **Step 12: Chờ CI trên PR xanh**

```bash
gh pr checks --watch
```

Expected: `kiem-tra` ✓

- [ ] **Step 13: Tự review PR của chính mình**

```bash
gh pr diff
```

Đọc từng dòng và tự hỏi ba câu:

1. Có dòng nào thừa không?
2. Test có thật sự kiểm tra hành vi, hay chỉ kiểm tra code chạy không lỗi?
3. Người lạ đọc diff này có hiểu ngay mục đích không?

Đây là bài tập chính của Task 7 — không phải thao tác `gh`, mà là **thói quen đọc lại code
của mình bằng con mắt người khác**.

- [ ] **Step 14: Merge và dọn nhánh**

```bash
gh pr merge --squash --delete-branch
git switch main
git pull
```

- [ ] **Step 15: Xác nhận trạng thái cuối cùng**

```bash
git log --oneline -8
uv run pytest
uv run python -m app doctor
uv run python -m app version
gh run list --limit 3
```

Expected:
- lịch sử commit có commit merge từ PR
- toàn bộ test xanh
- `doctor` in bảng kiểm tra
- `version` in `0.1.0`
- CI gần nhất trên `main` màu xanh

---

## Tiêu chí hoàn thành Chặng 0

Đánh dấu xong khi tất cả đúng:

- [ ] `uv run python --version` in `Python 3.12.x`
- [ ] `uv run pytest` xanh, không có test nào đỏ hay bị bỏ qua
- [ ] `uv run ruff check .` và `uv run ruff format --check .` sạch
- [ ] `uv run mypy` sạch
- [ ] `uv run python -m app doctor` chạy được và in bảng kiểm tra
- [ ] Thử commit khoá riêng tư → **bị chặn**
- [ ] Thử commit `.env` → **bị chặn**
- [ ] CI trên GitHub xanh ở nhánh `main`
- [ ] Có ít nhất một PR đã merge
- [ ] Đọc xong `docs/lessons/lesson-00-nen-mong.md` và trả lời miệng được 6 câu hỏi ở Task 1 Step 3

## Chặng tiếp theo

Chặng 1 — API đầu tiên (FastAPI, Pydantic, HTTP, async). Plan riêng, viết khi Chặng 0 xong,
vì cách tổ chức router phụ thuộc vào việc `Settings` dùng ra sao trong thực tế.
