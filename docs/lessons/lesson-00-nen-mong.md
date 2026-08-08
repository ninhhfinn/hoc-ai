# Bài học 00: Nền móng của một AI Engineer

Đây là bài học lý thuyết đầu tiên của dự án `hoc-ai`. Trước khi gõ một dòng code nào, bạn cần
gỡ vài hiểu nhầm và nắm vài khái niệm nền — nếu không, những task viết code ở sau sẽ chỉ là
làm theo hướng dẫn mà không hiểu vì sao.

## AI Engineer khác ML Researcher chỗ nào

Có một hiểu nhầm rất phổ biến ở người mới: nghe nói "chạy LLM (Large Language Model — mô hình
ngôn ngữ lớn) trên máy cá nhân", nhiều người tưởng tượng ngay đến việc phải *train* (huấn luyện)
model đó, và train thì cần GPU khủng, kiểu 100GB VRAM (Video RAM — bộ nhớ riêng của card đồ
hoạ, nơi model và dữ liệu tính toán được nạp vào khi chạy trên GPU) trở lên. Đây chính xác là
hiểu nhầm cần gỡ trước khi làm bất cứ điều gì trong dự án này, vì **toàn bộ dự án không train
gì cả**.

Sự khác biệt nằm ở hai công việc rất khác nhau:

- **ML Researcher** (nhà nghiên cứu Machine Learning) tạo ra model mới: thu thập dữ liệu khổng
  lồ, thiết kế kiến trúc mạng nơ-ron, rồi *train* — tức là chạy hàng triệu vòng lặp để chỉnh
  từng trọng số (weight) của model sao cho nó dự đoán đúng hơn. Đây là công việc cực kỳ tốn
  tài nguyên.
- **AI Engineer** (kỹ sư AI — đúng vị trí JD đang nhắm tới) hầu như không train model từ đầu.
  Công việc là *dùng* model đã được ai đó train sẵn (OpenAI, DeepSeek, Meta, Qwen...), rồi ghép
  nó vào một hệ thống thật: gọi API, xử lý dữ liệu đưa vào, xử lý kết quả trả ra, tối ưu chi
  phí, đo chất lượng. Việc "dùng model có sẵn để tạo ra kết quả" gọi là **inference**
  (suy luận) — model chỉ chạy xuôi một lượt (forward pass) từ đầu vào ra đầu ra, không có bước
  chỉnh trọng số nào cả.

Khác biệt giữa train và inference lộ rõ nhất ở lượng bộ nhớ GPU cần dùng. Khi train bằng kỹ
thuật phổ biến nhất (mixed-precision Adam — một cách train giữ hai bản trọng số song song,
một bản 16-bit nhẹ để tính nhanh và một bản 32-bit chính xác để cộng dồn thay đổi nhỏ, cộng với
bộ nhớ đệm của thuật toán tối ưu Adam), với model có N tham số, con số cộng dồn lại như sau:

```
Train (mixed-precision Adam):
  trọng số fp16   2N  +  gradient 2N  +  bản fp32 4N  +  Adam m 4N  +  Adam v 4N
  = 16N byte      →  model 7B (7 tỷ tham số) cần khoảng 112 GB VRAM

Inference (lượng tử hoá 4-bit — nén mỗi trọng số xuống còn khoảng nửa byte):
  trọng số ~0.5N + bộ nhớ cho ngữ cảnh (context) đang xử lý
  = model 7B cần khoảng 5 GB VRAM
```

Nói cách khác: train một model 7 tỷ tham số cần ~112GB VRAM — nhiều hơn tổng VRAM của hàng
chục chiếc RTX 4060 cộng lại. Còn *chạy* (inference) đúng model đó sau khi đã lượng tử hoá
(quantization — nén trọng số từ số thực chính xác cao xuống số nguyên nhỏ hơn để tiết kiệm bộ
nhớ, đánh đổi một chút độ chính xác) xuống 4-bit thì chỉ cần ~5GB.

| Tiêu chí | Train | Inference |
|---|---|---|
| Mục đích | Tạo/chỉnh trọng số model | Dùng trọng số có sẵn để sinh kết quả |
| Có tính gradient không | Có (backward pass) | Không (chỉ forward pass) |
| VRAM cho model 7B | ~112 GB | ~5 GB (4-bit) |
| Thời gian | Vài ngày đến vài tuần | Vài giây mỗi câu hỏi |
| Dữ liệu cần | Tập dữ liệu lớn, đã gán nhãn/xử lý | Không cần — chỉ cần input tại thời điểm hỏi |
| Ai làm việc này | ML Researcher / ML Engineer huấn luyện | AI Engineer (đúng công việc JD mô tả) |

