# Phase 4 – Validation & Pilot Experiment Report

**ccbench v1 · dataset v1 (64 item, SHA `5e550060fea81413`) · fixture `8da947b42b62564d` · prompt p1 · scorer s2 · 13/11/2026**

> **Mọi con số trong tài liệu này đến từ lần chạy thật** với `claude-haiku-5-5` và `claude-sonnet-5-5` qua `claude -p` (Claude Code CLI 2.1.323, đã tắt toàn bộ tool). Số liệu được tính lại từ raw response bằng `python3 -m ccbench report …`. Phần nào **chưa chạy** hoặc là **thăm dò (post hoc)** đều được ghi nhãn rõ. Kết quả mock (SIMULATED) chỉ dùng để test pipeline và không xuất hiện ở đây.
>
> Thư mục kết quả: `results/main_haiku-20261113-184053`, `results/main_sonnet-20261113-184443`, `results/oracle_trace_{haiku,sonnet}-*`, `results/repeat_haiku-20261113-201949`, phân tích gộp `results/combined_v1-20261113/report/` (`report.md`, `summary.csv`, `exploratory.json`, SVG).

---

## 1. Đã chạy những gì

| Run | Model (ID thật do provider trả về) | Job | OK | Lỗi còn lại | Input tok | Output tok | Cost (giá niêm yết*) | Thời gian |
|---|---|---|---|---|---|---|---|---|
| main_haiku | claude-haiku-5-5 | 2.112 | 2.112 | 0 | 16,5M | 1,6M | 3,90 $ | 18:40–20:18 |
| main_sonnet | claude-sonnet-5-5 | 2.112 | 2.112 | 0 (68 lỗi quota đã chạy lại) | 16,4M | 0,9M | 70,26 $ | 18:44–20:57 + resume |
| oracle_trace (thăm dò) | haiku / sonnet | 64 + 64 | 128 | 0 | 0,7M | 0,1M | 1,84 $ | |
| repeat_haiku (3 lần × E4/E5 @4K) | claude-haiku-5-5 | 384 | 384 | 0 (102 lỗi quota đã chạy lại) | 2,0M | 0,3M | 0,21 $ | |
| LLM-judge | claude-sonnet-5-5 chấm Haiku | 40 | 30 hợp lệ | 10 bị quota cắt | | | | |

\* `total_cost_usd` do Claude CLI báo, là **giá niêm yết tương đương**. Với gói subscription thì không bị trừ tiền thật, nhưng quota 5 giờ bị tiêu hết. Lần chạm *"You've hit your 5-hour limit"* lúc 20:30 đã sinh lỗi, và các job đó được resume sau khi quota reset.

**Chưa chạy:** model 7B coder miễn phí. Adapter `openai_compat` cùng `configs/free_qwen7b.json` đã sẵn sàng, nhưng máy chưa có API key free-tier nào. Vì vậy mọi kết luận "giữa model" dưới đây chỉ là **Haiku vs Sonnet, cùng họ Claude**.

Tham số model: CLI **không** cho đặt temperature hoặc seed, nên chúng được ghi `unsupported` trong `config.json`. Model chạy với thinking thích ứng mặc định; số thinking token được lưu ở `provider_extra`.

---

## 2. Kiểm định ground truth và hạ tầng

| Kiểm tra | Kết quả |
|---|---|
| Oracle chạy được, không lỗi | 64/64 |
| Unit gold dạng hàm/method thực sự được thực thi (dynamic trace) | 64/64 item có trace đều đạt |
| `build-dataset --check` tái tạo đúng SHA | Đạt (cũng là integration test) |
| Đột biến trong bộ nhớ được undo sạch | Đạt (có assert sau mỗi đột biến) |
| Unit test + integration test | 26/26 đạt |
| Context không vượt budget (test) | Đạt ở mọi strategy × {2K, 4K, 8K} |

