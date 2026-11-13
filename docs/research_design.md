# Phase 1 – Research Design

**Đề tài 5-KH · Chương 13 · IT5440** — *Repository-Level Code Understanding under Limited Context Budget*

> **Trạng thái:** bản nháp Phase 1, 13/11/2026. Tài liệu này **chưa chứa kết quả thực nghiệm nào**. Mọi con số dưới đây hoặc trích từ tài liệu có sẵn (ghi nguồn), hoặc là **ngưỡng đề xuất** cần nhóm chốt trước khi chạy (pre-registration).
>
> **Cập nhật sau pilot (13/11/2026):** kết quả thật và trạng thái từng giả thuyết nằm ở `docs/pilot_experiment_report.md`. Tóm tắt: H1b được ủng hộ; H1a chỉ đạt với Haiku @2K khi chưa hiệu chỉnh; H2b và H3a bị bác bỏ; DGC không vượt BM25 sau hiệu chỉnh. Gold evidence viết tay chưa đủ cho L4, nên v2 sẽ dùng gold theo trace.
>
> **Quy ước:** [1]–[4] là 4 bài trong `4-papers/`. "Pilot-11/11" = `experiment/IT5440_5KH_BaoCao_Pilot.pdf`. "Đánh giá-12/11" = `experiment/danh-gia-tong-hop-12-11-2026.md`. "Đề cương" = `analysis/IT5440_5KH_PhanTich_va_DeCuong.pdf`.

---

## 0. Đã đọc những gì, ở mức nào

| Tài liệu | Mức đọc | Ghi chú |
|---|---|---|
| `analysis/abstract.md` | Toàn bộ | Hướng hiện tại: tách vị trí / lexical / aggregation (H-ret vs H-agg) trên toolz |
| Đề cương (43 tr.) | Toàn bộ | RQ1–RQ3, điều kiện C0–C4, K1–K5, rủi ro R1–R7 |
| Pilot-11/11 | Toàn bộ | qwen2.5-coder 7B local, SemTrace-Dep, C0–C3 |
| Đánh giá-12/11 | Toàn bộ | DeepSeek-V4-Flash + Qwen3.6-27B trên toolz, TOST, power simulation |
| [2] Sense & Sensitivity | Phần Limitations, Conclusion; phần còn lại qua Đề cương | |
| [3] Lin et al. | Bảng research agenda (hướng "Repository context and agents") | |
| [4] Code Comprehensor | Qua Đề cương (mục I.2.4) | |
| [1] Survey Zhang et al. | Qua Đề cương (mục I.2.1) | 417 KB text, chỉ dùng làm nguồn phân loại |

Giới hạn: [1] và [4] **không** được đọc lại toàn văn trong phiên này; các nhận định về chúng dựa trên Đề cương (đã phân tích toàn văn) và cần nhóm đối chiếu khi trích dẫn.

---

## 1. Tổng hợp: các nghiên cứu đã làm gì

### 1.1 Phương pháp, biến thực nghiệm, benchmark, metric

| | [2] Štorek et al. | [4] Roychowdhury et al. | Nhóm: Pilot-11/11 | Nhóm: toolz (12/11) |
|---|---|---|---|---|
| Đơn vị phân tích | 1 hàm | Kho C/C++ 1,2M–5M dòng | Chuỗi 4 hàm tổng hợp | 1 hàm thư viện toolz (đã đổi tên) |
| Tác vụ | I/O prediction, lexical retrieval | Text→code retrieval; QA qua agent | Output prediction | Output prediction, lexical copy, RTT |
| Biến độc lập | Vị trí, độ dài (20–80 distractor ≈ 4–16K), ngôn ngữ, số chữ số | Cấu hình dữ liệu D1–D3 | C0–C3, vị trí | Vị trí, độ dài 4–32K, k=1/3 mảnh |
| Distractor | Ngẫu nhiên, không liên quan | — | 50% giống cấu trúc + 50% tiện ích | stdlib + toolz |
| Ground truth | Thực thi | LLM sinh (RAGAS) | Thực thi | Thực thi |
| Metric | Exact match, relative drop, sensitivity | Top-1/Top-K, Faithfulness, Answer Correctness (LLM-judge) | Acc, Wilson CI, McNemar | Acc, cluster bootstrap, TOST |
| Chi phí / token | Không báo cáo chi tiết | ~3.200 USD sinh tài liệu | Thời gian local | Token thật |