Máy của bạn — RTX 4060 Laptop 8GB VRAM, i5-13500HX, RAM 14GB — hoàn toàn không đủ để train một
model 7B (thiếu hơn 100GB VRAM), nhưng **thừa sức** để chạy inference cho cả hai model dự án
này cần: `multilingual-e5-base` dùng để tạo vector cho văn bản (~0.6GB VRAM) và Qwen2.5-7B đã
lượng tử hoá 4-bit dùng làm LLM đối chứng chạy local (~5GB VRAM) — cộng lại vẫn còn dư VRAM
trong ngân sách 8GB. Đây là lý do then chốt: dự án này khả thi trên đúng chiếc laptop bạn đang
có, vì nó chưa bao giờ định train bất cứ thứ gì.

## RAG tồn tại để làm gì

Một LLM khi được train xong chỉ biết những gì có trong dữ liệu train của nó, tính đến một mốc
thời gian nhất định. Nó không biết nội dung tài liệu riêng của bạn — ví dụ file spec dự án
này, hay ghi chú học tập bạn tự viết — vì những thứ đó chưa từng tồn tại lúc model được train.
Câu hỏi đặt ra là: làm sao để model trả lời được câu hỏi dựa trên tài liệu riêng đó?

Có hai con đường:

**Con đường 1 — Train lại (hoặc fine-tune, tức train tiếp trên dữ liệu mới):** đưa toàn bộ tài
liệu của bạn vào làm dữ liệu train, chạy lại quá trình cập nhật trọng số. Như Mục 1 vừa tính,
train một model 7B cần ~112GB VRAM — phần cứng hàng chục nghìn đô, hàng nghìn đô chi phí thuê
GPU cloud nếu không có máy đó, và mất vài tuần chuẩn bị dữ liệu, chạy, kiểm tra.

**Con đường 2 — RAG (Retrieval-Augmented Generation — sinh câu trả lời có tăng cường truy
xuất):** không đụng đến một trọng số nào của model. Thay vào đó: tìm đoạn tài liệu liên quan
đến câu hỏi, dán đoạn đó thẳng vào prompt (văn bản gửi cho model), rồi hỏi model trả lời dựa
trên đoạn vừa dán. Toàn bộ việc này tốn khoảng 5 giây và gần như 0 đồng nếu dùng embedding
local và model rẻ hoặc local.

Cơ chế RAG cụ thể như sau:

```
Nạp tài liệu (một lần, khi có tài liệu mới):
  Tài liệu → cắt thành đoạn nhỏ (chunk) → embed mỗi đoạn thành vector số →
  lưu vector + đoạn gốc vào một kho lưu trữ vector (vector store)

Trả lời câu hỏi (mỗi lần người dùng hỏi):
  Câu hỏi → embed thành vector → so sánh với các vector đã lưu →
  lấy ra k đoạn giống câu hỏi nhất → dán [k đoạn đó] + [câu hỏi] vào prompt →
  gửi cho LLM → LLM trả lời dựa trên đoạn được cung cấp, kèm trích nguồn
```

Phép so sánh dễ hình dung nhất: train lại giống như bắt một người *học thuộc lòng* toàn bộ
một cuốn sách dày trước khi thi (tốn thời gian, tốn công, và nếu sách đổi thì phải học lại từ
đầu). RAG giống như cho phép người đó *mang sách vào phòng thi* (open-book exam) — không cần
học thuộc, chỉ cần biết tra đúng trang khi cần, và khi sách đổi nội dung thì chỉ cần thay cuốn
sách mới, không phải học lại gì cả. Model không "biết" tài liệu của bạn theo nghĩa nó đã học
thuộc, nhưng nó *đọc được* tài liệu đó ngay tại thời điểm trả lời, nên trả lời được y như thể
nó biết.

