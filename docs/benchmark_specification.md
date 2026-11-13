# Phase 2 – Benchmark Specification (ccbench v1)

> Tài liệu này mô tả **thiết kế** benchmark (dataset, ground truth, baseline, metric, giao thức). Kết quả chạy thật nằm ở `docs/pilot_experiment_report.md`. Ngưỡng giả thuyết được đóng băng trong `configs/prereg.json` trước main run (13/11/2026).

## 1. Tổng quan

```
fixture_repo/frostline  ──AST──►  RepoIndex (278 units)  ──►  ProgramGraph / NameGraph / BM25
        │                                                           │
        │ execute (subprocess, -I)                                  ▼
        ▼                                                   ContextBuilder (E0–E5 + A1–A5)
  Oracle worker ──► ground truth, dynamic trace,                    │  budget B
                    mutation-based impact                           ▼
        │                                                prompt p1 ──► Provider (claude_cli | anthropic | openai_compat | mock)
        ▼                                                           │
  data/items.v1.jsonl  ─────────────────────────────────►  rule-based scorer ──► results/<exp>/results.jsonl
                                                                    │
                                                                    ▼
                                                 aggregate + stats + SVG + report.md
```

Toàn bộ chỉ dùng Python standard library (không cần pip, không GPU, không tải model).

## 2. Repository fixture `frostline`

Hệ thống điều phối bưu kiện kho lạnh, viết tay cho benchmark (không lấy từ dự án mở → giảm rủi ro model đã ghi nhớ). 74 file, 278 code unit, ≈ 26K token thật (≈ 19K token ước lượng cũ; xem §6).

| Tầng | Package | Đặc điểm dùng để đánh giá |
|---|---|---|
| API | `api/` (router decorator, handlers, serializers, app wiring) | Route → handler gián tiếp qua `@route`; thứ tự import trong `app.py` quyết định plugin nào thắng |
| Service | `services/` | Event bus: `publish("shipment.booked")` → subscriber ở module khác |
| Pricing | `pricing/` | Strategy pattern + kế thừa 3 tầng `Flat ← Tiered ← Distance` (override + `super()`) |
| Domain | `domain/rules/` | ABC `SurchargeRule`, `PercentageRule`, `PerParcelRule`; rule đăng ký qua `@register` |
| Plugins | `plugins/` | `PartnerRemoteRule` **ghi đè** đăng ký `remote` bằng `replace=True` |
| Config | `config/` | `DEFAULTS` + `PROFILES` (default / express / eco) chọn implementation qua registry |
| Storage | `storage/` | Repository pattern trên in-memory DB |
| Shared | `utils/`, `pricing/money.py` | Dùng chung bởi nhiều module (round_money, normalize_*) |
| Distractors | `legacy/`, `integrations/`, `warehouse/` | 3 hàm `calculate_fee` khác nghĩa; `normalize` vs `normalize_code`; `round_money` vs `round_money_even`; `volumetric_weight` vs `volumetric_weight_air`; `legacy.QuoteEngine`, `legacy.NorthTax` không được import |

## 3. Dataset v1 (64 item)

| Level | Nội dung | n | Ví dụ |
|---|---|---|---|
| L1 | Một file | 13 | `round_money_even(2.345)`; TIERS biên inclusive |
| L2 | Nhiều file, quan hệ trực tiếp | 10 | `/storage/estimate` total; Greedy vs Dijkstra path |
| L3 | Cross-module, gián tiếp (registry/config/event) | 13 | Ai thực sự tính phụ phí `remote`? Bảng nào nhận row khi POST /quotes? |
| L4 | Data/control flow qua nhiều tầng | 12 | Payload → `total_cents` lưu xuống DB; late fee của invoice |
| L5 | Impact analysis | 16 | Nếu `X` trả về +1 thì scenario nào (S1–S8) đổi response? |

40/64 item gắn nhãn `indirect`, 29/64 gắn `lookalike` (có đáp án "look-alike" được **tính bằng thực thi** cho phân loại lỗi `distractor_confusion`). Danh mục đầy đủ: `docs/dataset_catalog.md`.

**Mỗi item có:** `id`, `question`, `answer` (ground truth), `answer_type`, `gold_evidence` (unit + file + dòng), `level`, `qtype`, `indirect`, `lookalike`, `rubric`, `explanation`, `distractor_answer`, `oracle` (đoạn code tạo ground truth), `executed_units`, `verified_by`.