### 1.2 Hạn chế (do tác giả nêu + nhận xét)

- **[2]**: distractor *ngẫu nhiên, không liên quan ngữ nghĩa* (tác giả nêu là câu hỏi mở: "the relationship between semantic similarity of surrounding code and semantic recall failures remains an open question"); phạm vi tác vụ chỉ I/O + retrieval, chưa có "complex multi-hop reasoning"; chỉ chẩn đoán, không thử biện pháp giảm nhẹ; ngữ cảnh ≤ 16K.
- **[4]**: đánh giá khép kín (câu hỏi do LLM sinh, LLM chấm); không có baseline ngoài (BM25, embedding sẵn có); D3 gộp 2 nguồn nên không ablation được; không kiểm bằng thực thi; chi phí không tái lập được.
- **[3]**: với hướng *Repository context and agents*, câu hỏi mở được nêu nguyên văn: *"Which gains come from retrieval, the model, the harness, tools, or additional retries?"*, bằng chứng tối thiểu yêu cầu: *"controlled component ablations; equalized budgets; … multiple projects"*.

### 1.3 Nhóm đã làm được gì và học được gì (bài học thực nghiệm quan trọng nhất)

| Phát hiện của nhóm | Hệ quả cho thiết kế mới |
|---|---|
| **Trần (ceiling)**: 33/40 item k1 đúng ở cả 9 ô; chỉ ~7 item còn thông tin (Đánh giá-12/11 §3.2) | Item phải có độ khó phân tầng; pilot calibration để loại item luôn đúng ở E1 (no-context) |
| **Truy hồi quá dễ**: câu hỏi gọi thẳng `fn_NNN`, lexical copy 100% (§3.4) | Câu hỏi **không được** nêu tên hàm then chốt; phải đi qua route/config/event → hàm |
| **Hàm "anh em" gây nhiễu**: 108/112 câu sai của `tail` trả kết quả của `take` (§3.1) | Đưa *look-alike siblings* vào kho một cách có hệ thống, và có nhãn để phân tích lỗi |
| **C3 (call-graph closure) đúng ~tuyệt đối trên code tổng hợp** vì không có lời gọi gián tiếp (Pilot-11/11 §5, rủi ro R4) | Kho phải có dispatch gián tiếp (registry, config, override, DI, event bus) mà name-based call graph **bỏ sót** |
| **C2 (chỉ sắp xếp lại) không giúp**, C3 giúp mạnh (24/3, p=5·10⁻⁵) — trên 1 model 7B, 3,7K token | Giả thuyết hợp lý: *chọn lọc* quan trọng hơn *thứ tự* → kiểm lại ở quy mô kho và với budget cố định |
| **Không có lost-in-the-middle** (D = +0,3pp, đạt TOST ±5pp) | Không lấy vị trí làm biến chính nữa; chuyển sang **ngân sách** và **chiến lược chọn ngữ cảnh** |
| Power: chạy lại cùng prompt gần như vô ích; nên tăng biến thể dữ liệu (§4.2) | Dùng nhiều item + paired design; lặp lại chỉ cho ước lượng phi tất định |
| Phi tất định ở T=0: 6,3% prompt đổi đúng/sai qua 3 lần (§3.5) | Lặp lại ≥ 2 lần trên tập con, báo cáo flip-rate |

---

## 2. Khoảng trống nghiên cứu

