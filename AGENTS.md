# AGENTS.md — Hướng dẫn cho agent làm việc trên repo này

File này dành cho AI agent (DeepSeek, Qwen, GLM, Kimi, Claude…) được giao việc trên repo
`hoc-ai`. Đọc hết file này trước khi gõ dòng lệnh đầu tiên.

---

## 1. Bối cảnh

`hoc-ai` là app RAG cá nhân bằng tiếng Việt, vừa là công cụ học vừa là dự án portfolio để trở
thành AI Engineer. Nạp tài liệu (PDF, Markdown, URL) → app trả lời có trích nguồn, sinh quiz,
chấm bài, và tự đo chất lượng bằng một bộ eval.

- **Ngăn xếp:** Python 3.12 (ghim qua `uv`), Pydantic 2, pytest, ruff, mypy strict, pre-commit,
  GitHub Actions.
- **Trạng thái:** Chặng 0 (Nền móng) đã xong. Đang ở đầu Chặng 1 (API đầu tiên — FastAPI).
- **Lộ trình:** 9 chặng, mỗi chặng kết thúc bằng một app chạy được.

Chi tiết ở hai file sau — **đọc khi cần, đừng chép lại nội dung của chúng đi đâu**:

- Kiến trúc và quyết định thiết kế:
  `docs/superpowers/specs/2026-08-08-app-hoc-ai-engineering-design.md`
- Tổng quan ngắn: `docs/project-overview.md`
- Bản ghi Chặng 0 và nguồn gốc 8 nhiệm vụ dưới đây:
  `docs/superpowers/plans/2026-08-08-chang-00-nen-mong.md`

---

## 2. Luật bắt buộc

Vi phạm bất kỳ dòng nào dưới đây thì PR bị từ chối, không cần đọc code.

1. **Một nhiệm vụ = một nhánh = một PR.** Không gộp hai nhiệm vụ vào một PR.
2. **Không tạo file nào ngoài file mà nhiệm vụ nêu tên.** Không thêm README phụ, không thêm
   file ghi chú, không thêm script tiện ích.
3. **Không thêm dependency** vào `pyproject.toml`. Cả 8 nhiệm vụ dưới đây đều không cần thư
   viện mới. Nếu bạn nghĩ là cần — bạn đang làm sai hướng, dừng lại và báo.
4. **Không đụng vào:** `.env`, `uv.lock`, `docs/superpowers/specs/`,
   `docs/superpowers/plans/`. Hai thư mục sau là bản ghi lịch sử, không phải tài liệu sống.
5. **Không sửa hay xoá test cho hết đỏ.** Test đỏ nghĩa là code sai, không phải test sai. Nếu
   một nhiệm vụ *bắt buộc* phải sửa test cũ, nhiệm vụ đó nói rõ ở mục "Bẫy".
6. **Không `git push --force`. Không commit thẳng lên `main`.**
7. **Quy ước ngôn ngữ:** định danh và comment trong code viết bằng **tiếng Việt không dấu**
   (`chay_kiem_tra`, `lay_cau_hinh`, `# Chan moi no luc commit file .env`). Tài liệu `.md`
   viết tiếng Việt **có dấu**. Đây là quy ước đang có sẵn, giữ nguyên, đừng "chuẩn hoá" sang
   tiếng Anh.
8. **Định dạng:** dòng tối đa 100 ký tự. ruff bật `E, F, I, UP, B, SIM`. mypy chạy `strict`.
9. **Không đạt được tiêu chí "Xong khi" thì dừng và báo rõ vướng ở đâu.** Không tự mở rộng
   phạm vi để lách. Báo cáo trung thực một nhiệm vụ chưa xong có giá trị hơn một PR đoán mò.
10. **Không đổi cấu trúc file trong `docs/lessons/`.** Các file bài học chỉ dùng heading `#`
    và `##`, mỗi mục dài 534–936 từ, không tham chiếu chéo giữa các mục. Đây **không phải**
    tình cờ: Chặng 3 sẽ chunk tài liệu theo `##` để nạp vào vector store, và khuôn hiện tại
    chạy được ngay. Sửa chữ nghĩa bên trong một mục thì được; thêm `###`, gộp mục, tách mục,
    hay đổi thứ tự heading thì không.