RAG cũng có giới hạn: chất lượng câu trả lời phụ thuộc vào việc tìm đúng đoạn liên quan (nếu
tìm sai đoạn, model vẫn trả lời trôi chảy nhưng dựa trên thông tin sai — đây chính là vấn đề
Mục 5 sẽ nói tới), và tổng độ dài đoạn dán vào prompt bị giới hạn bởi context window (cửa sổ
ngữ cảnh) của model. Nhưng so với chi phí và thời gian của việc train lại, RAG gần như luôn là
lựa chọn hợp lý hơn cho bài toán "dạy model thứ nó chưa biết mà không cần train" — và đó chính
xác là bài toán của dự án này: một app hỏi đáp dựa trên tài liệu do chính bạn nạp vào.

## Vì sao phải ghim phiên bản Python

Máy bạn hiện đang cài sẵn Python 3.14.4 — một phiên bản rất mới. Nghe có vẻ "mới hơn thì tốt
hơn", nhưng trong dự án này nó lại là một vấn đề, vì hai thư viện cốt lõi của Machine
Learning — `torch` (PyTorch, thư viện tính toán tensor và chạy model) và `sentence-transformers`
(dùng để chạy model embedding) — chưa phát hành **wheel** cho Python 3.14 tại thời điểm viết
bài này.

**Wheel** là gì? Đó là định dạng gói cài đặt đã được biên dịch sẵn (file `.whl`) cho một tổ hợp
cụ thể: phiên bản Python + hệ điều hành + kiến trúc CPU (và với các thư viện GPU như `torch`,
còn thêm cả phiên bản CUDA — nền tảng tính toán của NVIDIA). Khi bạn gõ `pip install torch`,
pip đi tìm một file wheel khớp đúng tổ hợp máy bạn đang chạy, tải về, giải nén — xong, không
cần biên dịch gì thêm, mất vài chục giây.

Vấn đề xảy ra khi **không có wheel** khớp với máy bạn. Với `torch`, mã nguồn bên dưới là hàng
trăm nghìn dòng C++/CUDA; "build từ nguồn" (tự biên dịch lại từ mã nguồn thay vì tải bản có
sẵn) đòi hỏi đúng phiên bản trình biên dịch, đúng phiên bản CUDA Toolkit, đủ RAM để biên dịch,
và có thể mất hàng giờ — với xác suất lỗi giữa chừng rất cao, đặc biệt với người mới chưa từng
cấu hình môi trường biên dịch C++. Vì Python 3.14 quá mới, các đội phát triển thư viện chưa kịp
build và phát hành wheel cho nó. Kết quả nếu cứ dùng 3.14: lệnh cài đặt hoặc báo lỗi thẳng, hoặc
âm thầm chuyển sang build từ nguồn rồi lỗi giữa chừng — cả hai đều là trải nghiệm tệ cho người
mới.

Giải pháp không phải là gỡ Python 3.14.4 đi. Giải pháp là dùng **`uv`** — một công cụ quản lý
project và phiên bản Python (viết bằng Rust, chạy rất nhanh) có khả năng tự tải về một bản
Python khác (ví dụ 3.12 — phiên bản đã được các thư viện ML hỗ trợ đầy đủ) **riêng cho từng
project**, hoàn toàn tách biệt với Python hệ thống. Nói cách khác: Python 3.14.4 đang cài trên
máy bạn vẫn nằm nguyên đó, dùng cho việc khác nếu cần; project `hoc-ai` sẽ có một bản Python
3.12 riêng, do `uv` quản lý, chỉ project này thấy và dùng.

Cơ chế ghim phiên bản nằm ở một file tên `.python-version` — chỉ chứa một dòng, ví dụ `3.12`.
Khi bạn chạy bất cứ lệnh nào qua `uv` (ví dụ `uv run pytest`), `uv` đọc file này, kiểm tra xem
đã có Python 3.12 chưa; nếu chưa, tự tải về (không cần bạn tự đi tìm trình cài đặt Python trên
mạng); nếu có rồi, dùng luôn. Nhờ vậy, dù bạn chuyển sang máy khác, hay quay lại project sau
sáu tháng, lệnh `uv run` luôn dùng đúng phiên bản Python mà project đã ghim — không phụ thuộc
vào việc máy đó đang có Python hệ thống là bản nào.

## Môi trường ảo và khoá phụ thuộc

Giả sử bạn có hai project Python trên cùng một máy: project A cần `numpy` bản 1.24, project B
cần `numpy` bản 2.0 vì dùng tính năng mới hơn. Nếu cả hai project cùng cài thư viện thẳng vào
Python hệ thống, chỉ có thể tồn tại một bản `numpy` tại một thời điểm — cài bản này cho B thì
A hỏng, ngược lại. Tình huống này gọi là "dependency hell" (địa ngục phụ thuộc), và nó là lý do
mỗi project Python nghiêm túc đều cần **môi trường ảo** (virtual environment) riêng.