| Mã | Khoảng trống | Bằng chứng | Mức chắc chắn |
|---|---|---|---|
| G1 | Benchmark hiểu mã dài [2] dùng **1 hàm** + distractor ngẫu nhiên; chưa đo hiểu **quan hệ xuyên file/module** với distractor giống thật | Limitations của [2] | Cao |
| G2 | Hệ thống cấp kho [4] dùng call graph + retrieval nhưng **không ablation**, **không baseline lexical**, **không budget cân bằng**, ground truth do LLM sinh | Đề cương I.2.4; [3] Bảng agenda | Cao |
| G3 | Context construction bằng phân tích chương trình thường được đánh giá trên code mà **call graph theo tên là đủ**; tình huống dispatch gián tiếp (registry/config/override) chưa được tách riêng | Pilot-11/11 §5 (R4); Đề cương II.8.4 | Trung bình–cao (trong phạm vi 4 bài + tài liệu nhóm) |
| G4 | Thiếu phép đo **tách "không đưa đủ bằng chứng vào context" (retrieval failure) khỏi "đưa đủ mà vẫn sai" (use/aggregation failure)** ở mức kho, dưới cùng budget | abstract.md đặt câu hỏi H-ret/H-agg ở mức hàm; chưa có ở mức kho | Trung bình |
| G5 | Impact analysis (thay đổi X ảnh hưởng gì) bằng LLM thường chấm bằng LLM-judge; thiếu ground truth **thực thi được** (mutation-based) | Suy luận từ [4] (RAGAS) | Trung bình |

> ⚠️ **Kiểm tra tính mới chưa hoàn tất.** Ngoài 4 bài, các benchmark cấp kho đã biết (từ kiến thức nền, **chưa xác minh trong phiên này**): RepoQA, RepoBench, CrossCodeEval, Long Code Arena, CodeRAG-Bench, SWE-bench, RepoGraph [Đề cương 9], LongCodeZip [8], SWEzze [10]. Trước khi viết bài, nhóm cần tra cứu có hệ thống các từ khóa ở §8. **Tài liệu này không tuyên bố phương pháp mới.** Đóng góp được định vị ở *thiết kế đo lường có kiểm soát* (xem §5).

---

## 3. Hướng nghiên cứu được chọn và lý do

**Hướng:** *Repository-Level Code Understanding under Limited Context Budget* — đúng hướng tham khảo của yêu cầu, nhưng được **cụ thể hóa** bằng 3 yếu tố rút từ bài học của nhóm:

1. **Dependency gián tiếp** (registry, config key, override, DI, event bus) — để kiểm tra liệu phân tích chương trình *có giá trị thật* khi name-based call graph không đủ (giải quyết R4).
2. **Look-alike distractors** (hàm/lớp trùng tên ở module khác, module legacy không được import, hàm anh em) — trực tiếp trả lời câu hỏi mở của [2] và hiện tượng `tail`→`take`.
3. **Budget cân bằng** (2K/4K/8K/16K + unbounded) — trả lời yêu cầu "equalized budgets" của [3] và tách "model có window lớn" khỏi "phương pháp cung cấp context tốt".

**Vì sao không giữ hướng lost-in-the-middle trên toolz?** Dữ liệu của nhóm đã cho kết quả âm khá chặt (TOST ±5pp đạt). Hướng đó vẫn hợp lệ cho bài báo hiện tại (abstract.md), **benchmark mới là phần mở rộng**, không thay thế. Hai hướng nối với nhau qua RQ2 (H-ret/H-agg ở mức kho).

---

## 4. Câu hỏi nghiên cứu và giả thuyết (đề xuất, chốt trước khi chạy main run)

Ký hiệu: `Acc(s, B, m)` = độ chính xác của chiến lược `s` ở budget `B` với model `m`, trên cùng tập item (paired). Ngưỡng là **đề xuất** — chưa có cơ sở từ dữ liệu; nhóm chốt và commit vào `configs/prereg.yaml` trước main run.