11. **Không khẳng định điều gì về thế giới bên ngoài mà không chạy lệnh kiểm chứng.** Đây là
    lỗi nghiêm trọng nhất mà review Chặng 0 tìm ra: một câu sai về phiên bản thư viện đi thẳng
    từ spec qua plan vào bài học vì không lệnh nào kiểm được nó. Mọi mệnh đề dạng "thư viện X
    phiên bản Y" phải kèm output lệnh, kèm ngày.

---

## 3. Lệnh kiểm tra

Chạy đủ **6 lệnh** này trước khi báo xong. Dán nguyên output vào PR.

```bash
uv sync
uv run ruff check . && uv run ruff format --check .
uv run mypy
uv run pytest
uv run python -m app doctor
uv run pre-commit run --all-files
```

Lưu ý: `uv run python -m app doctor` trả mã thoát `1` nếu máy thiếu thứ gì bắt buộc — trên máy
chưa cài `docker` thì vẫn là `0` vì docker không bắt buộc ở giai đoạn này. Đọc bảng nó in ra,
đừng chỉ nhìn mã thoát.

---

## 4. Cây thư mục hiện tại

Đây là **toàn bộ** file đang tồn tại (bỏ qua `.git/`, `.venv/`, các thư mục cache).

```
ApphocAIengineering/
├── app/
│   ├── __init__.py               # chi giu __version__ = "0.1.0"
│   ├── __main__.py               # CLI: lenh `doctor` va `version`.
│   │                             #   Lop mong, khong chua logic nghiep vu
│   └── core/
│       ├── __init__.py           # rong
│       ├── config.py             # Settings (Pydantic BaseSettings) doc .env
│       │                         #   + lay_cau_hinh() -> Settings
│       └── doctor.py             # KetQua, BaoCao, kiem_tra_python,
│                                 #   kiem_tra_lenh, chay_kiem_tra
├── tests/
│   ├── conftest.py               # fixture autouse `moi_truong_sach`: xoa bien
│   │                             #   moi truong cua app + chdir sang tmp_path
│   └── unit/
│       ├── test_config.py        # 5 test cho Settings / lay_cau_hinh
│       ├── test_doctor.py        # 14 test cho doctor va main()
│       └── test_khoi_dong.py     # 1 test: package import duoc, co __version__
├── docs/
│   ├── lessons/
│   │   └── lesson-00-nen-mong.md # bai hoc Chang 0 (397 dong)
│   ├── project-overview.md       # tong quan ngan cho nguoi doc
│   └── superpowers/
│       ├── specs/
│       │   └── 2026-08-08-app-hoc-ai-engineering-design.md   # KHONG SUA
│       └── plans/
│           └── 2026-08-08-chang-00-nen-mong.md               # KHONG SUA
├── scripts/
│   └── chan-env.sh               # pre-commit hook: chan commit .env va .env.*
├── .github/workflows/ci.yml      # pre-commit -> ruff -> ruff format -> mypy
│                                 #   -> pytest --cov
├── .pre-commit-config.yaml       # pre-commit-hooks + ruff + chan-env.sh
├── pyproject.toml                # project, dependency, cau hinh ruff/mypy/pytest
├── uv.lock                       # khoa phien ban phu thuoc — KHONG SUA TAY
├── .python-version               # 3.12
├── .env.example                  # mau cau hinh (file .env that KHONG duoc commit)
├── .gitignore
├── LICENSE                       # MIT
└── README.md
```

**Quy mô hiện tại:** 5 file Python trong `app/`, 4 file test, tổng dưới 400 dòng code. Repo
nhỏ — đọc hết file liên quan trước khi sửa, đừng grep rồi đoán.

---

## 5. Cây thư mục đích

Đây là hình dạng cuối của dự án theo spec §5.3. Mục nào ghi `[chua co - Chang N]` là **chưa
tồn tại** và sẽ được tạo ở chặng tương ứng.

**Không tự tạo bất kỳ mục nào trong danh sách này.** Không báo lỗi "thiếu file". Không tạo
file rỗng hay stub để "chuẩn bị sẵn".