Môi trường ảo là một thư mục con chứa bản sao (hoặc liên kết) riêng của trình thông dịch Python
và một nơi cài đặt thư viện (site-packages) riêng, tách biệt hoàn toàn khỏi Python hệ thống và
khỏi môi trường ảo của các project khác. Khi bạn "kích hoạt" môi trường ảo của project A, lệnh
`python` và `pip` trong terminal đó trỏ vào bản riêng của A — cài gì, xoá gì cũng chỉ ảnh hưởng
project A. `uv` tự tạo và quản lý môi trường ảo này (thường nằm ở thư mục `.venv/`) mỗi khi bạn
chạy `uv sync` hoặc `uv run`, bạn không cần tự gõ lệnh tạo môi trường ảo theo cách truyền thống.

Trong môi trường đó, hai file đóng hai vai trò khác nhau, dễ nhầm nếu không phân biệt rõ:

- **`pyproject.toml`** khai báo bạn *muốn gì* — ví dụ `fastapi>=0.100`, tức "cần FastAPI, bản
  100 trở lên, phiên bản cụ thể nào cũng được". Đây là danh sách mong muốn, viết bằng tay, ít
  thay đổi.
- **`uv.lock`** ghi lại *chính xác cái gì đã được cài* — sau khi `uv` giải quyết toàn bộ ràng
  buộc (kể cả các thư viện phụ mà FastAPI âm thầm kéo theo), nó chốt lại từng thư viện ở đúng
  một phiên bản cụ thể, kèm mã băm (hash) để xác minh file tải về không bị đổi khác. File này
  do `uv` tự sinh ra, không tự tay sửa.

Ví von cho dễ nhớ: `pyproject.toml` giống công thức nấu ăn ghi "cần bột mì, cần trứng" — không
ghi rõ nhãn hiệu, ngày sản xuất. `uv.lock` giống hoá đơn đi chợ — ghi chính xác bạn đã mua bột
mì nhãn hiệu nào, lô hàng nào, hôm nay. Nếu đưa công thức cho hai người khác nhau đi chợ, họ có
thể mua hai nhãn hiệu bột mì khác nhau (kết quả món ăn hơi khác); nhưng nếu đưa đúng hoá đơn,
ai đi mua cũng ra đúng nguyên liệu y hệt.

Đây là lý do `uv.lock` **phải được commit vào Git**, trong khi thư mục `.venv/` thì không (nó
được liệt vào `.gitignore` vì có thể tái tạo lại bất cứ lúc nào từ lock file, và thường nặng
hàng trăm MB). Khi CI (Continuous Integration — hệ thống tự động chạy test mỗi lần bạn đẩy code
lên) chạy `uv sync`, nó đọc đúng `uv.lock` và cài lại chính xác từng phiên bản đã ghi — đảm bảo
CI chạy trên đúng bộ thư viện y hệt máy bạn, không phải một bộ thư viện "mới nhất tính đến hôm
nay" vốn có thể đã đổi khác và gây lỗi không đoán trước được. Không commit `uv.lock` nghĩa là
mỗi lần cài lại, thư viện có thể lệch phiên bản, và một lỗi "chạy trên máy tôi thì được" trở nên
gần như chắc chắn xảy ra.

## Vì sao viết test trước

Bạn chưa từng viết test bao giờ. Bài học này đưa việc viết test lên ngay từ Chặng 0 vì ba lý do
cụ thể, không phải vì "ai cũng bảo nên viết test":

**Lý do 1 — học một mình, không ai review.** Trong công việc bình thường, đồng nghiệp đọc code
của bạn trước khi merge, chỉ ra chỗ sai. Bạn học một mình, không có ai đóng vai đó hằng ngày.
Test tự động đóng vai người review: nó không mệt, không bỏ sót, và chạy lại được bất cứ lúc
nào miễn phí.