### RQ1 — Chiến lược × Ngân sách
*Dưới cùng giới hạn token đầu vào, chiến lược tổ chức ngữ cảnh ảnh hưởng thế nào đến độ chính xác hiểu kho mã, và ảnh hưởng đó thay đổi thế nào theo budget?*

- **H1a:** Ở `B ∈ {2K, 4K}`, `Acc(DGC) − Acc(BM25) ≥ 10pp` (gộp L3–L5, cả 2 model). Bác bỏ nếu cận trên CI95% paired bootstrap < 3pp.
- **H1b (tương tác):** khoảng cách DGC − FullContext **giảm** khi B tăng đến unbounded (kho vừa window). Kiểm định: hệ số tương tác strategy × log(B) trong mô hình logistic theo item (hoặc so sánh hiệu paired giữa B thấp và B cao).
- Đối chứng: `E0 Oracle` (bằng chứng gold) là cận trên; `E1 No-context` là sàn/kiểm tra rò rỉ.

### RQ2 — Lỗi do *thiếu bằng chứng* hay do *không dùng được bằng chứng* (H-ret/H-agg ở mức kho)
*Phần chênh lệch giữa các chiến lược được giải thích bởi Context Recall (bằng chứng cần thiết có trong context) đến mức nào?*

- **H2a:** Tương quan item-level giữa Context Recall và đúng/sai là dương, và **sau khi điều kiện hóa trên Context Recall = 1**, chênh lệch giữa chiến lược `|Acc(DGC|CR=1) − Acc(BM25|CR=1)| < 5pp` (TOST). Nếu đạt → lợi ích của DGC chủ yếu đến từ *đưa đúng bằng chứng* (retrieval), không từ cách trình bày.
- **H2b:** Ở L4–L5, kể cả với `E0 Oracle`, tỷ lệ sai còn ≥ 15% → tồn tại *use/aggregation failure* độc lập với retrieval.
- Phân loại lỗi tự động: `missing_evidence`, `distractor_confusion` (đáp án khớp với đáp án của look-alike — tính sẵn trong ground truth), `partial_set`, `format_error`, `reasoning_error`.

### RQ3 — Dependency gián tiếp, distractor giống thật và đóng góp từng thành phần
*Khi dependency phải giải qua registry/config/override, name-based retrieval và name-based call graph thất bại đến mức nào? Thành phần nào của DGC đóng góp?*

- **H3a (tương tác):** Bỏ thành phần *dispatch resolution* làm `Acc` giảm ≥ 10pp trên item có nhãn `indirect=True`, và < 3pp trên item `indirect=False`.
- **H3b:** Trên item có look-alike, tỷ lệ `distractor_confusion` của BM25 cao hơn DGC (McNemar trên tập item đó).
- Ablation: `−dispatch`, `−expansion`, `−ranking`, `−skeleton`, `−reverse_edges` (xem §6).

### RQ4 — Hiệu quả chi phí và tính tổng quát qua model (mô tả, không ngưỡng)
*Đánh đổi accuracy – token – latency – cost như thế nào; xếp hạng chiến lược có giữ nguyên giữa Claude và model miễn phí không?*

- Báo cáo: accuracy / 1K input token, Pareto front (accuracy vs tokens), cost per correct answer, Kendall τ giữa xếp hạng chiến lược của 2 model.
- Phân biệt **hiệu ứng model** và **hiệu ứng chiến lược**: so sánh *trong* model (paired) là chính; so sánh *giữa* model chỉ ở mức xếp hạng / tương tác.

---

## 5. Đóng góp dự kiến (định vị thận trọng)