**Lỗi do validation bắt được trong lúc thiết kế** (minh chứng cho giá trị của ground truth thực thi):
1. L5-10: tôi kỳ vọng đột biến `notify_booking` *không* làm đổi response nào. Thực thi cho thấy **S8 đổi**, vì `GET /reports/revenue` trả về số tin nhắn outbox theo kênh. Tôi đã sửa phần giải thích; đáp án luôn lấy từ thực thi.
2. L5-16 (phiên bản đầu, đột biến +0,01): S2 *không* đổi, vì giảm giá 10% làm tròn đã "nuốt" 1 cent. Tôi đổi mọi đột biến L5 sang **+1** để câu hỏi đo phân tích phụ thuộc thay vì đo sự trùng hợp số học.
3. L2-05/L4-09: đáp án look-alike (Dijkstra) trùng đáp án đúng (Greedy) ở tuyến HAN→HCM, nên tôi đổi sang HPH→LCU, nơi hai thuật toán khác nhau.

**Smoke run hiệu chỉnh** (12 lời gọi Haiku, trước main run) chỉ dùng để đo tỷ lệ token. Với 3,2 ký tự/token thì slope = 1,354, intercept = 478, nên tôi đổi sang 2,35 ký tự/token. Thư mục smoke đã bị xoá (sai sót quy trình: lẽ ra phải giữ); hệ số đã ghi trong `ccbench/tokens.py`.

**Hiệu chỉnh token:** với 2,35 ký tự/token, `input_tokens ≈ 561 + 0,957 × prompt_est_tokens` (Haiku, n = 2.112). Nghĩa là budget xấp xỉ token thật, và intercept khoảng 560 là overhead cố định của harness Claude Code. Repo đầy đủ tốn 26,3K token thật.

**Kiểm tra bộ chấm (audit tự động + thủ công bởi Claude, chưa có người duyệt):** rà toàn bộ câu sai của Haiku. 472 câu là `null` ("cannot be determined" khi thiếu bằng chứng), phần còn lại sai thật về giá trị. Phát hiện **10 record** có JSON gần hợp lệ (dấu nháy chưa escape trong `explanation`) bị chấm sai do parse. Tôi thêm cơ chế phục hồi trường `answer`/`evidence` (scorer **s2**) và chấm lại **từ raw response**; file gốc không bị sửa. Đây là thay đổi bộ chấm **sau khi thấy dữ liệu**, ảnh hưởng đúng 10/2.112 record của Haiku. `manual_audit_sample.csv` (40 record phân tầng) có cột `human_verdict` dành cho nhóm điền.

**LLM-as-a-Judge** (Sonnet chấm explanation của Haiku, rubric 0–2): Cohen's κ = **0,67** so với chấm rule-based (n = 30 hợp lệ). Điểm trung bình là 1,74 khi đúng và 0,27 khi sai, không có ca "đúng → 0" hay "sai → 2". Judge chỉ dùng làm chỉ số phụ.

**Độ ổn định (repeat_haiku):** flip-rate **5,5 %** (128 ô item × điều kiện, 3 lần). SD accuracy giữa các lần lặp là 2,3pp (DGC@4K) và 2,5pp (BM25@4K). Mức này tương đương 6,3 % mà nhóm đo được trên toolz.

---

## 3. Kết quả chính

### 3.1 Accuracy (%) theo chiến lược × budget, 64 item, 1 lần chạy [Wilson 95% CI]

| Chiến lược | Haiku 2K | 4K | 8K | 16K | Sonnet 2K | 4K | 8K | 16K |
|---|---|---|---|---|---|---|---|---|
| E2 Full (cắt) | 7,8 | 14,1 | 21,9 | 43,8 | 18,8 | 23,4 | 34,4 | 48,4 |
| E3 Fixed | 6,2 | 10,9 | 23,4 | 21,9 | 23,4 | 26,6 | 39,1 | 37,5 |
| E4 BM25 | 42,2 | 56,2 | **71,9** | **81,2** | 56,2 | **70,3** | **79,7** | **87,5** |
| E4b BM25+name graph | 35,9 | 53,1 | 70,3 | 79,7 | 53,1 | 60,9 | 79,7 | 85,9 |
| E5 DGC | **51,6** | **57,8** | 65,6 | 75,0 | **57,8** | 62,5 | 70,3 | 81,2 |
| A2 DGC − expansion | – | 65,6 | 71,9 | – | – | 73,4 | 81,2 | – |