**Lý do 2 — code AI sai âm thầm.** Đây là lý do đặc thù của dự án RAG, khác hẳn lập trình
thông thường. Nếu một hàm cộng hai số trả sai kết quả, bạn nhận ra ngay vì con số rõ ràng sai.
Nhưng nếu hệ thống retrieval (bước tìm đoạn tài liệu liên quan) trả về *sai đoạn* — đoạn không
thật sự liên quan đến câu hỏi — LLM vẫn có thể ghép ra một câu trả lời nghe hoàn toàn trôi
chảy, tự tin, đúng ngữ pháp. Nhìn bằng mắt, câu trả lời "có vẻ ổn"; chỉ khi so với đoạn tài liệu
gốc mới thấy nó không hề dựa trên nội dung đúng. Đây gọi là sai âm thầm — không có tiếng động
báo lỗi nào cả nếu không chủ động kiểm tra. Test viết đúng cách (ví dụ: kiểm tra đoạn trả về có
đúng `chunk_id` mong đợi hay không) bắt được lỗi này ngay cả khi câu trả lời bằng lời nghe có
vẻ hợp lý.

**Lý do 3 — CI xanh là bằng chứng nhà tuyển dụng nhìn thấy.** Một repo GitHub có dấu tick xanh
(build đang chạy tốt) trên mỗi commit là tín hiệu trực quan, không cần đọc code, cho thấy người
viết có kỷ luật kỹ thuật. Đây là bằng chứng kiểm chứng được — đúng thứ mục tiêu dự án này nhắm
tới (xem lại mục tiêu: "có bằng chứng kiểm chứng được").

Cách viết test trước đi theo một vòng lặp ba bước, gọi là **đỏ → xanh → refactor**:

```
1. ĐỎ (red)      — viết một test cho hành vi CHƯA tồn tại, chạy thử, thấy nó thất bại
                    (đỏ) vì code thật chưa được viết.
2. XANH (green)  — viết code tối giản vừa đủ để test đó chuyển sang thành công (xanh).
                    Không viết thêm gì ngoài mức cần thiết.
3. REFACTOR      — dọn lại code cho sạch, dễ đọc hơn, mà KHÔNG đổi hành vi; chạy lại
                    test, vẫn phải xanh. Nếu đỏ trong bước này, nghĩa là refactor đã
                    lỡ tay đổi hành vi.
```

Từ Task 3 của Chặng 0 trở đi, mọi module trong dự án đều đi theo đúng vòng lặp này: trước khi
viết `app/core/config.py`, sẽ có một file test viết trước và chạy thử để xác nhận nó đỏ (vì
module chưa tồn tại); Task 4 cũng vậy với `app/core/doctor.py` — các hàm như `kiem_tra_lenh`
đều có test viết trước, chạy đỏ, rồi mới viết code khiến nó xanh. Không có ngoại lệ "viết code
trước rồi test sau" trong dự án này, kể cả với những hàm rất nhỏ.

## Git: nhánh, commit, Pull Request

Không commit thẳng lên `main` vì `main` được xem là dòng code "luôn chạy được" — bất cứ ai
(kể cả bạn, ba tháng sau) mở repo ra cũng mong `main` là bản ổn định nhất. Nếu commit thẳng vào
đó khi đang thử nghiệm dở dang, một lần lỡ tay có thể để lại code hỏng ngay tại điểm mà mọi
người (và CI) coi là chuẩn.

**Nhánh (branch)** là một con trỏ di động chỉ vào một chuỗi commit — bạn có thể tạo một nhánh
mới xuất phát từ `main`, commit thoải mái trên đó mà không ảnh hưởng gì đến `main`, rồi khi
xong mới gộp (merge) ngược lại:

```
main     ──●───────────────●────────────●──────→
             \                          ╱
feat/doctor   ●───●───●───●────────────╯
              (commit)  (commit)  (merge vào main)
```

Nếu nhánh `feat/doctor` có lỗi giữa chừng, `main` hoàn toàn không bị ảnh hưởng — bạn có thể xoá
nhánh đó, tạo lại từ đầu, mà không mất gì ở `main`.

**Pull Request (PR)** là một yêu cầu, tạo trên GitHub, xin gộp các thay đổi từ một nhánh (ví dụ
`feat/doctor`) vào một nhánh khác (thường là `main`). PR không phải một khái niệm Git thuần —
Git chỉ biết nhánh và commit; PR là tính năng của nền tảng lưu trữ (GitHub, GitLab...) xây thêm
lên trên Git, cho một trang xem được toàn bộ khác biệt (diff), để lại bình luận trên từng dòng,
và tự động chạy CI kiểm tra trước khi cho phép gộp.

