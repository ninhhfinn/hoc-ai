# Thiết kế: App học tập để trở thành AI Engineer

**Ngày:** 2026-08-08
**Trạng thái:** Đã duyệt
**Tác giả:** ninh + Claude

---

## 1. Tóm tắt

Xây một ứng dụng RAG cá nhân bằng tiếng Việt, vừa là **công cụ học** vừa là **dự án portfolio**.
Người dùng nạp tài liệu (PDF, Markdown, URL) vào app; app trả lời câu hỏi kèm trích nguồn, tự
sinh quiz, chấm bài, phỏng vấn thử, và tự đo chất lượng của chính nó bằng một bộ eval.

Điểm cốt lõi: **quá trình xây app chính là giáo trình.** Mỗi chặng phát triển tương ứng một
nhóm yêu cầu trong JD AI Engineer Intern 2026. Tài liệu học của mỗi chặng được nạp ngược vào
app, để app kiểm tra lại kiến thức người xây nó.

---

## 2. Bối cảnh và mục tiêu

### 2.1 Nguồn gốc

JD AI Engineer Intern năm 2026 (ảnh chụp bài đăng Facebook) yêu cầu:

- Python, FastAPI
- LangChain, VectorDB
- Hiểu RAG, Embeddings, Vector Similarity
- Hiểu Tokenization, Context Window, Inference của LLM
- Có 1–2 dự án AI thực tế
- Docker, Linux, đọc log
- Git/GitLab Workflow, Merge Request
- ML Evaluation

### 2.2 Mục tiêu

1. Người học đạt đủ 10/10 gạch đầu dòng trên, **có bằng chứng kiểm chứng được** (code, test, CI, báo cáo eval).
2. Sản phẩm cuối là một app thật, dùng được hằng ngày, đủ chất lượng đưa vào CV.
3. Người học **giải thích được** mọi mảnh trong hệ thống, không chỉ ghép thư viện.

### 2.3 Không phải mục tiêu

- Không train hay fine-tune model (xem §9.6).
- Không làm sản phẩm thương mại, không đa người dùng.
- Không phủ Machine Learning cổ điển (hồi quy, cây quyết định, CNN). JD không đòi.

---

## 3. Người học và ràng buộc

| Yếu tố | Giá trị |
|---|---|
| Trình độ | Python cơ bản (biến, hàm, list/dict). Chưa từng viết API, chưa dùng Docker, chưa dùng Git nghiêm túc |
| Thời gian | ~10 giờ/tuần, không deadline gấp |
| Ngôn ngữ | Toàn bộ tài liệu học và giao diện bằng **tiếng Việt** |
| Ngân sách | Càng thấp càng tốt; chấp nhận vài chục nghìn VNĐ/tháng |

### 3.1 Cấu hình máy (đã kiểm tra 2026-08-08)

```
CPU     : Intel i5-13500HX, 6 nhân / 12 luồng
RAM     : 14 GB (trống ~6.8 GB lúc đo)
GPU     : NVIDIA RTX 4060 Laptop, 8 GB VRAM
Disk    : 117 GB, còn trống 38 GB
Python  : 3.14.4  ← quá mới, xem §9.1
Git     : 2.53.0  ✓
Node    : v22.22.1 ✓
Docker  : CHƯA CÀI  ← cài ở Chặng 4
```

Hệ quả thiết kế:

- 8 GB VRAM **thừa sức** chạy embedding local và một LLM 7B lượng tử hoá 4-bit (xem §9.6).
- RAM 14 GB là điểm chật nhất. Không chạy đồng thời Ollama + Qdrant + app + IDE. Dùng
  Docker Compose profiles để bật/tắt theo nhu cầu.
- Disk 38 GB đủ nhưng cần theo dõi: model Ollama ~5 GB/cái, image Docker ~2 GB.

---

## 4. Sản phẩm

Một app, **bốn chế độ cho người dùng** cộng **một công cụ đo chất lượng**, tất cả dùng chung
một lõi RAG.