1. **Benchmark cấp kho có ground truth kiểm chứng tự động** (thực thi, dynamic trace, mutation-based impact) với 5 mức độ khó, dependency gián tiếp có nhãn và look-alike có nhãn. *Không phải* LLM sinh đáp án.
2. **Giao thức đo có budget cân bằng** + phân biệt rõ: budget đầu vào, token thực dùng, token đầu ra, context truy xuất vs context cung cấp — đáp ứng trực tiếp yêu cầu "equalized budgets, controlled ablations" của [3].
3. **Phân rã retrieval failure vs use failure ở mức kho** (mở rộng câu hỏi H-ret/H-agg của nhóm từ mức hàm lên mức kho).
4. **DGC** (Dependency-Guided Context) là *baseline có phân tích chương trình được ablation đầy đủ*, **không tuyên bố là kỹ thuật mới** (ý tưởng dùng call graph / slicing để chọn ngữ cảnh đã có: [4], RepoGraph, Trace Gadgets…). Giá trị của nó là công cụ đo: thành phần nào thực sự cần khi dependency gián tiếp.
5. Gói tái lập (config, raw responses, prompt hash, seed, model ID) theo quy trình báo cáo tối thiểu của [3].

Mức bằng chứng theo [3]: **E2** (benchmark có kiểm soát). Không khái quát lên kho mã thực ngoài phạm vi.

---

## 6. Đề xuất thiết kế benchmark (tóm lược — chi tiết ở Phase 2)

### 6.1 Repository fixture
Một kho Python viết tay (không dùng thư viện nổi tiếng để giảm rủi ro ghi nhớ), miền nghiệp vụ giả định ít phổ biến (ví dụ: hệ thống điều phối kho lạnh/logistics), kích thước mục tiêu **~25–35K token** để: 2K–16K đều phải cắt; "unbounded" vừa window của cả 2 model.

Cấu trúc: `config/`, `core/` (interfaces, ABC, DI container, event bus, registry), `domain/` (models, rules có inheritance/override), `storage/` (repository pattern, in-memory DB), `services/`, `api/` (router, handlers), `plugins/` (đăng ký qua decorator + config key), `legacy/` (code chết trùng tên — distractor), `utils/` (hàm dùng chung, hàm anh em dễ nhầm).

### 6.2 Năm mức độ khó
| Mức | Mô tả | Ví dụ dạng câu hỏi | Ground truth |
|---|---|---|---|
| L1 | Một file | Giá trị hằng số / kết quả hàm thuần trong 1 file | Thực thi / AST |
| L2 | Nhiều file, quan hệ trực tiếp | Hàm X dùng lớp nào từ module khác; giá trị qua 2 hàm | Thực thi / AST |
| L3 | Cross-module, gián tiếp | Với cấu hình mặc định, plugin/strategy nào thực sự chạy cho "kind=Y" | Thực thi + trace |
| L4 | Data/control flow | Payload P gửi vào route R → giá trị lưu xuống storage là bao nhiêu; chuỗi hàm được gọi | Thực thi + dynamic trace |
| L5 | Impact analysis | Nếu đổi hành vi hàm `Z` thì route nào cho kết quả khác | **Mutation + chạy lại toàn bộ scenario** |

Đáp án dạng có cấu trúc (JSON: `answer` + `evidence[]` file:line) → chấm tự động bằng exact match / set-F1 / evidence accuracy. Câu hỏi **không nêu tên hàm then chốt**.

### 6.3 Điều kiện thực nghiệm
| Mã | Chiến lược | Mô tả |
|---|---|---|
| E0 | Oracle | Đoạn code gold-evidence (cận trên) |
| E1 | No context | Chỉ câu hỏi |
| E2 | Full context | Toàn bộ kho, thứ tự cố định, cắt theo budget |
| E3 | Fixed context | Cùng một tập file "lõi" cho mọi câu hỏi, cắt theo budget |
| E4 | Retrieval (BM25) | BM25 trên chunk mức hàm/lớp, lấy top đến khi đầy budget |
| E4b | BM25 + name call graph | Thêm callee theo tên (≈ C3 của pilot) — baseline phân tích tĩnh "ngây thơ" |
| E5 | **DGC** | seed (định danh + BM25) → program graph (import, call, class hierarchy, registry/config/DI/event dispatch) → mở rộng theo hướng câu hỏi (callee/caller) → xếp hạng theo khoảng cách đồ thị → đóng gói theo budget (code đầy đủ cho top, *skeleton* chữ ký cho phần còn lại), kèm số dòng |
| A1–A5 | Ablation của E5 | −dispatch, −expansion, −ranking, −skeleton, −reverse_edges |