| Mốc tham chiếu (không giới hạn budget) | Haiku | Sonnet | Input tokens TB |
|---|---|---|---|
| E1 No context | 10,9 [5,4; 20,9] | 15,6 [8,7; 26,4] | ≈ 1,3K |
| E0 Oracle (gold viết tay) | 79,7 [68,3; 87,7] | 84,4 [73,6; 91,3] | ≈ 2,2K |
| E0′ Trace oracle (thăm dò) | 95,3 | 96,9 [89,3; 99,1] | ≈ 5,7K |
| E2 Full – **cả repo** | 98,4 [91,7; 99,7] | **100** [94,3; 100] | ≈ 26,3K |

Theo level (Haiku, 4K): L1 100 / L2 90 / **L3 31–38 / L4 0–8** / L5 50–69 với BM25 và DGC. L4 (data flow nhiều tầng) là khó nhất dưới budget: mọi chiến lược chọn lọc đều ≤ 17 % ở ≤ 8K (Haiku), trong khi cả repo đạt 100 %.

Biểu đồ: `results/combined_v1-20261113/report/accuracy_vs_budget_*.svg`, `accuracy_vs_budget_L3-L5_*.svg`, `accuracy_by_level_4K_*.svg`, `ablation_*.svg`, `accuracy_vs_tokens_*.svg`.

### 3.2 Giả thuyết đăng ký trước (`configs/prereg.json`, Holm trên họ 6 phép thử mỗi model)

| | Haiku | Sonnet |
|---|---|---|
| **H1a** DGC − BM25 ≥ 10pp @2K, L3–L5 | +14,6pp, CI [+2,4; +26,8], p = 0,04, **Holm p = 0,20** → *chỉ đạt khi chưa hiệu chỉnh* | −2,4pp [−17,1; +12,2] → không kết luận |
| **H1a** @4K | +2,4pp [−14,6; +17,1] → không kết luận | −9,8pp [−26,8; +7,3] → không kết luận |
| **H1b** khoảng cách DGC − Full giảm khi budget tăng | +43,8pp @2K → −21,9pp @16K/cả repo; Δ = 65,6pp [53,1; 78,1], Holm p < 0,001 → **ủng hộ** | +39,1 → −18,8; Δ = 57,8pp [45,3; 70,3] → **ủng hộ** |
| **H2a** acc(DGC│CR=1) ≈ acc(BM25│CR=1) (±5pp) | 93,6 vs 96,0; CI90 [−7,0; +2,1] → *không tương đương* (sát biên) | 94,3 vs 99,0 → *không tương đương* |
| **H2b** oracle sai ≥ 15 % ở L4–L5 | 39 % → "ủng hộ" **nhưng là artefact** (§4.2): với trace oracle chỉ còn **7,1 %** [2,0; 22,6] → **bác bỏ** | 32 % → artefact; trace oracle 7,1 % → **bác bỏ** |
| **H3a** bỏ dispatch làm giảm ≥ 10pp trên item gián tiếp | Δ = 0,0pp @4K → **bác bỏ**; @8K 0,0pp | −2,5pp → không kết luận |
| **H3b** BM25 nhầm look-alike nhiều hơn DGC | 3 vs 0 ca, p = 0,25 → không kết luận | 0 vs 1 → không kết luận |

### 3.3 Phép so sánh thăm dò (không đăng ký trước, không hiệu chỉnh) – `exploratory.json`

| So sánh (paired, 64 item) | Haiku | Sonnet |
|---|---|---|
| BM25 − Full cắt, cùng budget (2K…16K) | +34 … +50pp, mọi CI > +21pp, McNemar p < 10⁻⁴ | +38 … +47pp, tương tự |
| Cả repo (26K) − BM25@16K | +17,2pp [7,8; 26,6] | +12,5pp [4,7; 20,3] |
| DGC − DGC không ranking (A3) @4K | +39,1pp [25,0; 53,1] | +28,1pp [14,1; 42,2] |
| DGC không expansion (A2) − DGC @4K | +7,8pp [−1,6; 17,2] | +10,9pp [1,6; 20,3] |
| A2 − BM25 @4K | +9,4pp [−1,6; 20,3] | +3,1pp [−4,7; 10,9] |
| Xếp hạng chiến lược giữa 2 model | Kendall τ = **0,95** (34 ô) | |