```
        ┌─────────────── LÕI RAG (dùng chung) ───────────────┐
        │  Tài liệu → Chunk → Embed(GPU local) → VectorDB    │
        │  Câu hỏi  → Embed → Tìm top-k → Prompt → LLM       │
        └────────────────────────┬──────────────────────────┘
                                 │
        ┌────────────┬───────────┼───────────┬──────────────┐
        ▼            ▼           ▼           ▼              ▼
   1. Hỏi đáp   2. Quiz     3. Phỏng vấn  4. Chấm code   5. Eval
   + trích      + ôn tập     nhiều lượt    pytest+AI     đo chất
     nguồn        ngắt quãng                review        lượng
```

### 4.1 Hỏi đáp có trích nguồn

Người dùng đặt câu hỏi. App tìm các đoạn tài liệu liên quan, đưa vào prompt, trả lời, và
**luôn hiển thị nguồn** (tên tài liệu, số đoạn, số trang nếu có PDF). Nếu không tìm được đoạn
nào đủ liên quan, app nói *"không tìm thấy trong tài liệu"* thay vì bịa.

### 4.2 Quiz và ôn tập ngắt quãng

App sinh câu hỏi từ tài liệu đã nạp — trắc nghiệm và tự luận. Câu tự luận được chấm bằng
LLM theo rubric. Kết quả lưu vào SQLite; thuật toán SM-2 rút gọn quyết định khi nào hỏi lại
câu đó. Chủ đề người học hay sai được ưu tiên.

### 4.3 Phỏng vấn thử

Phiên hội thoại nhiều lượt. AI đóng vai người phỏng vấn, hỏi theo chủ đề JD, đào sâu dựa
trên câu trả lời trước, cuối phiên chấm điểm và chỉ ra chỗ thiếu. Dùng LangGraph để quản lý
trạng thái phiên.

### 4.4 Chấm bài code

Bank bài tập có sẵn (viết hàm chunking, viết endpoint FastAPI...). Người dùng nộp code; app
chạy bộ `pytest` **đã viết sẵn** trong container Docker cô lập; sau đó LLM review code theo
rubric. **Không chạy code tuỳ ý** — xem §9.5.

### 4.5 Eval

Không phải tính năng cho người dùng cuối, mà là công cụ đo chất lượng của bốn chế độ trên.
Xem §12.

---

## 5. Kiến trúc

### 5.1 Luồng dữ liệu

```
PDF / Markdown / URL
   ↓ Loader          đọc file, crawl web, tách text
   ↓ Chunker         cắt đoạn ~500 token, chồng lấn 50
   ↓ Embedder        multilingual-e5-base trên RTX 4060 → vector 768 chiều
   ↓ VectorStore     Qdrant: vector + metadata (nguồn, số đoạn, số trang)

Câu hỏi
   ↓ Embedder        cùng model → vector 768 chiều
   ↓ VectorStore     tìm top-k đoạn gần nhất (cosine similarity)
   ↓ PromptBuilder   [k đoạn tài liệu] + [câu hỏi] + [chỉ dẫn trích nguồn]
   ↓ LLMProvider     DeepSeek v4-flash (hoặc Ollama local)
   ↓ Answer          text + danh sách citation
   ↓ SQLite          ghi lịch sử: hỏi gì, chủ đề nào, tốn bao nhiêu token
```

### 5.2 Nguyên tắc phân lớp

- `core/` **không biết** FastAPI tồn tại → test được mà không cần chạy server.
- `features/` **không biết** DeepSeek tồn tại → chỉ gọi qua `LLMProvider`.
- `api/` chỉ làm việc chuyển đổi HTTP ↔ lời gọi hàm, không chứa logic nghiệp vụ.
- Mọi phụ thuộc ra bên ngoài (LLM, VectorDB, embedding) đều nằm sau một interface có
  bản giả (fake) dùng trong test.

### 5.3 Cấu trúc thư mục