Học một mình thì tự mở PR và tự review PR của chính mình vẫn có ích, vì hai lý do: thứ nhất,
đọc code trên giao diện diff của PR là một góc nhìn khác hẳn so với đọc trong editor — bạn hay
phát hiện ra debug code còn sót lại, dòng comment thừa, quên chưa thêm test, hoặc commit message
không rõ nghĩa mà lúc code trong editor không để ý. Thứ hai, tự review PR xây thành thói quen
sẵn có; khi sau này làm việc thật với người khác, quy trình "mở PR → review → merge" đã là phản
xạ chứ không phải điều phải học lại từ đầu.

Một điểm dễ gây bối rối khi đọc JD: có JD ghi "Pull Request" (thuật ngữ của GitHub), có JD ghi
"Merge Request" (thuật ngữ của GitLab) — **cùng một khái niệm**, chỉ khác tên do khác nhà cung
cấp nền tảng lưu trữ Git. JD của dự án này ghi cả hai ("Git/GitLab Workflow, Merge Request"),
nên cần biết cả hai tên để không hiểu nhầm đó là hai kỹ năng khác nhau.

Để commit message có ý nghĩa và dễ lọc lại sau này, dự án dùng quy ước **Conventional
Commits** — mỗi commit message bắt đầu bằng một tiền tố nêu rõ loại thay đổi:

| Tiền tố | Ý nghĩa | Ví dụ |
|---|---|---|
| `feat:` | Thêm tính năng mới | `feat: them module cau hinh co kieu` |
| `fix:` | Sửa lỗi | `fix: sua loi kiem_tra_lenh tra sai bat_buoc` |
| `test:` | Thêm hoặc sửa test | `test: them test cho chay_kiem_tra` |
| `docs:` | Thay đổi tài liệu | `docs: them bai hoc lesson-00 nen mong` |
| `chore:` | Việc lặt vặt, không đổi hành vi (cập nhật dependency...) | `chore: nang cap uv.lock` |
| `ci:` | Thay đổi cấu hình CI | `ci: them buoc chay ruff` |

Lợi ích: nhìn lịch sử commit là biết ngay loại thay đổi mà không cần mở ra đọc, và nhiều công
cụ có thể tự sinh changelog dựa vào các tiền tố này.

## Terminal Linux và cách đọc log

JD ghi thẳng "Docker, Linux, đọc log". Docker để dành cho Chặng 4; mục này lo phần nền của
Linux — các lệnh terminal tối thiểu và thói quen đọc log — vì cả hai đều cần trước khi Docker
xuất hiện.

Các lệnh tối thiểu, mỗi lệnh gắn với tình huống thực tế cần đến nó:

| Lệnh | Khi nào cần |
|---|---|
| `pwd` | Bị lạc giữa nhiều tầng thư mục, không chắc terminal đang đứng ở đâu |
| `ls -la` | Kiểm tra một file (kể cả file ẩn như `.env`, `.git`) có tồn tại không, quyền ra sao |
| `cd` | Di chuyển giữa các thư mục của project |
| `cat` | Xem nhanh toàn bộ nội dung một file ngắn |
| `less` | Xem một file dài (log hàng nghìn dòng) theo trang, cuộn và tìm được, không tràn màn hình như `cat` |
| `tail -f` | Theo dõi log của một tiến trình đang chạy, thấy dòng mới ngay khi nó xuất hiện |
| `grep -n` | Tìm dòng chứa từ khoá (ví dụ `ERROR`) kèm số dòng, giữa hàng nghìn dòng log |
| `find` | Tìm một file khi nhớ tên nhưng quên nó nằm thư mục nào |
| `chmod +x` | Một script `.sh` báo "Permission denied" khi chạy trực tiếp — cấp quyền thực thi |
| `which` | Nghi ngờ máy đang chạy nhầm phiên bản chương trình (Python hệ thống thay vì Python của `uv`) |
| `echo $PATH` | Debug lỗi "command not found" |
| `df -h` | Máy chỉ còn 38GB đĩa trống — kiểm tra chỗ nào đang chiếm dung lượng |
| `free -h` | Máy chạy chậm, nghi ngờ hết RAM (chỉ có 14GB, dễ hết khi chạy nhiều thứ) |
| `nvidia-smi` | Nghi ngờ hết VRAM, hoặc muốn biết model đang chạy có thật sự dùng GPU không |

Ba khái niệm nền bắt buộc phải hiểu rõ:

**1. `PATH` là gì.** `PATH` là một biến môi trường (environment variable — giá trị hệ điều hành
giữ sẵn cho mọi chương trình đọc) chứa danh sách thư mục, ngăn cách bởi dấu `:`. Gõ một lệnh,
ví dụ `git`, shell đi lần lượt từng thư mục trong `PATH` tìm file thực thi tên đó; thấy ở đâu
thì chạy ở đó. `git` chạy được vì trình cài Git đã đặt file thực thi vào một thư mục nằm trong
`PATH`; `docker` báo "command not found" đơn giản vì chưa cài, nên không thư mục nào trong
`PATH` có file đó — không phải lỗi bí ẩn, chỉ là không tìm thấy. Hàm `kiem_tra_lenh` ở Task 4
làm đúng việc này bằng code: gọi `shutil.which(ten_lenh)`, tức là chỉ đang tra `PATH` hộ bạn —
y hệt gõ `which git` bằng tay, khác ở chỗ tự động và trả về kết quả có cấu trúc.

**2. `stdout` và `stderr` là hai luồng khác nhau.** Mỗi chương trình có hai đường xuất riêng:
`stdout` (standard output — luồng ra chuẩn) mang kết quả bình thường, `stderr` (standard
error — luồng lỗi chuẩn) mang thông báo lỗi. Tách riêng có chủ đích, để chương trình khác có
thể lấy kết quả mà bỏ qua lỗi, hoặc ngược lại. Đây là lý do `lenh > file.txt` (dấu `>` chỉ
chuyển hướng `stdout`) vẫn thấy lỗi hiện ra trên màn hình — `stderr` không hề bị chuyển hướng.
Muốn gom cả hai vào một file: `lenh > file.txt 2>&1` — đọc là "cho luồng 2 (`stderr`) trỏ đến
cùng chỗ luồng 1 (`stdout`) đang trỏ tới"; vì `stdout` đã chuyển hướng vào file trước đó,
`stderr` đi theo vào đúng file đó. Thứ tự quan trọng: chuyển hướng `stdout` trước, `2>&1` sau.

**3. Mã thoát (exit code).** Mọi chương trình khi kết thúc trả về một số nguyên cho hệ điều
hành: `0` là thành công, khác `0` là thất bại. `echo $?` ngay sau một lệnh in ra mã thoát của
nó. Đây là cơ chế CI dùng để biết build "xanh" hay "đỏ": mỗi bước (lint, test...) chỉ là chạy
một lệnh rồi kiểm tra mã thoát — `0` thì qua, khác `0` thì dừng và báo đỏ. Đây cũng là lý do
hàm `main` ở Task 4 phải trả về kiểu `int` chứ không phải `None`: giá trị đó được đưa thẳng vào
`sys.exit()` và trở thành mã thoát của cả chương trình khi chạy từ dòng lệnh — đúng cơ chế
`0`/khác-`0` vừa nói, không phải quy ước tuỳ tiện.

Cuối cùng, thói quen đọc log — thứ JD gọi thẳng là "đọc log" — gói gọn trong ba bước:

```
1. Đọc dòng lỗi ĐẦU TIÊN, không phải dòng cuối.
   Một lỗi thường kéo theo hàng loạt lỗi phụ ở phía sau; dòng cuối cùng
   thường chỉ là hệ quả, sửa nó không giải quyết gốc vấn đề.

2. Tìm tên file và số dòng trong stack trace (dấu vết ngăn xếp — danh sách
   các lời gọi hàm dẫn đến chỗ lỗi).
   Đó chính xác là chỗ cần mở file ra xem, không phải đoán mò nơi khác.

3. Không đoán.
   Nếu log hiện tại chưa đủ thông tin để biết vì sao lỗi, việc cần làm là
   thêm log (print/logging) vào đúng chỗ nghi ngờ, chạy lại, đọc log mới,
   RỒI mới sửa code. Sửa trước khi biết chắc nguyên nhân thường chỉ che
   triệu chứng, không giải quyết gốc rễ.
```

## Tự kiểm tra

1. Vì sao 8GB VRAM đủ cho dự án này?
2. RAG thay thế cho việc gì?
3. Vì sao không dùng Python 3.14 có sẵn?
4. Vì sao phải commit `uv.lock`?
5. Vì sao code AI cần test hơn code thường?
6. Merge Request và Pull Request khác nhau thế nào?
7. Mã thoát khác `0` nghĩa là gì, và CI dùng nó để làm gì?