---

## 4. Diễn giải

### 4.1 Phát hiện vững (lớn, có ý nghĩa ở cả hai model)
1. **Cách tổ chức context quyết định kết quả nhiều hơn số token.** Ở cùng budget, chọn theo truy xuất (BM25/DGC) hơn cắt prefix (Full/Fixed) từ 34 đến 50pp ở mọi budget, với cả hai model. Fixed context gần như vô dụng (≤ 39 %) dù chứa các file "kiến trúc".
2. **Cửa sổ lớn chứa trọn repo thắng mọi chiến lược chọn lọc ≤ 16K** (98–100 % so với 75–88 %). Tuy nhiên, ở 2K–4K, chọn lọc tốt giữ được khoảng 50–70 % accuracy với 1/8–1/5 lượng token và chi phí. Ví dụ Sonnet BM25@4K đạt 70 % với 0,025 $/task, so với cả repo đạt 100 % với 0,108 $/task. Đây là đánh đổi cụ thể mà yêu cầu RQ4 đặt ra; H1b ủng hộ mạnh.
3. **Accuracy gần như được quyết định bởi việc bằng chứng có nằm trong context hay không.** Khi đủ bằng chứng gold (CR = 1): 94–99 %. Khi thiếu: 25–57 %. Lỗi chủ yếu là `missing_evidence` (Haiku BM25: 86/256; Sonnet: 66/256), còn `distractor_confusion` hiếm (1–5 mỗi ô chiến lược, tổng 15 ca trên BM25/DGC, xem §5). Phát hiện này nối với câu hỏi H-ret/H-agg của nhóm: ở mức repository và với model 2026, **thất bại chủ yếu đến từ khâu truy xuất bằng chứng (H-ret), không phải khâu ghép nối (H-agg)**.
4. **Model trả lời "không xác định được" thay vì đoán** khi thiếu bằng chứng (472 câu `null` ở Haiku). No-context chỉ đạt 11–16 %, nên rủi ro rò rỉ hoặc ghi nhớ fixture thấp.

### 4.2 Phát hiện về độ hợp lệ của chính benchmark
- **Unit gold viết tay là cần nhưng chưa đủ** cho L4. Với oracle gold, Haiku L4 chỉ 4/12 và trả lời `null`. Với trace oracle (gold ∪ unit thực thi ∪ header module), L4 đạt **12/12** ở cả hai model.
  - Hệ quả 1: kết quả H2b "ủng hộ" là artefact. Sau hiệu chỉnh, tỷ lệ "use failure" thật chỉ là 7 %, nên **bác bỏ H2b**.
  - Hệ quả 2: chỉ số context recall theo gold viết tay **lạc quan quá mức**. Đã thêm `context_recall_trace` (thăm dò): BM25@4K là 0,43 (thay vì 0,60), DGC@4K là 0,60 (thay vì 0,75).
  - Đề xuất cho dataset v2: định nghĩa gold evidence = unit thực thi ∪ bằng chứng tĩnh, rồi đóng băng lại.
- E0 không phải cận trên. **E0′ (trace oracle) là cận trên thực tế** với chi phí khoảng 5,7K token (96–97 %).