```
ApphocAIengineering/
├── app/
│   ├── core/
│   │   ├── config.py             # DA CO
│   │   ├── doctor.py             # DA CO
│   │   ├── models.py             # [chua co - Chang 3] Chunk, SearchHit,
│   │   │                         #   Completion, Citation
│   │   ├── chunking.py           # [chua co - Chang 3] cat doan ~500 token
│   │   ├── embedding.py          # [chua co - Chang 3] Embedder protocol
│   │   ├── vectorstore.py        # [chua co - Chang 3] VectorStore protocol
│   │   ├── retriever.py          # [chua co - Chang 3]
│   │   ├── prompts.py            # [chua co - Chang 3] template prompt
│   │   └── llm/                  # [chua co - Chang 2]
│   │       ├── base.py           #   LLMProvider protocol, Completion, gia tien
│   │       ├── deepseek.py
│   │       ├── ollama.py
│   │       └── fake.py           #   dung trong test, khong goi mang
│   ├── ingest/                   # [chua co - Chang 3] loaders.py, pipeline.py
│   ├── features/                 # [chua co] qa.py (C3), quiz.py (C5),
│   │                             #   interview.py (C7), grader.py (C8)
│   ├── api/                      # [chua co - Chang 1] main.py, routers/, errors.py
│   └── db/                       # [chua co - Chang 5] models.py, session.py,
│                                 #   migrations/
├── eval/                         # [chua co - Chang 6] golden/, metrics/,
│                                 #   configs/, run.py, reports/
├── web/                          # [chua co - Chang 5] templates/ (Jinja2), static/
├── exercises/                    # [chua co - Chang 8] bank bai tap + test
├── docker/                       # [chua co - Chang 4] Dockerfile,
│                                 #   docker-compose.yml, runner.Dockerfile
├── tests/
│   ├── unit/                     # DA CO
│   └── integration/              # [chua co - Chang 1]
└── docs/lessons/                 # lesson-00 DA CO; lesson-01..08 [chua co]
```

**Nguyên tắc phân lớp** (áp dụng khi chạm vào code, kể cả các nhiệm vụ nhỏ dưới đây):

- `core/` **không biết** FastAPI tồn tại → test được mà không cần chạy server.
- `features/` **không biết** DeepSeek tồn tại → chỉ gọi qua `LLMProvider`.
- `api/` chỉ chuyển đổi HTTP ↔ lời gọi hàm, không chứa logic nghiệp vụ.
- File vượt ~300 dòng là tín hiệu nó làm quá nhiều việc.

---

## 6. Hàng đợi nhiệm vụ

8 nhiệm vụ, lấy nguyên từ mục "Việc mang sang Chặng 1" của
`docs/superpowers/plans/2026-08-08-chang-00-nen-mong.md`. Xếp theo rủi ro tăng dần.

**Phụ thuộc:** N1, N2, N3 độc lập — làm song song được. **N4 phải xong trước N5** (cùng sửa
`app/core/config.py`). N6, N7, N8 độc lập.

Mỗi nhiệm vụ chỉ được chạm vào các file ghi ở mục "File được sửa". File nào không có tên trong
đó mà xuất hiện trong `git diff` là lỗi.

---

### N1 — Sửa hai chỗ chữ nghĩa trong bài học

Rủi ro: thấp nhất. Chỉ tài liệu, không đụng code.

**File được sửa:** `docs/lessons/lesson-00-nen-mong.md`

**Mục tiêu — chỗ 1** (khoảng dòng 123): câu hiện tại viết `sentence-transformers` "là gói
thuần Python nên chưa bao giờ phụ thuộc vào phiên bản Python". Câu này **nói quá**. Gói này
khai báo `requires_python >= 3.10` và phụ thuộc `torch`. Nó đúng ở mức *wheel tag*
(`py3-none-any` — file cài đặt không gắn với một phiên bản Python cụ thể), nhưng sai nếu đọc
theo nghĩa đen. Sửa cho chính xác, **giữ nguyên kết luận** của đoạn văn (kết luận là: ghim
3.12 không phải vì 3.14 hỏng).

**Mục tiêu — chỗ 2** (khoảng dòng 63–65): đoạn nói về `~0.6GB` VRAM có dòng "và Qwen2.5-7B đã"
bị ngắt sớm, ngắn hơn hẳn các dòng xung quanh. Gói lại các dòng cho đều, cùng độ rộng với phần
còn lại của file.