### 3.1 Ground truth – không dùng LLM
1. **Execution oracle**: mỗi item có đoạn code Python chạy trên fixture trong subprocess cô lập (`python -I`, không ghi bytecode) → `ANSWER`.
2. **Dynamic trace**: `sys.setprofile` ghi mọi hàm fixture thực sự chạy; build **thất bại** nếu một unit gold kiểu hàm/method không được thực thi (trừ unit tĩnh khai báo rõ, ví dụ `register` chạy lúc import).
3. **Mutation-based impact (L5)**: thay hàm đích bằng wrapper (+1 / đảo list / lower / trả rỗng) **trong bộ nhớ** (module globals, class attribute, container cấp module như danh sách subscriber) — không sao chép hay sửa file. Chạy 8 scenario trước/sau, so sánh JSON response. Kiểm tra undo sạch sau mỗi đột biến.
4. `build-dataset --check` tái tạo toàn bộ ground truth và so SHA (test tích hợp tự động).

Validation đã bắt được 2 lỗi do chính người thiết kế viết sai kỳ vọng (ghi lại ở pilot report §2) — minh chứng giá trị của ground truth thực thi.

## 4. Điều kiện thực nghiệm

| Mã | `strategy` | Định nghĩa | Budget |
|---|---|---|---|
| E0 | `oracle` | Unit gold đầy đủ (+ class header). Cận trên. | không giới hạn |
| E1 | `none` | Chỉ câu hỏi. Sàn / kiểm tra rò rỉ. | 0 |
| E2 | `full` | Toàn repo theo thứ tự path, **cắt prefix** khi đầy budget | 2K/4K/8K/16K + unbounded (cả repo) |
| E3 | `fixed` | 10 file "kiến trúc" cố định cho mọi câu hỏi | 2K–16K (tối đa ≈ 7K vì tập file nhỏ) |
| E4 | `bm25` | Okapi BM25 trên unit (path + code), lấy top tới khi đầy budget | 2K–16K |
| E4b | `bm25_namegraph` | BM25 top-3 + mở rộng callee **theo tên** (grep-like, gồm cả look-alike), rồi phần còn lại theo BM25 | 2K–16K |
| E5 | `dgc` | **Dependency-Guided Context** (bên dưới) | 2K–16K |
| A1 | `dgc_no_dispatch` | E5 nhưng đồ thị không có cạnh registry/config/event/route | 4K, 8K |
| A2 | `dgc_no_expansion` | Chỉ seed (không lan truyền đồ thị) + BM25 | 4K, 8K |
| A3 | `dgc_no_ranking` | Tập mở rộng nhưng xếp theo thứ tự repo thay vì điểm | 4K, 8K |
| A4 | `dgc_no_skeleton` | Không thêm chữ ký (skeleton) khi unit không vừa budget | 4K, 8K |
| A5 | `dgc_no_reverse` | Không dùng cạnh ngược (caller) | 4K, 8K |

**DGC (E5)** — chỉ dùng phân tích tĩnh, không dùng ground truth:
1. *Seed localization*: route literal (`POST /quotes`), event topic, config key, tên đăng ký registry, định danh/đường dẫn file trong câu hỏi, top-5 BM25.
2. *Program graph*: import-aware call resolution, class hierarchy analysis (self-call → override ở subclass), `super()`, instantiation, kiểu thuộc tính `self.x = Cls(...)`, duck-call trọng số thấp; cạnh *dispatch*: `resolve(kind, settings.get(key))` → class đăng ký (giá trị DEFAULTS 0.95, giá trị profile 0.6, còn lại 0.3), `publish(topic)` → subscriber, `settings.get(key)` → định nghĩa config.
3. *Expansion*: best-first, điểm = seed × Π trọng số cạnh × 0.8^depth; câu hỏi impact ưu tiên cạnh ngược (caller), câu hỏi khác ưu tiên cạnh xuôi.
4. *Ranking + packing*: theo điểm; method kéo theo class header; unit không vừa thì thêm skeleton (chữ ký + docstring); phần budget còn lại lấp bằng BM25 để mọi chiến lược dùng budget tương đương.

Mọi chiến lược render cùng định dạng (`### file:` + số dòng) và cùng prompt `p1` (câu hỏi đặt trước và sau context như [2]; đáp án JSON `{answer, evidence, explanation}`).

## 5. Metric

