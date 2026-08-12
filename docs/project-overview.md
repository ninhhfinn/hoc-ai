# Tổng quan dự án hoc-ai

## 1. Dự án là gì

`hoc-ai` là một ứng dụng RAG (Retrieval-Augmented Generation) cá nhân, **vừa là công cụ học tập vừa là dự án portfolio** để trở thành AI Engineer.

Người dùng nạp tài liệu (PDF, Markdown, URL) vào app; app trả lời câu hỏi kèm trích nguồn, tự sinh quiz, chấm bài, phỏng vấn thử, và tự đo chất lượng của chính nó bằng một bộ eval.

## 2. Mục tiêu

1. Đạt đủ các yêu cầu trong JD AI Engineer Intern 2026, có bằng chứng kiểm chứng được (code, test, CI, báo cáo eval).
2. Sản phẩm cuối là một app thật, dùng được hằng ngày, đủ chất lượng đưa vào CV.
3. Người học giải thích được mọi mảnh trong hệ thống, không chỉ ghép thư viện.

## 3. Công nghệ chính

| Mảng | Chọn | Lý do |
|---|---|---|
| Python | **3.12** qua `uv` | Hệ sinh thái ML ổn định; `uv` ghim phiên bản |
| Web API | **FastAPI + Pydantic** | JD yêu cầu; Pydantic dạy ràng buộc dữ liệu |
| Embedding | **multilingual-e5-base** local GPU | Hiểu Việt lẫn Anh, 768 chiều, ~0.6 GB VRAM |
| VectorDB | **Qdrant** (Docker) | JD ghi "VectorDB"; có UI xem vector |
| LLM chính | **DeepSeek deepseek-v4-flash** | Rẻ, API tương thích OpenAI, context 1M |
| LLM đối chứng | **Ollama + Qwen2.5-7B 4-bit** | Chạy local, học Inference |
| CSDL | **SQLite + SQLAlchemy** | App một người dùng, không cần Postgres |
| Giao diện | **Jinja2 + HTMX** | Đủ dùng, vẫn trong Python, dạy HTTP |
| Test | **pytest** | Viết test trước |
| Lint | **ruff + mypy** | |
| Đóng gói | **Docker + docker-compose** | JD yêu cầu |
| CI | **GitHub Actions** | Chạy lint + test mỗi push |
| Log | **structlog** (JSON) | JD ghi "đọc log"; log có cấu trúc |

## 4. Kiến trúc tổng quan

```
PDF / Markdown / URL
   ↓ Loader          đọc file, crawl web, tách text
   ↓ Chunker         cắt đoạn ~500 token, chồng lấn 50
   ↓ Embedder        multilingual-e5-base → vector 768 chiều
   ↓ VectorStore     Qdrant: vector + metadata (nguồn, số đoạn, số trang)

Câu hỏi
   ↓ Embedder        cùng model → vector 768 chiều
   ↓ VectorStore     tìm top-k đoạn gần nhất (cosine similarity)
   ↓ PromptBuilder   [k đoạn tài liệu] + [câu hỏi] + [chỉ dẫn trích nguồn]
   ↓ LLMProvider     DeepSeek v4-flash (hoặc Ollama local)
   ↓ Answer          text + danh sách citation
   ↓ SQLite          ghi lịch sử: hỏi gì, chủ đề nào, tốn bao nhiêu token
```

### 4.1 Các chế độ người dùng

| Chế độ | Chức năng | Module |
|---|---|---|
| 1. Hỏi đáp | Trả lời câu hỏi kèm trích nguồn | `features/qa.py` |
| 2. Quiz | Sinh câu hỏi, chấm tự luận, ôn tập SM-2 | `features/quiz.py` |
| 3. Phỏng vấn | Phiên hỏi đáp nhiều lượt, chấm điểm cuối | `features/interview.py` |
| 4. Chấm code | Chạy pytest trong Docker, LLM review | `features/grader.py` |
| 5. Eval | Đo chất lượng 4 chế độ trên | `eval/` |

## 5. Cấu trúc thư mục

