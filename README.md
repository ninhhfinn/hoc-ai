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