**Bẫy:**
- Đừng viết lại cả đoạn. Sửa đúng chỗ sai. `git diff` càng nhỏ càng dễ review.
- **Không đụng vào bất kỳ dòng heading nào** (xem Luật số 10). File này sẽ được chunk theo `##`
  ở Chặng 3. Chỉ sửa chữ bên trong đoạn văn.

**Xong khi:**
- `git diff --name-only` chỉ ra đúng một file.
- `git diff` không chứa dòng nào bắt đầu bằng `#` — chứng minh cấu trúc heading còn nguyên.
- `uv run pre-commit run --all-files` sạch.
- Đoạn văn đọc vẫn xuôi, kết luận không đổi.

---

### N2 — Thêm kiểm tra `nvidia-smi` vào doctor

**File được sửa:** `app/core/doctor.py`, `tests/unit/test_doctor.py`

**Mục tiêu:** thêm `kiem_tra_lenh("nvidia-smi", bat_buoc=False)` vào danh sách `muc` trong hàm
`chay_kiem_tra`.

**Vì sao:** `EMBEDDING_DEVICE=cuda` là giá trị mặc định trong `config.py` và `.env.example`.
Đến Chặng 3 khi nạp model embedding thật, cấu hình này sẽ nổ trên máy không có GPU. Lệnh
`doctor` tồn tại để cảnh báo trước những chuyện như vậy. Hàm `kiem_tra_lenh` đã có sẵn, chỉ
cần gọi thêm một lần.

**Bẫy:** **bắt buộc** `bat_buoc=False`. Để `True` là CI đỏ ngay lập tức — GitHub runner không
có GPU. Đây cũng là lý do `docker` đang để `bat_buoc=False`, xem dòng ngay trên.

**Xong khi:**
- `uv run python -m app doctor` in thêm một dòng cho `nvidia-smi`.
- Có test mới trong `tests/unit/test_doctor.py` khẳng định `nvidia-smi` có
  `bat_buoc is False` — theo đúng khuôn của `test_docker_khong_bat_buoc_o_chang_0` đã có.
- Toàn bộ 6 lệnh kiểm tra sạch.

---

### N3 — Nối cái seam đang bỏ không

**File được sửa:** `app/__main__.py`, `tests/unit/test_doctor.py`

**Mục tiêu:** `chay_kiem_tra(settings: Settings | None = None)` đã nhận tham số `settings`
nhưng `app/__main__.py` gọi rỗng, và không test nào truyền vào. Nối lại:
`__main__.py` lấy cấu hình rồi truyền vào.

**Vì sao:** Chặng 1 dựng FastAPI dependency sẽ dùng đúng pattern này
(`Depends(lay_cau_hinh)`). Cho `__main__.py` chạy trước một lần để pattern đó nhất quán.

**Bẫy nặng — đọc kỹ:** viết thẳng `chay_kiem_tra(lay_cau_hinh())` là **hỏng**.
`lay_cau_hinh()` ném `ValidationError` khi `.env` sai (ví dụ chọn `deepseek` mà thiếu khoá).
Nó ném *trước khi* luồng đi vào `chay_kiem_tra`, nên khối `try/except ValidationError` sẵn có
bên trong hàm đó không đỡ được. Kết quả: lệnh `doctor` chết đúng lúc nó cần chạy nhất —
docstring của `chay_kiem_tra` nói rõ nó tồn tại để chẩn đoán máy hỏng nên bản thân nó không
được chết vì máy hỏng.

Bắt lỗi ở `__main__.py` rồi truyền `None` để rơi về đúng đường cũ:

```python
try:
    settings = lay_cau_hinh()
except ValidationError:
    settings = None
bao_cao = chay_kiem_tra(settings)
```

**Xong khi:**
- Có test mới khẳng định: đặt `LLM_PROVIDER=deepseek` và `DEEPSEEK_API_KEY` rỗng
  (`monkeypatch.setenv`) thì `main(["doctor"])` trả về `1` và in dòng cấu hình trượt —
  **không ném exception**.
- Test `test_cau_hinh_hong_thi_bao_cao_chu_khong_nem_loi` đã có vẫn xanh (nó kiểm đường bên
  trong; test mới kiểm đường qua `main`).
- Toàn bộ 6 lệnh kiểm tra sạch.

---