```
ApphocAIengineering/
├── docs/
│   ├── lessons/                 # bài lý thuyết tiếng Việt
│   └── superpowers/specs/       # spec thiết kế
├── app/
│   ├── __main__.py              # điểm vào CLI
│   ├── core/                    # lõi, không phụ thuộc web
│   │   ├── config.py            # cấu hình có kiểu (Pydantic)
│   │   ├── models.py            # Chunk, SearchHit, Completion, Citation
│   │   ├── chunking.py
│   │   ├── embedding.py         # Embedder protocol + bản local GPU
│   │   ├── vectorstore.py       # VectorStore protocol + bản numpy, bản Qdrant
│   │   ├── retriever.py
│   │   ├── prompts.py
│   │   └── llm/                 # LLMProvider protocol + bản deepseek, ollama, fake
│   ├── ingest/                  # loader PDF/Markdown/URL, pipeline nạp
│   ├── features/                # qa, quiz, interview, grader
│   ├── api/                     # FastAPI: main.py, routers, errors
│   └── db/                      # SQLAlchemy models, session, migrations
├── eval/                        # golden set, metrics, configs, reports
├── web/                         # Jinja2 templates + static
├── exercises/                   # bank bài tập + test cho chấm code
├── tests/                       # unit + integration
├── docker/                      # Dockerfile, docker-compose, runner
├── .github/workflows/ci.yml     # CI: ruff → mypy → pytest
├── pyproject.toml               # khai báo project + tool config
├── uv.lock                      # khóa phiên bản phụ thuộc
├── .env.example                 # mẫu cấu hình môi trường
└── README.md
```

## 6. Nguyên tắc phân lớp

- `core/` **không biết** FastAPI tồn tại → test được mà không cần chạy server.
- `features/` **không biết** DeepSeek tồn tại → chỉ gọi qua `LLMProvider`.
- `api/` chỉ làm việc chuyển đổi HTTP ↔ lời gọi hàm, không chứa logic nghiệp vụ.
- Mọi phụ thuộc ra bên ngoài đều nằm sau một interface có bản giả (fake) dùng trong test.

## 7. Trạng thái hiện tại

Dự án đang ở **Chặng 0 — Nền móng**.

Đã hoàn thành:
- Cấu trúc repo, CI xanh (ruff, mypy, pytest)
- Module `core/config.py`: đọc cấu hình từ `.env`, kiểm tra kiểu với Pydantic
- Module `core/doctor.py`: kiểm tra môi trường (Python, git, docker, config)
- CLI `app doctor` và `app version`
- Test hermetic (conftest xoá biến môi trường + chdir sang tmp_path)

## 8. Lộ trình (9 chặng, ~22 tuần)

| # | Chặng | Tuần | Sản phẩm |
|---|---|---|---|
| 0 | Nền móng | 1–2 | Repo sạch, CI xanh, PR đầu tiên |
| 1 | API đầu tiên | 3–4 | API chạy được, có test |
| 2 | Nói chuyện với LLM | 5–6 | `/ask` trả lời thật, streaming, log tiền |
| 3 | RAG làm tay | 7–9 | Hỏi đáp tài liệu, có trích nguồn |
| 4 | VectorDB + Docker | 10–12 | `docker compose up` chạy cả hệ |
| 5 | Quiz + ôn tập | 13–15 | App quiz hằng ngày, có giao diện |
| 6 | ML Evaluation | 16–18 | Báo cáo eval có số liệu |
| 7 | LangChain + Phỏng vấn | 19–20 | Chế độ phỏng vấn thử |
| 8 | Chấm code + hoàn thiện | 21–22 | App hoàn chỉnh + README demo |

## 9. Chại thử

```bash
uv sync
cp .env.example .env
uv run python -m app doctor
```

## 10. Phát triển

```bash
uv run pytest                  # chay test
uv run ruff check .            # lint
uv run mypy                    # kiem tra kieu
uv run pre-commit install      # cai hook (chi lam mot lan)
```

## 11. Tài liệu chi tiết

- [Spec thiết kế](docs/superpowers/specs/2026-08-08-app-hoc-ai-engineering-design.md)
- [Bài học](docs/lessons/)