| Metric | Định nghĩa |
|---|---|
| Accuracy / EM | Rule-based theo `answer_type`: number so sánh Decimal; string chuẩn hóa; set = bằng tập; list = đúng thứ tự; json = cấu trúc |
| Precision / Recall / F1 | Cho đáp án tập/list (L3 tables, L5 scenarios…) |
| Evidence precision / recall | Trích dẫn `path:line` trúng dòng thuộc unit gold / tỷ lệ unit gold được trích |
| Context recall (hard / soft) | Tỷ lệ unit gold có **đầy đủ** trong context đã cung cấp (soft: skeleton = 0.5) |
| Token | `budget` (giới hạn) · `context_est_tokens` (ước lượng của context đã cung cấp) · `prompt_est_tokens` · `input_tokens` (provider báo, gồm overhead harness) · `output_tokens` (gồm thinking) · số unit retrieved vs provided |
| Latency | Thời gian phản hồi provider báo (`duration_ms`) hoặc đo wall-clock |
| Cost per task / per correct | `total_cost_usd` từ Claude CLI (giá niêm yết tương đương, *không phải số tiền bị trừ* với gói subscription) |
| Success rate | Gọi thành công **và** parse được JSON / tổng job |
| Distractor-confusion rate | Đáp án sai trùng đáp án look-alike (đã tính bằng thực thi) |
| Error class | `correct` · `distractor_confusion` · `missing_evidence` (CR<1) · `use_failure` (CR=1 mà vẫn sai) · `format_error` |

**LLM-as-a-Judge** (`python -m ccbench judge`) chỉ chấm phần `explanation` (rubric 0–2), bắt buộc judge ≠ model được đánh giá, và báo cáo Cohen's κ so với chấm rule-based. **Kiểm tra thủ công**: mỗi report sinh `manual_audit_sample.csv` (40 bản ghi phân tầng theo level × đúng/sai) có cột `human_verdict`.

## 6. Token budget

Ước lượng ký tự→token (`ccbench/tokens.py`). Hiệu chỉnh trên usage thật của `claude-haiku-5-5` (smoke run 13/11): với 3,2 ký tự/token, token thật ≈ 478 + 1,354 × ước lượng → đổi hằng số thành **2,35 ký tự/token** để budget ≈ token thật của context. Report luôn in hồi quy `input_tokens ~ prompt_est_tokens` để kiểm tra lại. Overhead cố định của Claude Code harness (≈ 480–630 token) được tách bằng intercept.

## 7. Giao thức

1. `build-dataset` → kiểm tra ground truth (fail = dừng).
2. `context-stats` (offline) → context recall theo strategy × budget (không cần model).
3. Đóng băng `configs/prereg.json`.
4. Main run mỗi model: 64 item × 33 điều kiện = 2.112 job; thứ tự item xáo trộn theo seed (kết quả dở dang vẫn phủ mọi level); resume theo `job_key`.
5. Lặp lại (`repeat_haiku.json`, 3 lần trên E4/E5 @4K) để đo flip-rate.
6. `report` → `summary.csv/json`, `report.md`, SVG, audit CSV.

## 8. Phân tích thống kê (đăng ký trước)

| Giả thuyết | Phép so sánh | Tiêu chí |
|---|---|---|
| H1a | `dgc − bm25` @2K và @4K, item L3–L5, paired | Supported nếu Δ ≥ 10pp và CI95 bootstrap > 0; refuted nếu cận trên < 3pp |
| H1b | `(dgc@2K − full@2K) − (dgc@16K − full@unbounded)` | Supported nếu CI95 > 0 |
| H2a | `acc(dgc│CR=1) − acc(bm25│CR=1)` (gộp budget) | Tương đương nếu CI90 ⊂ ±5pp (TOST) |
| H2b | Tỷ lệ sai của E0 oracle trên L4–L5 | Supported nếu ≥ 15% và CI95 > 0 |
| H3a | `dgc − dgc_no_dispatch` trên item indirect vs direct @4K/8K | Supported nếu Δ_indirect ≥ 10pp, CI > 0 và Δ_direct < 3pp |
| H3b | Distractor-confusion trên item look-alike, bm25 vs dgc (McNemar) | Supported nếu bm25 > dgc, p < 0.05 |

Paired bootstrap theo item (10.000 lần), McNemar chính xác, Holm cho họ {H1a×2, H1b, H3a×2, H3b} mỗi model, Wilson CI cho tỷ lệ. Mọi so sánh khác là thăm dò.

## 9. Tái lập & tài nguyên

- Mỗi run: `results/<name>-<timestamp>/config.json` (config + provenance: dataset SHA, fixture hash, prompt version, tham số hiệu lực của provider — nhiệt độ/seed được ghi `unsupported` nếu provider không hỗ trợ), `results.jsonl` (raw response, ground truth, điểm, token, latency, cost). Không ghi đè; `run results/<exp>/config.json` tạo experiment mới từ cấu hình đã lưu.
- Record **không chứa source code** (chỉ id unit + SHA context); prompt dựng lại tất định.
- Pool worker cố định, LRU context trong RAM, một thư mục tạm duy nhất cho mỗi run (`tempfile.TemporaryDirectory`, tự xoá), `python -m ccbench clean` xoá cache.