```
ApphocAIengineering/
├── docs/
│   ├── lessons/                 # bài lý thuyết tiếng Việt, đọc trước khi code
│   │   ├── lesson-00-nen-mong.md        # Chặng 0 (kèm phần train vs inference)
│   │   ├── lesson-01-fastapi.md         # Chặng 1
│   │   ├── ...                          # lesson-NN ↔ Chặng NN
│   │   └── lesson-08-cham-code.md       # Chặng 8
│   └── superpowers/specs/       # spec và plan
├── app/
│   ├── core/
│   │   ├── config.py            # đọc .env, cấu hình có kiểu
│   │   ├── models.py            # Chunk, SearchHit, Completion, Citation
│   │   ├── chunking.py
│   │   ├── embedding.py         # Embedder protocol + bản local GPU
│   │   ├── vectorstore.py       # VectorStore protocol + bản numpy, bản Qdrant
│   │   ├── retriever.py
│   │   ├── prompts.py           # template prompt, tách khỏi logic
│   │   └── llm/
│   │       ├── base.py          # LLMProvider protocol, Completion, giá tiền
│   │       ├── deepseek.py
│   │       ├── ollama.py
│   │       └── fake.py          # dùng trong test, không gọi mạng
│   ├── ingest/
│   │   ├── loaders.py           # PDF, Markdown, URL
│   │   └── pipeline.py          # loader → chunker → embedder → store
│   ├── features/
│   │   ├── qa.py
│   │   ├── quiz.py
│   │   ├── interview.py
│   │   └── grader.py
│   ├── api/
│   │   ├── main.py
│   │   ├── routers/
│   │   └── errors.py
│   └── db/
│       ├── models.py            # SQLAlchemy
│       ├── session.py
│       └── migrations/
├── eval/
│   ├── golden/                  # bộ câu hỏi vàng (.jsonl)
│   ├── metrics/                 # recall@k, mrr, ndcg, faithfulness
│   ├── configs/                 # mỗi file = một cấu hình đem so sánh
│   ├── run.py
│   └── reports/                 # kết quả xuất ra
├── web/
│   ├── templates/               # Jinja2
│   └── static/
├── exercises/                   # bank bài tập + test cho Chặng 8
├── tests/
│   ├── unit/
│   └── integration/
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── runner.Dockerfile        # container chạy pytest bài nộp
├── .github/workflows/ci.yml
├── .env.example
└── pyproject.toml
```

Mỗi thư mục một trách nhiệm. Khi một file vượt ~300 dòng, đó là tín hiệu nó đang làm quá
nhiều việc và cần tách.

---

## 6. Giao diện các module

Đây là các hợp đồng cố định. Bản cài đặt phía sau thay đổi tự do miễn giữ đúng hợp đồng.

```python
# app/core/models.py
@dataclass(frozen=True)
class Chunk:
    id: str                 # ổn định giữa các lần nạp lại (hash nội dung + nguồn)
    text: str
    source_id: str          # đường dẫn file hoặc URL
    source_title: str
    ordinal: int            # đoạn thứ mấy trong tài liệu
    page: int | None
    token_count: int

@dataclass(frozen=True)
class SearchHit:
    chunk: Chunk
    score: float            # cosine similarity, [-1, 1]

@dataclass(frozen=True)
class Citation:
    source_title: str
    source_id: str
    ordinal: int
    page: int | None
```

```python
# app/core/embedding.py
class Embedder(Protocol):
    dim: int
    def embed_documents(self, texts: list[str]) -> np.ndarray: ...   # (n, dim), đã chuẩn hoá L2
    def embed_query(self, text: str) -> np.ndarray: ...              # (dim,), đã chuẩn hoá L2
```

Vector được chuẩn hoá L2 ngay tại nguồn, nên cosine similarity rút gọn thành tích vô hướng.

```python
# app/core/vectorstore.py
class VectorStore(Protocol):
    def upsert(self, chunks: list[Chunk], vectors: np.ndarray) -> None: ...
    def search(self, vector: np.ndarray, k: int,
               source_filter: list[str] | None = None) -> list[SearchHit]: ...
    def delete_by_source(self, source_id: str) -> None: ...
    def count(self) -> int: ...
```

Hai bản cài đặt: `NumpyVectorStore` (Chặng 3) và `QdrantVectorStore` (Chặng 4). Cùng test suite
chạy qua cả hai — đó là cách chứng minh việc chuyển đổi không làm hỏng gì.