### N4 — `deepseek_api_key` thành `pydantic.SecretStr`

**File được sửa:** `app/core/config.py`, `tests/unit/test_config.py`

**Mục tiêu:** đổi kiểu trường `deepseek_api_key` từ `str` sang `pydantic.SecretStr`.

**Vì sao:** hiện chưa lộ gì, nhưng `doctor.py` làm `str(loi)` rồi `print` ra stdout, và lỗi từ
`model_validator(mode="after")` có thể dump nguyên dict đầu vào. Chặng 1 thêm `structlog` sẽ
log cả object `Settings` — lúc đó `SecretStr` là thứ duy nhất đứng giữa khoá thật và file log.
Rẻ nhất là làm ngay khi mới có đúng một chỗ dùng.

**Bẫy — kiểm chứng trên pydantic 2.13.4 ngày 2026-08-12, đừng đoán lại:**

1. **Giá trị mặc định là chỗ nguy hiểm nhất.** Pydantic **không** validate giá trị mặc định
   (`validate_default=False` là mặc định), nên viết `deepseek_api_key: SecretStr = ""` sẽ để
   lại một `str` thô trong object, và `.get_secret_value()` sau đó nổ `AttributeError`. Phải
   viết `= SecretStr("")`. Kiểm chứng lại bằng:

   ```bash
   uv run python -c "
   from pydantic import BaseModel, SecretStr
   class M(BaseModel):
       k: SecretStr = ''
   print(type(M().k).__name__)   # in ra 'str', khong phai 'SecretStr'
   "
   ```

2. **Validator hiện tại KHÔNG vỡ — đừng sửa nó vì tưởng nó vỡ.** `SecretStr` có `__len__`, nên
   `not SecretStr("")` vẫn là `True` và `not self.deepseek_api_key` trong `_kiem_tra_khoa_api`
   vẫn chạy đúng sau khi đổi kiểu. Đổi sang `not self.deepseek_api_key.get_secret_value()` là
   **tuỳ chọn**, lý do là tường minh cho người đọc, không phải sửa lỗi. Làm hay không đều được,
   miễn `test_bao_loi_khi_chon_deepseek_ma_thieu_khoa` vẫn xanh.

3. **`test_doc_duoc_tu_bien_moi_truong` sẽ đỏ.** Nó khẳng định
   `s.deepseek_api_key == "sk-test-123"`, mà giá trị truyền vào bị ép thành `SecretStr`. Đây là
   **trường hợp duy nhất trong 8 nhiệm vụ được phép sửa test cũ** — đổi sang
   `.get_secret_value()`.

**Xong khi:**
- Có test mới khẳng định `repr(s)` và `str(s)` **không** chứa chuỗi khoá thật.
- Test `test_bao_loi_khi_chon_deepseek_ma_thieu_khoa` vẫn xanh (chứng minh hàng rào chưa mất
  tác dụng).
- `uv run mypy` sạch — đây là chỗ mypy strict sẽ bắt lỗi nếu sót một chỗ.
- Toàn bộ 6 lệnh kiểm tra sạch.

---

### N5 — Cache cấu hình (cặp đi liền, làm thiếu một nửa là sinh bug)

**Làm sau khi N4 đã merge.**

**File được sửa:** `app/core/config.py`, `tests/conftest.py`, `tests/unit/test_config.py`

**Mục tiêu:** thêm `@lru_cache` cho `lay_cau_hinh()`.

**Vì sao:** hiện mỗi lần gọi là một lần đọc file `.env` từ đĩa. Với FastAPI
`Depends(lay_cau_hinh)` ở Chặng 1, việc đó thành một lần I/O trên **mỗi request**.

**Bẫy — đây là lý do nhiệm vụ này gọi là "cặp đi liền":** cache phá mọi test dùng
`monkeypatch.setenv`. Test thứ hai sẽ nhận lại đúng object mà test thứ nhất đã tạo, và sai
một cách âm thầm — test vẫn xanh hoặc đỏ tuỳ thứ tự chạy, cực khó truy. Bắt buộc thêm
`lay_cau_hinh.cache_clear()` vào fixture `moi_truong_sach` trong `tests/conftest.py`,
**trong cùng PR này**. Làm một nửa còn tệ hơn không làm.