### 4.3 Về phương pháp đề xuất DGC – kết luận trung thực
- DGC **không** vượt BM25 một cách có ý nghĩa thống kê sau hiệu chỉnh. Lợi thế chỉ thấy ở **Haiku @2K** (+14,6pp trên L3–L5, +9,4pp trên toàn bộ), và mất đi khi đã hiệu chỉnh Holm. Với Sonnet thì không có lợi thế. Ở ≥ 8K, BM25 còn nhỉnh hơn (không có ý nghĩa thống kê).
- Ablation cho thấy **thành phần lan truyền trên đồ thị (expansion, dispatch) không giúp, thậm chí hại**. A2 (chỉ seed neo vào route/topic/config/định danh, rồi BM25) tốt hơn DGC đầy đủ ở cả hai model (+7,8 / +10,9pp @4K), và tốt ngang hoặc hơn BM25. **Ranking là thành phần thiết yếu duy nhất** (bỏ đi mất 28–39pp).
- DGC đưa nhiều bằng chứng hơn BM25 ở mọi budget (CR_trace 0,69 so với 0,57 @8K), và evidence precision/recall của câu trả lời cao hơn (Haiku @4K: P 0,77 / R 0,61 so với 0,71 / 0,51). Vậy mà accuracy không cao hơn. Giả thuyết cần kiểm tra: DGC kéo vào nhiều unit liên quan *một phần* (duck-call, registry "other", skeleton), làm loãng context. Đây là quan sát **thăm dò**.
- Ở fixture này, dispatch gián tiếp **không** làm name-based retrieval thất bại như kỳ vọng (H3a bị bác bỏ). Một lý do là các câu hỏi chứa đủ từ khóa (route, `remote`, `express`…) để BM25 tìm thẳng tới implementation. Đây đúng là bài học "truy hồi quá dễ" mà nhóm đã gặp với toolz.

**Không được điều chỉnh DGC rồi chạy lại trên cùng 64 item** để "làm đẹp" kết quả (overfitting test set, HARKing). Muốn kiểm định biến thể "anchored seeding + ranking" (A2) như một phương pháp, cần: (i) đăng ký trước A2 là phương pháp chính; (ii) một **tập item mới** (dataset v2, held-out) hoặc một fixture thứ hai; (iii) chạy lại.

### 4.4 Đóng góp có thể tuyên bố (mức bằng chứng E2 theo [3])
1. Benchmark repo-level với ground truth thực thi/trace/mutation, 5 level và nhãn indirect/look-alike, cùng giao thức budget cân bằng. Chạy trên 2 model với 4.224 lời gọi, tái lập được.
2. Bằng chứng định lượng: **tổ chức context > lượng context**; với model Claude 2026 trên repo ~26K token, thất bại chủ yếu là **thiếu bằng chứng (H-ret)**; có đánh đổi accuracy–token–cost cụ thể.
3. Kết quả âm tính có giá trị: lan truyền call graph + dispatch **không** cải thiện so với retrieval từ vựng có neo. Điều này phản biện giả định ngầm trong các hệ thống kiểu [4] (vốn không có ablation hay baseline BM25).
4. Bài học về phương pháp đo: gold evidence viết tay làm sai lệch cả oracle lẫn context recall. Trace-based evidence khắc phục được.

**Không** tuyên bố DGC là phương pháp mới hoặc vượt trội.

---

## 5. Phân tích thất bại (ví dụ)
- **L5-06** (đột biến `RemoteAreaRule.amount`, đáp án đúng `[]` vì `PartnerRemoteRule` override): BM25@4K của Haiku trả `[S1, S2, S4, S6, S8]`. Context thiếu `plugins/island.py` (CR = 0,25), model tự giả định rule gốc được dùng. DGC đúng.
- **L4-01/L4-06** (tổng tiền qua chuỗi 10+ hàm): ở ≤ 8K, mọi chiến lược thiếu ít nhất một mắt xích (strategy, rule hoặc tax), nên model trả `null`. Khi có cả repo hoặc trace oracle thì đúng.
- **L2-02** (`flat` 3 kg → 12.50 do min charge): một số context có `FlatStrategy.price` nhưng thiếu `DEFAULTS["pricing.min_charge"]`, nên model trả 7.20 (= 3 × 2.40).
- **Look-alike** (15 ca trên BM25/DGC của cả hai model, tất cả ở L2–L3; không ca nào nhầm giữa ba hàm `calculate_fee`):
  - L3-03/L3-04 trả `9.00` / `RemoteAreaRule`, tức rule gốc thay vì plugin `PartnerRemoteRule` đã ghi đè bằng `replace=True`. Haiku có 4 ca BM25 và 2 ca DGC.
  - L3-05 trả `26.00`, tức giá tiered thay vì strategy `distance` của profile express. Haiku DGC có 3 ca.
  - L3-01 trả `10.00`, tức `CentralTax` thay vì `ExemptTax` cho khách gov. Sonnet DGC có 3 ca.
  - L3-12 trả `0.08` (thuế north mặc định thay vì region của khách). L2-02 trả `7.20` (bỏ qua min charge).

  Như vậy nhầm lẫn tập trung ở **cơ chế dispatch theo cấu hình / ghi đè**, không ở hàm trùng tên. DGC nhầm ở L3-01/L3-05 dù context có chứa cả hai lớp (look-alike lẫn đúng), nên đây là lỗi *sử dụng* bằng chứng.

