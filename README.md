# ccbench – Repository-Level Code Context Benchmark

[![tests](https://github.com/tuannt2906/code-context-benchmark/actions/workflows/tests.yml/badge.svg)](https://github.com/tuannt2906/code-context-benchmark/actions/workflows/tests.yml) ![python](https://img.shields.io/badge/python-3.9%2B-blue) ![deps](https://img.shields.io/badge/dependencies-stdlib%20only-brightgreen) ![license](https://img.shields.io/badge/license-MIT-lightgrey)

> **English summary.** ccbench measures how well LLMs understand a *whole repository* under a limited input-token budget. A hand-written Python repository (`fixture_repo/frostline`, ~26K tokens, registries, plugin overrides, an event bus, inheritance, look-alike functions) is queried with 64 questions across 5 difficulty levels (single file → cross-module dispatch → data flow → change-impact analysis). **Ground truth is computed by executing the code** (dynamic call traces and in-memory mutation for impact questions), never by an LLM. Context strategies (none, truncated full repo, fixed files, BM25, BM25 + name graph, a dependency-guided strategy and 5 ablations) are compared at 2K/4K/8K/16K tokens. Real runs with Claude Haiku 5.5 and Sonnet 5.5 (4,224 calls) are included in `results/`; see `docs/pilot_experiment_report.md`. Stdlib-only Python, no GPU. License: MIT.
>
> Key findings (E2-level evidence, one synthetic repo): context *organization* matters far more than context *size* (retrieval beats truncation by 34–50 pp at equal budget); most failures are missing evidence rather than failing to use it; the dependency-graph expansion did **not** beat lexical retrieval after multiple-comparison correction (a negative result, reported as such).

Benchmark đánh giá khả năng **hiểu ngữ cảnh code ở cấp repository** của LLM dưới **giới hạn token budget**, so sánh các chiến lược dựng ngữ cảnh (no-context, full, fixed, BM25, BM25 + name graph, Dependency-Guided Context và 5 ablation), với ground truth **tính bằng thực thi code** (không dùng LLM tạo đáp án).

- Python ≥ 3.9, **chỉ thư viện chuẩn** (không pip, không GPU, không tải model).
- Claude chạy qua **Claude Code CLI** (`claude -p`, dùng login sẵn có, tắt toàn bộ tool) – không cần API key.
- Model đối chứng miễn phí: adapter OpenAI-compatible (OpenRouter / Groq / Gemini / HF / Together).

Tài liệu: [`docs/research_design.md`](docs/research_design.md) (Phase 1) · [`docs/benchmark_specification.md`](docs/benchmark_specification.md) (Phase 2) · [`docs/dataset_catalog.md`](docs/dataset_catalog.md) · [`docs/pilot_experiment_report.md`](docs/pilot_experiment_report.md) (Phase 4, kết quả thật).

## Cấu trúc

```
code_context_benchmark/
├── fixture_repo/frostline/   # repository được hỏi (74 file, 278 unit)
├── ccbench/
│   ├── repo/        index.py (AST units) · graph.py (program graph, name graph)
│   ├── context/     bm25.py · packer.py (budget) · strategies.py (E0–E5, A1–A5)
│   ├── dataset/     specs.py (64 câu hỏi) · scenarios.py (S1–S8) · build.py (validate)
│   ├── oracle/      worker.py (thực thi, trace, mutation) · runner.py
│   ├── providers/   claude_cli · anthropic_api · openai_compat · mock
│   ├── eval/        prompt.py · parse.py · scoring.py · judge.py
│   ├── analysis/    stats.py · aggregate.py (hypotheses)
│   ├── report/      report.py (CSV/JSON/SVG/Markdown)
│   ├── runner.py · cli.py
├── configs/         prereg.json + cấu hình thí nghiệm
├── data/            items.v1.jsonl · manifest.v1.json · context_stats.v1.json
├── results/         mỗi run một thư mục <name>-<timestamp>/ (không ghi đè)
├── tests/           unit + integration (unittest)
├── LICENSE          MIT
└── docs/
```

## Cài đặt & kiểm tra nhanh (không cần API)

```bash
cd code_context_benchmark
python3 -m unittest discover -s tests          # 25 test
python3 -m ccbench build-dataset --check       # tái tạo ground truth, so SHA
python3 -m ccbench context-stats               # context recall offline theo strategy × budget
python3 -m ccbench run configs/demo_mock.json  # demo end-to-end bằng mock (SIMULATED)
python3 -m ccbench show-context L3-03 dgc --budget 4000 --prompt   # xem prompt thực tế
```

## Cấu hình model

**Claude (chính)** – chỉ cần đã đăng nhập `claude`:
```bash
python3 -m ccbench run configs/smoke_claude.json   # 12 lời gọi kiểm tra
python3 -m ccbench run configs/main_haiku.json     # 2.112 lời gọi
python3 -m ccbench run configs/main_sonnet.json
```
CLI không hỗ trợ temperature/seed → được ghi `unsupported` trong `config.json`. Nếu có `ANTHROPIC_API_KEY`, đổi `"provider": "anthropic"` để dùng temperature = 0.

**Model miễn phí (đối chứng)**: `cp .env.example .env`, điền key (ví dụ `OPENROUTER_API_KEY`), chỉnh `preset`/`model` trong `configs/free_qwen7b.json`, rồi:
```bash
python3 -m ccbench run configs/free_qwen7b.json
```
Kiểm tra model ID còn tồn tại và còn miễn phí trên trang của nhà cung cấp trước khi chạy (danh sách model free thay đổi thường xuyên). Quota không được giả định: HTTP 429/quota → dừng model đó, chạy lại bằng `resume`.

## Chạy, resume, tổng hợp

```bash
python3 -m ccbench resume results/main_haiku-YYYYMMDD-HHMMSS     # bỏ qua job đã xong
python3 -m ccbench report results/<exp>                          # CSV/JSON/SVG/report.md
python3 -m ccbench combine results/combined_all results/<exp1> results/<exp2>
python3 -m ccbench rescore results/<exp>                         # chấm lại từ raw response
python3 -m ccbench judge results/<exp> --judge-model sonnet --n 40   # LLM-as-judge (judge ≠ model được chấm)
python3 -m ccbench run results/<exp>/config.json                 # chạy lại từ cấu hình đã lưu (experiment mới)
python3 -m ccbench clean                                          # xoá __pycache__
```

## Dữ liệu kết quả được công bố

`results/` chứa raw response, cấu hình và report của các run thật (`main_haiku`, `main_sonnet`, `oracle_trace_*`, `repeat_haiku`). Không công bố: file `*.log` (chứa đường dẫn máy cục bộ), `.env`, và `results/combined_*/results.jsonl` (bản sao gộp, tạo lại bằng `python3 -m ccbench combine ...`).

## Đọc kết quả

`results/<exp>/report/`:
- `report.md` – bảng accuracy [95% CI] theo model × strategy × budget, theo level, context recall, evidence P/R, token (ước lượng / thật / output), latency, cost; kết quả giả thuyết đăng ký trước (verdict + CI + p Holm); flip-rate; hiệu chỉnh token.
- `summary.csv`, `summary.json` – số liệu máy đọc.
- `accuracy_vs_budget_*.svg`, `accuracy_by_level_*.svg`, `ablation_*.svg`, `accuracy_vs_tokens_*.svg`.
- `manual_audit_sample.csv` – mẫu 40 bản ghi để người kiểm tra (cột `human_verdict`).

Run có provider `mock` được đánh dấu **SIMULATED** – không phải kết quả thực nghiệm.

## Thêm model / chiến lược / câu hỏi

- Model: thêm adapter vào `ccbench/providers/` và đăng ký trong `PROVIDERS`.
- Chiến lược: thêm nhánh trong `ContextBuilder.build`.
- Câu hỏi: thêm `item(...)` vào `ccbench/dataset/specs.py` với đoạn `oracle`; chạy `build-dataset` (validate tự động). Đổi `DATASET_VERSION` khi thay đổi dataset đã dùng cho kết quả.