```python
# app/core/llm/base.py
@dataclass(frozen=True)
class Completion:
    text: str
    input_tokens: int
    output_tokens: int
    model: str
    cost_usd: float
    latency_ms: int

class LLMProvider(Protocol):
    name: str
    def complete(self, messages: list[Message], *,
                 temperature: float = 0.0,
                 max_tokens: int | None = None,
                 json_schema: dict | None = None) -> Completion: ...
    def stream(self, messages: list[Message], **kw) -> Iterator[str]: ...
    def count_tokens(self, text: str) -> int: ...
```

Mọi lời gọi LLM đều trả về số token và giá tiền. Không có đường nào gọi LLM mà không ghi
được chi phí — đây là ràng buộc cố ý, để §11.3 hoạt động.

---

## 7. Mô hình dữ liệu (SQLite)

Qdrant giữ vector và nội dung chunk. SQLite giữ **trạng thái học tập** và **nhật ký vận hành**.

| Bảng | Nội dung |
|---|---|
| `documents` | id, source_uri, title, kind, checksum, ingested_at, chunk_count |
| `quiz_items` | id, document_id, chunk_id, kind (mcq/open), question, choices_json, answer, rubric, topic |
| `attempts` | id, quiz_item_id, user_answer, score, feedback, answered_at |
| `review_schedule` | quiz_item_id, ease, interval_days, repetitions, due_at (SM-2) |
| `interview_sessions` | id, topic, transcript_json, final_score, feedback, started_at, ended_at |
| `exercises` | id, slug, title, prompt_md, test_path, rubric_md |
| `submissions` | id, exercise_id, code, pytest_output, passed, ai_review, score, submitted_at |
| `llm_calls` | id, feature, model, input_tokens, output_tokens, cost_usd, latency_ms, created_at |

`checksum` trên `documents` cho phép nạp lại chỉ khi tài liệu đổi — quan trọng vì
`docs/lessons/` sẽ được nạp đi nạp lại liên tục.

`llm_calls` là bảng để trả lời *"tháng này tốn bao nhiêu tiền, tính năng nào tốn nhất"*.

---

## 8. Công nghệ

| Mảng | Chọn | Lý do |
|---|---|---|
| Python | **3.12** qua `uv` | Máy này, máy khác và CI phải cùng một bản; hệ sinh thái ML chậm hơn bản Python mới nhất vài tháng. `uv` cài Python riêng cho project |
| Web API | **FastAPI + Pydantic** | JD ghi thẳng tên. Pydantic dạy ràng buộc dữ liệu |
| Embedding | **`intfloat/multilingual-e5-base`** local GPU | Hiểu Việt lẫn Anh, 768 chiều, ~0.6 GB VRAM |
| VectorDB | **Qdrant** (Docker) | JD ghi "VectorDB". Có UI xem được vector |
| LLM chính | **DeepSeek `deepseek-v4-flash`** | Rẻ, API tương thích OpenAI, context 1M |
| LLM đối chứng | **Ollama + Qwen2.5-7B (4-bit)** | Chạy local, để so sánh và học Inference |
| CSDL | **SQLite + SQLAlchemy** | App một người dùng. Không cần Postgres |
| Giao diện | **Jinja2 + HTMX** | Xem §9.4 |
| Test | **pytest**, viết test trước | Xem §9.3 |
| Lint | **ruff** + **mypy** | |
| Đóng gói | **Docker + docker-compose** | JD ghi. Cài ở Chặng 4 |
| CI | **GitHub Actions** | Chạy lint + test mỗi lần push |
| Log | **structlog** (JSON) | JD ghi "đọc log". Log có cấu trúc mới truy được |

### 8.1 Giá DeepSeek (tra ngày 2026-08-08)

| Model | Input (cache miss) | Output | Context |
|---|---|---|---|
| `deepseek-v4-flash` | $0.14 / 1M token | $0.28 / 1M token | 1M |
| `deepseek-v4-pro` | $0.435 / 1M token | $0.87 / 1M token | 1M |

Ước tính dùng cá nhân (hỏi đáp + sinh quiz + eval định kỳ): **dưới 25.000 VNĐ/tháng**.

Trang giá của DeepSeek ghi rõ họ dự kiến tăng giá đáng kể. Lớp `LLMProvider` khiến việc đổi
nhà cung cấp chỉ là đổi một dòng cấu hình.