---

## 6. Mối đe dọa đối với tính hợp lệ

| Loại | Mối đe dọa | Mức độ / giảm nhẹ |
|---|---|---|
| Nội tại | Người viết fixture cũng là người viết DGC và câu hỏi (thiên lệch thiết kế) | DGC đóng băng trước khi chạy; kết quả lại *bất lợi* cho DGC, nên thiên lệch không theo hướng có lợi. Vẫn cần item do người khác viết |
| Nội tại | Gold evidence viết tay chưa đủ | Đã phát hiện và định lượng (§4.2); v2 dùng trace |
| Nội tại | Thay đổi bộ chấm sau khi thấy dữ liệu (s1 → s2) | Ảnh hưởng 10 record; chấm lại từ raw; ghi version |
| Nội tại | Điều kiện E0′ và chỉ số CR_trace là post hoc | Ghi nhãn thăm dò |
| Cấu trúc | Câu hỏi dạng giá trị/tập chỉ là proxy của "hiểu repo" | Có evidence accuracy, judge explanation (κ = 0,67) |
| Cấu trúc | Câu hỏi chứa từ khóa giúp BM25 ("truy hồi dễ") | Cần thêm câu hỏi diễn đạt gián tiếp (paraphrase, không nêu route) ở v2 |
| Kết luận | n = 64 item; CI rộng (±10–12pp); 1 lần chạy mỗi ô | Paired bootstrap, McNemar, Holm; flip-rate 5,5 % (sai số lặp cỡ 2–3pp) |
| Kết luận | Không đặt được temperature/seed qua CLI; thinking thích ứng | Ghi `unsupported`; đo flip-rate |
| Ngoại suy | 1 fixture Python ~26K token, 2 model cùng họ Claude, chưa có model 7B | Chỉ tuyên bố ở mức E2; cần model khác họ và repo thứ hai |
| Ngoại suy | Ước lượng token theo ký tự | Hiệu chỉnh: slope 0,96 so với usage thật |
| Tái lập | Model thương mại thay đổi theo thời gian | Lưu model ID, ngày, prompt SHA, raw response |

---

## 7. Tài nguyên
- Chỉ chạy orchestration trên máy local: không GPU, không tải model, không cài pip.
- Mỗi run tạo một thư mục tạm dùng làm cwd cho `claude -p` và tự xoá. Hai thư mục rỗng sót lại do `pkill` đã được xoá, và đã thêm handler SIGTERM.
- `results/` khoảng 49 MB (chủ yếu raw response; thư mục `combined_v1` chứa bản sao gộp khoảng 20 MB, có thể xoá bằng `python3 -m ccbench clean --results combined_v1-20261113`). Record không chứa source code.
- Wall-clock: khoảng 0,36 job/s (Haiku) và 0,2 job/s (Sonnet) với 4–6 worker. Hai run chính chạy song song mất khoảng 2,5 giờ, cộng resume sau khi quota reset.

---

## 8. Bước tiếp theo đề xuất
1. **Thêm model khác họ**: điền key free-tier (OpenRouter/Groq/Gemini) vào `.env` rồi chạy `python3 -m ccbench run configs/free_qwen7b.json`. Model 7B nhiều khả năng ít trả `null` và đoán nhiều hơn, nên phân bố lỗi sẽ khác.
2. **Dataset v2 (held-out)**: gold = trace; khoảng 30 câu hỏi diễn đạt gián tiếp (không nêu route hay tên rule); thêm một fixture thứ hai. Đăng ký trước A2 ("anchored seeding + ranking") làm phương pháp đề xuất.
3. Nhóm điền `manual_audit_sample.csv` (người thật) để có độ đồng thuận người–máy.
4. Tăng power: hiện n = 64, MDE paired khoảng 15pp. Muốn phát hiện 10pp cần khoảng 120–150 item.