**Xong khi:**
- Có test khẳng định hai lần gọi `lay_cau_hinh()` liên tiếp trả về **cùng một** object
  (dùng `is`, không dùng `==`).
- Có test dùng `monkeypatch.setenv` rồi gọi `lay_cau_hinh()` và thấy giá trị mới — chứng minh
  `cache_clear()` trong fixture thực sự có tác dụng.
- `uv run pytest` xanh **và** `uv run pytest tests/unit/test_config.py` chạy riêng cũng xanh.
  Chạy riêng một file là cách phát hiện test đang ăn nhờ trạng thái do test khác để lại — đúng
  loại hỏng mà cache gây ra.
- Toàn bộ 6 lệnh kiểm tra sạch.

---

### N6 — Một nguồn sự thật cho số phiên bản

**File được sửa:** `app/__init__.py`, `tests/unit/test_khoi_dong.py`

**Mục tiêu:** `pyproject.toml` và `app/__init__.py` đang giữ hai bản `"0.1.0"` rời nhau, và
`test_khoi_dong.py` khẳng định literal `"0.1.0"`. Ba chỗ này sẽ lệch nhau ngay lần bump version
đầu tiên. Chuyển `__version__` sang `importlib.metadata.version("hoc-ai")`, lấy
`pyproject.toml` làm nguồn duy nhất.

**Bẫy:**
1. `importlib.metadata.version` ném `PackageNotFoundError` nếu package chưa được cài. Chạy qua
   `uv run` thì package đã cài editable nên không sao. **Đừng bọc `try/except` nuốt lỗi** rồi
   trả về một chuỗi mặc định — làm thế là dựng lại đúng cái nguồn sự thật thứ hai mà nhiệm vụ
   này đang đi xoá.
2. Test **không được** viết thành `__version__ == importlib.metadata.version("hoc-ai")`. Phép
   so sánh đó tự quy chiếu, luôn đúng, không kiểm được gì.
3. **Không bump số phiên bản để thử.** `uv.lock` cũng ghi `version = "0.1.0"` (dòng 120), nên
   sửa `pyproject.toml` rồi `uv sync` sẽ làm `uv.lock` đổi theo — vi phạm Luật 4. Việc bump
   thật để người chủ repo làm ở lần phát hành tiếp theo.

**Xong khi:**
- `uv run python -m app version` in `0.1.0`.
- Test khẳng định `__version__` khớp dạng `X.Y.Z` (regex) chứ không khẳng định literal `0.1.0`.
- Dán output hai lệnh sau vào PR, cho thấy hai số khớp nhau và chỉ còn một chỗ khai báo:

  ```bash
  grep -n '^version' pyproject.toml
  uv run python -c "import importlib.metadata as m; print(m.version('hoc-ai'))"
  grep -rn '0\.1\.0' app/ tests/    # phai KHONG con dong nao
  ```
- Toàn bộ 6 lệnh kiểm tra sạch; `git diff` không đụng `pyproject.toml` hay `uv.lock`.

---

### N7 — Chặn `.env` bị track, ở CI

**File được sửa:** `.github/workflows/ci.yml`

**Mục tiêu:** thêm một bước CI độc lập, chặn trường hợp có file `.env` (hoặc `.env.local`,
`.env.prod`…) bị track trong git.

**Vì sao bước hiện có không đủ:** `ci.yml` đang chạy `uv run pre-commit run --all-files` với
nhãn "Kiem tra hang rao chan lo khoa". Bước đó **không chặn được gì**:

- `chan-env.sh` đọc `git diff --cached`, mà `pre-commit run --all-files` không stage file nào
  → index rỗng → luôn Passed.
- `detect-private-key` chỉ khớp header khoá PEM / OpenSSH, không bắt được một khoá dạng
  `sk-...` nằm trong file `.env`.

Hàng rào thật phải hỏi *cái gì đang bị track*, và `git ls-files` là lệnh trả lời câu đó.

**Bước cần thêm:**

```yaml
- name: Kiem tra khong co file .env bi track
  run: |
    if git ls-files -z | tr '\0' '\n' \
       | grep -vE '(^|/)\.env\.example$' \
       | grep -qE '(^|/)\.env(\.|$)'; then
      echo "LOI: co file .env bi track trong git"
      exit 1
    fi
```