---

## 9. Các quyết định thiết kế

### 9.1 Dùng Python 3.12, không dùng 3.14 có sẵn

Máy đang có Python 3.14.4, và **3.14 không hỏng** — kiểm chứng trên PyPI ngày 2026-08-09:
`torch` 2.13.0 có wheel `cp314` (đã có từ 2.9.0), `sentence-transformers` là gói thuần Python
`py3-none-any`. Ghim 3.12 vì lý do khác: một project cần đúng một phiên bản Python cố định,
cùng lý do cần `uv.lock` — máy này, máy khác và CI phải chạy trên một bản duy nhất; và hệ sinh
thái ML thường chậm vài tháng sau mỗi bản Python mới nên chọn bản đã ổn định lâu là phòng rủi
ro, không phải chữa lỗi. `uv` tải Python 3.12 riêng cho project, không đụng tới Python hệ thống.

Đây cũng là bài học đầu tiên: **quản lý môi trường Python** — thứ mọi JD ngầm đòi và người
mới hay bỏ qua.

### 9.2 Tự viết RAG bằng tay trước, LangChain sau

JD ghi "LangChain". Đường nhanh là dùng LangChain ngay từ đầu: khoảng 15 dòng là có RAG chạy.
Nhưng người học sẽ không hiểu chuyện gì đang xảy ra, và người phỏng vấn phát hiện điều đó rất nhanh.

- **Chặng 3:** tự viết chunker, tự gọi embedding, **tự viết hàm cosine similarity bằng numpy**,
  tự ghép prompt. Không dùng thư viện RAG nào.
- **Chặng 7:** viết lại đúng pipeline đó bằng LangChain và so sánh.

Đánh đổi: chậm hơn khoảng một tuần. Đổi lại người học trả lời được *"LangChain làm hộ cái gì
và giấu đi cái gì"* — câu chỉ người từng tự viết mới trả lời nổi.

### 9.3 Viết test trước khi viết code

Người học chưa từng viết test. Bắt đầu ngay từ Chặng 0 vì ba lý do:

1. Học một mình, không ai review — test đóng vai người review.
2. Code AI **sai âm thầm**: retrieval trả về đoạn không liên quan mà câu trả lời vẫn nghe
   xuôi tai. Không có test thì không bao giờ phát hiện.
3. CI xanh trên GitHub là bằng chứng nhà tuyển dụng nhìn thấy ngay.

### 9.4 Jinja2 + HTMX, không dùng React

JD không đòi frontend. Thêm React là thêm một mảng học riêng (build tool, state, hooks) mà
không đổi lấy điểm cộng nào cho vị trí AI Engineer.

Jinja + HTMX cho giao diện đủ dùng, đủ đẹp để quay demo, vẫn nằm trong Python, và dạy HTTP
đúng bản chất. API đã sẵn sàng nếu sau này muốn gắn React.

### 9.5 Chấm code: chạy pytest có sẵn, không chạy code tuỳ ý

Cho người dùng chạy code bất kỳ trong sandbox là một bài toán bảo mật lớn (thoát container,
cạn tài nguyên, gọi mạng ra ngoài) và **không nằm trong JD**.

Thay vào đó: mỗi bài tập có sẵn một file test. App chạy `pytest` trong container Docker
không có mạng, giới hạn CPU/RAM/thời gian, rồi để LLM review code theo rubric.

Vẫn học đủ Docker và cách ly tài nguyên, mà không mất ba tuần vào bảo mật sandbox.

### 9.6 Không train, không fine-tune bất cứ thứ gì

Toàn bộ dự án chỉ **dùng** model đã huấn luyện sẵn (inference), không tạo model.

Với model N tham số, bộ nhớ GPU cần:

```
Train (mixed-precision Adam):
  trọng số fp16   2N  +  gradient 2N  +  bản fp32 4N  +  Adam m 4N  +  Adam v 4N
  = 16N byte      →  model 7B cần ~112 GB VRAM

Inference (lượng tử hoá 4-bit):
  trọng số ~0.5N + ngữ cảnh
  = model 7B cần ~5 GB VRAM
```