Budget: 2K, 4K, 8K, 16K, unbounded. Cùng prompt template, T=0, cùng tập item.

### 6.4 Model
- **Claude (chính):** qua adapter `claude_cli` (Claude Code headless `claude -p`, dùng subscription có sẵn, trả về usage/cost/model ID) **hoặc** `anthropic` API nếu có key.
- **Model đối chứng miễn phí:** adapter OpenAI-compatible (Google Gemini free tier qua endpoint OpenAI-compatible, Groq, OpenRouter `:free`, hoặc FPT Cloud nhóm đã dùng). Quota **không được giả định**; adapter xử lý 429/quota và ghi nhận.
- **Mock (offline):** để chạy thử, test pipeline và *kiểm tra phân tích thống kê tìm lại được hiệu ứng cài sẵn* (giống `bundle.py mock` của nhóm).

### 6.5 Metrics
Accuracy/EM; Precision/Recall/F1 (đáp án tập); Evidence Accuracy (file + dòng, có dung sai); Context Recall & Precision (gold evidence units nằm trong context đã cung cấp); token (budget / estimate / provider-reported input / output); latency; cost per task & per correct; success rate (gọi API thành công + parse được).

### 6.6 Thống kê
Paired bootstrap theo item (10.000 lần) cho hiệu chiến lược; McNemar exact; Holm trên tập so sánh chính đăng ký trước; TOST cho các khẳng định "tương đương"; lặp 2–3 lần trên tập con để đo flip-rate; phân tích theo level và theo nhãn `indirect` / `lookalike`.

---

## 7. Rủi ro chính và phương án

| Rủi ro | Phương án |
|---|---|
| R-ceiling: Claude đúng gần hết ở mọi điều kiện (như toolz) | Calibration pilot: loại item đúng ở E1; tăng tỷ lệ L4–L5; budget thấp (2K/4K) là nơi kỳ vọng có chênh lệch |
| R-floor: model free quá yếu | Báo cáo sàn; dùng chủ yếu cho phân tích xếp hạng (RQ4) |
| R-circular: DGC được "thiết kế cho benchmark" (người viết kho = người viết phương pháp) | Đóng băng DGC trước khi viết câu hỏi test; tách dev/test split; công bố rõ là threat; có E4b như baseline phân tích tĩnh đơn giản |
| R-quota: Claude subscription / free tier hết quota | Resume theo job key; shard; giới hạn concurrency; budget-aware scheduler |
| R-tokenizer: không có tokenizer chính xác cho từng model | Ước lượng ký tự→token + hiệu chỉnh hậu kiểm bằng usage thật; báo cáo cả hai |
| R-novelty | Không tuyên bố kỹ thuật mới; tra cứu bổ sung trước khi viết |

---

## 8. Việc cần làm tiếp để củng cố tính mới
Từ khóa tra cứu (arXiv, Semantic Scholar, Google Scholar): *repository-level code understanding benchmark; repository QA LLM; context budget code retrieval; dependency-aware context code LLM; change impact analysis LLM benchmark; indirect call dispatch LLM; semantically similar distractors code LLM; RepoQA; CodeRAG-Bench; Long Code Arena*. Kết quả ghi vào `docs/related_work_check.md`.

---

## 9. Quyết định cần nhóm xác nhận trước Phase 3
1. Đồng ý hướng *budget × chiến lược × dependency gián tiếp* (benchmark mở rộng, song song với bài lost-in-the-middle)?
2. Claude qua `claude -p` (subscription) hay Anthropic API key?
3. Provider miễn phí nào nhóm có key (đề xuất Gemini free tier vì TPM cao, đủ cho prompt ~30K token)?
4. Các ngưỡng 10pp / 3pp / 5pp / 15pp ở §4.