**Bẫy:**
- Phải loại trừ `.env.example` — file đó *nên* được track.
- Phải bắt cả biến thể `.env.local`, `.env.prod`: pattern là `(^|/)\.env(\.|$)`, không phải
  `\.env$`. Đúng cặp pattern mà `scripts/chan-env.sh` đang dùng — đọc file đó trước khi viết.
- Giữ nguyên bước `pre-commit run --all-files` đang có, đừng thay thế nó. Hai bước làm hai
  việc khác nhau.

**Xong khi:**
- Chạy đúng khối lệnh trên ở local → thoát `0`.
- Thử ngược để chắc hàng rào có răng, rồi dọn sạch:

  ```bash
  touch .env.local && git add -f .env.local
  # chay lai khoi lenh tren -> phai thoat 1 va in dong LOI
  git rm --cached .env.local && rm .env.local
  git status   # phai sach
  ```
- CI xanh sau khi push.

---

### N8 — Nâng phiên bản GitHub Action

**File được sửa:** `.github/workflows/ci.yml`

**Mục tiêu:** `actions/checkout@v4` và `astral-sh/setup-uv@v5` trong `ci.yml` đều chậm nhiều
major so với bản hiện hành. Nâng lên bản mới nhất.

**Bẫy — đây là bài học số một của Chặng 0:** **không được điền số phiên bản từ trí nhớ.** Lỗi
nghiêm trọng nhất mà review Chặng 0 tìm ra là một khẳng định về phiên bản thư viện, viết từ trí
nhớ, không lệnh nào trong plan kiểm chứng được, nên nó đi thẳng từ spec qua plan vào bài học.
Chạy lệnh, đọc output, rồi mới gõ số:

```bash
gh api repos/actions/checkout/releases/latest --jq .tag_name
gh api repos/astral-sh/setup-uv/releases/latest --jq .tag_name
```

**Xong khi:**
- Số trong `ci.yml` khớp output hai lệnh trên. Dán nguyên output vào PR.
- Commit message ghi rõ ngày kiểm chứng.
- CI xanh sau khi push.
- Nếu bản mới đổi API (tên input khác, hành vi khác) làm CI đỏ: **dừng và báo**, đừng tự đoán
  cách sửa.

---

## 7. Quy trình làm một nhiệm vụ

```bash
git switch main && git pull
git switch -c n3-noi-seam-settings      # dat ten theo ma nhiem vu
# ... sua code ...
# ... chay du 6 lenh kiem tra o muc 3 ...
git add <chi nhung file nhiem vu cho phep>
git commit
git push -u origin n3-noi-seam-settings
gh pr create
```

Nội dung PR phải có:

1. Mã nhiệm vụ (N1…N8) và một câu tóm tắt.
2. Output của cả 6 lệnh kiểm tra.
3. Với N6, N7, N8: output của lệnh kiểm chứng thủ công mà nhiệm vụ yêu cầu.
4. Bất cứ điều gì bạn thấy đáng ngờ nhưng không sửa vì ngoài phạm vi.

---

## 8. Mẫu prompt

Dán vào công cụ nào không tự đọc `AGENTS.md`:

> Đọc file `AGENTS.md` ở gốc repo, toàn bộ.
> Thực hiện **đúng nhiệm vụ N3**, không làm gì khác.
> Tạo nhánh `n3-noi-seam-settings`.
> Chạy đủ 6 lệnh kiểm tra ở mục 3 và dán nguyên output.
> Nếu không đạt được tiêu chí "Xong khi", dừng lại và nói rõ vướng ở đâu — đừng mở rộng phạm
> vi để lách.

---

## 9. Checklist review (cho người duyệt PR)

- [ ] `git diff --stat` chỉ đụng những file mà nhiệm vụ cho phép?
- [ ] Test được **thêm**, hay bị **sửa cho dễ qua**? (chỉ N4 được phép sửa test cũ)
- [ ] Có dependency nào lén vào `pyproject.toml` hay `uv.lock` không?
- [ ] Output 6 lệnh kiểm tra có trong PR, và là output thật (không phải bịa)?
- [ ] Với N6/N7/N8: có output lệnh kiểm chứng thủ công không?
- [ ] CI xanh trên GitHub?
- [ ] Comment và định danh viết tiếng Việt không dấu?