Nên RTX 4060 8 GB thừa sức cho mục tiêu của dự án:

| Thành phần | VRAM |
|---|---|
| `multilingual-e5-base` (278 triệu tham số) | ~0.6 GB |
| Qwen2.5-7B 4-bit qua Ollama | ~5 GB |
| DeepSeek v4-flash | 0 GB — chạy trên server nhà cung cấp |

Đây cũng là lý do RAG tồn tại: để model biết tài liệu của bạn mà **không cần train lại**.
Nội dung mục này đưa vào `lesson-00`.

### 9.7 Chọn model embedding bằng eval, không chọn bằng cảm tính

Khởi đầu với `multilingual-e5-base`. Đến Chặng 6, chạy eval so sánh nó với `BAAI/bge-m3` trên
chính tài liệu của người học, rồi chọn theo số liệu.

Biến một lựa chọn kỹ thuật thành một thí nghiệm có số đo — đó là công việc thật của AI Engineer.

---

## 10. Xử lý lỗi

| Tình huống | Cách xử lý |
|---|---|
| LLM trả 429 / 5xx | Thử lại có lùi thời gian tăng dần (tenacity), tối đa 3 lần, có jitter |
| LLM quá thời gian | Timeout 60s, trả lỗi rõ ràng cho người dùng, ghi log |
| LLM trả JSON sai định dạng | Validate bằng Pydantic → gửi lại kèm thông báo lỗi, tối đa 2 lần → bỏ cuộc và ghi log |
| Nạp một tài liệu lỗi | Cô lập theo từng tài liệu; một file hỏng không làm chết cả mẻ |
| GPU hết bộ nhớ khi embed | Giảm kích thước batch và thử lại; nếu vẫn lỗi thì chuyển sang CPU |
| Qdrant không kết nối được | Kiểm tra lúc khởi động, báo lỗi nêu rõ cần chạy `docker compose up qdrant` |
| Không tìm được đoạn nào đủ liên quan | Trả lời *"không tìm thấy trong tài liệu"*, **không để LLM tự bịa** |
| Container chấm bài quá giờ | Giới hạn cứng 30 giây, kill container, báo timeout |

Toàn bộ lỗi API trả về cùng một hình dạng JSON: `{"error": {"code": ..., "message": ..., "request_id": ...}}`.

Log dùng structlog định dạng JSON, có `request_id` xuyên suốt để lần theo một yêu cầu qua
nhiều lớp. Đây là cách rèn kỹ năng "đọc log" mà JD nhắc.

---

## 11. Chiến lược test

### 11.1 Các tầng

| Tầng | Phạm vi | Có gọi mạng? |
|---|---|---|
| Unit | chunker, cosine similarity, SM-2, tính giá token, dựng prompt | Không |
| Contract | Mọi bản `VectorStore` chạy qua **cùng một** bộ test | Không |
| Integration | FastAPI TestClient + Qdrant tạm + `FakeLLMProvider` | Không |
| Smoke | Một lần gọi DeepSeek thật, kiểm tra khoá API còn sống | Có — chạy tay |
| Eval | Đo chất lượng, tốn tiền và thời gian | Có — xem §12 |

### 11.2 Bản giả

`app/core/llm/fake.py` cung cấp `FakeLLMProvider` trả lời theo kịch bản định sẵn. Mọi test
tự động dùng bản này. Hệ quả: bộ test chạy trong vài giây và **không tốn một đồng nào**.

### 11.3 CI

GitHub Actions chạy mỗi lần push: `ruff check` → `mypy` → `pytest tests/`.
Eval **không** chạy trong CI thường (chậm, tốn tiền); chỉ một tập con nhỏ chạy khi merge vào `main`.

---

## 12. Chiến lược eval

Đây là phần tạo khác biệt lớn nhất so với các dự án portfolio thông thường.

### 12.1 Bộ dữ liệu vàng

`eval/golden/qa.jsonl` — khoảng 50 mục, xây thủ công từ tài liệu của chính người học:

```json
{"question": "RAG khác fine-tuning ở điểm nào?",
 "relevant_chunk_ids": ["lesson-00#4", "lesson-03#1"],
 "expected_points": ["RAG không sửa trọng số model", "RAG đưa tài liệu vào prompt"],
 "topic": "rag-co-ban"}
```

### 12.2 Các chỉ số

**Phần tìm kiếm** (đo được chính xác, không cần LLM):

- `Recall@k` — trong k đoạn lấy về, có bao nhiêu đoạn đúng
- `MRR` — đoạn đúng đầu tiên nằm ở vị trí nào
- `nDCG@k` — có tính đến thứ hạng

**Phần sinh câu trả lời** (dùng LLM làm giám khảo):

- `faithfulness` — câu trả lời có bám vào đoạn tài liệu lấy được không, hay bịa thêm
- `answer_relevance` — có trả lời đúng trọng tâm câu hỏi không

**Vận hành:**

- độ trễ p50 / p95
- chi phí trung bình mỗi câu hỏi

### 12.3 Cạm bẫy của LLM-as-judge

Phải viết vào `lesson-06` và tính đến khi đọc kết quả:

- Giám khảo thiên vị câu trả lời dài
- Giám khảo thiên vị câu trả lời do chính model đó sinh ra
- Điểm không ổn định giữa các lần chạy → phải đặt `temperature=0` và chạy 3 lần lấy trung vị

Đối chứng: chấm tay 10 mục và so với điểm máy chấm, để biết giám khảo đáng tin đến đâu.

### 12.4 Cách chạy

```bash
uv run python -m eval.run --config eval/configs/baseline.yaml
```

Mỗi file config là một cấu hình đem so sánh (kích thước chunk, model embedding, giá trị k,
nhà cung cấp LLM). Kết quả xuất ra `eval/reports/YYYY-MM-DD-<tên>.md` gồm bảng số và biểu đồ.

### 12.5 Các thí nghiệm phải chạy

1. Kích thước chunk: 300 / 500 / 1000 token
2. Model embedding: `multilingual-e5-base` so với `bge-m3`
3. Số đoạn lấy về: k = 3 / 5 / 10
4. Nhà cung cấp LLM: DeepSeek v4-flash so với Qwen2.5-7B local

Kết quả các thí nghiệm này là nội dung người học mang đi phỏng vấn.

---

## 13. Lộ trình

Nguyên tắc: **chặng nào cũng kết thúc bằng một app chạy được.**

| # | Chặng | Tuần | Lý thuyết | Sản phẩm |
|---|---|---|---|---|
| 0 | Nền móng | 1–2 | Môi trường Python, Git/branch/PR, Linux, đọc log | Repo sạch, CI xanh, PR đầu tiên |
| 1 | API đầu tiên | 3–4 | HTTP, REST, JSON, FastAPI, Pydantic, async | API chạy được, có test |
| 2 | Nói chuyện với LLM | 5–6 | Tokenization, Context Window, Inference, temperature, streaming, chi phí | `/ask` trả lời thật, có streaming, log tiền |
| 3 | RAG làm tay | 7–9 | Embeddings, Vector Similarity, chunking, retrieval | Hỏi đáp tài liệu, có trích nguồn |
| 4 | VectorDB + Docker | 10–12 | Vì sao cần vector DB (ANN/HNSW), Docker, compose, volume | `docker compose up` chạy cả hệ |
| 5 | Quiz + ôn tập | 13–15 | Structured output, JSON schema, prompt có ràng buộc, thiết kế DB | App quiz hằng ngày, có giao diện |
| 6 | ML Evaluation | 16–18 | Recall@k, MRR, faithfulness, LLM-as-judge và cạm bẫy | Báo cáo eval có số liệu |
| 7 | LangChain + Phỏng vấn | 19–20 | LangChain/LangGraph, agent, tool calling, khi nào KHÔNG nên dùng | Chế độ phỏng vấn thử |
| 8 | Chấm code + hoàn thiện | 21–22 | Sandbox, pytest trong container, logging có cấu trúc | App hoàn chỉnh + README demo |

Tổng: **22 tuần ≈ 5,5 tháng** ở nhịp 10 giờ/tuần (~220 giờ).

### 13.1 Vòng lặp mỗi chặng

1. Viết `docs/lessons/lesson-NN-*.md` — lý thuyết tiếng Việt, có ví dụ và hình vẽ ASCII
2. Người học đọc, hỏi lại chỗ chưa hiểu
3. Viết test trước → viết code → test xanh
4. Tạo branch → commit → mở PR → tự review → merge
5. Nạp bài học vừa xong vào app → **để app quiz lại người học** (từ Chặng 5 trở đi)

### 13.2 Mốc có thể đi xin thực tập

**Sau Chặng 6 (khoảng tuần 18, tháng thứ 4,5)** hồ sơ đã đủ mạnh: app RAG chạy trong Docker,
có test, có CI, có báo cáo eval kèm số liệu. Chặng 7–8 làm song song trong lúc phỏng vấn.

### 13.3 Đối chiếu JD

| Yêu cầu JD | Chặng |
|---|---|
| Python | 0 |
| FastAPI | 1 |
| Tokenization, Context Window, Inference | 2 |
| RAG, Embeddings, Vector Similarity | 3 |
| VectorDB | 4 |
| Docker, Linux, đọc log | 0, 4, 8 |
| Git/GitLab workflow, Merge Request | 0 và mọi chặng |
| ML Evaluation | 6 |
| LangChain | 7 |
| AI pipeline | 3, 4, 7 |
| 1–2 dự án AI thực tế | Chính app này (dùng được từ Chặng 3) |

Phủ 10/10.

---

## 14. Rủi ro

| Rủi ro | Mức | Giảm thiểu |
|---|---|---|
| Bỏ cuộc giữa chừng | **Cao** | Mỗi chặng ra sản phẩm dùng được; người học tự dùng app hằng ngày nên có động lực sửa lỗi |
| Hệ sinh thái ML chậm chân so với bản Python mới nhất | Cao | `uv` ghim Python 3.12 ngay từ Chặng 0 |
| DeepSeek tăng giá hoặc chặn thanh toán từ VN | Trung bình | Lớp `LLMProvider` + Ollama local sẵn sàng thay thế |
| RAM 14 GB không đủ khi chạy đồng thời | Trung bình | Docker Compose profiles; không bật Ollama và Qdrant cùng lúc khi không cần |
| Disk 38 GB cạn | Trung bình | Theo dõi dung lượng; dọn image và model không dùng |
| Bộ eval quá nhỏ nên số liệu vô nghĩa | Trung bình | Tối thiểu 50 mục; đối chứng bằng 10 mục chấm tay |
| Sa lầy vào tinh chỉnh prompt | Trung bình | Mọi thay đổi prompt phải chứng minh bằng số eval, không sửa theo cảm tính |
| Lộ khoá API lên GitHub | Cao nếu xảy ra | `.env` vào `.gitignore` từ commit đầu; bật secret scanning; pre-commit chặn |

---

## 15. Ngoài phạm vi

Loại bỏ có chủ đích, để dự án hoàn thành được:

- Đăng nhập, đa người dùng, phân quyền
- Train hoặc fine-tune model
- Chạy code tuỳ ý do người dùng nộp
- Frontend React/Next.js
- PostgreSQL, Redis, hàng đợi tác vụ
- Triển khai lên cloud (có thể làm sau, không nằm trong 22 tuần)
- Ứng dụng di động, giọng nói
- Tìm kiếm lai (hybrid BM25 + vector), reranker — cân nhắc bổ sung sau Chặng 6 **nếu** eval
  cho thấy retrieval là điểm nghẽn

---

## 16. Tiêu chí hoàn thành

Dự án coi như xong khi tất cả đúng:

1. `docker compose up` dựng được toàn bộ hệ trên một máy sạch
2. `pytest` xanh, độ phủ trên `app/core/` từ 80% trở lên
3. CI xanh trên `main`
4. Hoàn tất 9 bài học trong `docs/lessons/`, và toàn bộ đã được nạp vào app
5. Báo cáo eval có số liệu cho cả 4 thí nghiệm ở §12.5
6. README có ảnh chụp màn hình hoặc GIF demo cả 4 chế độ
7. Người học **giải thích miệng được** mọi quyết định thiết kế trong tài liệu này
