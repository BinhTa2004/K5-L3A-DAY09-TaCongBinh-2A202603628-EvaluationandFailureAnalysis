# Lab 9: Evaluation & Failure Analysis — Ta Cong Binh (2A202603628)

Bài cá nhân trên fork Day 9, PR starter/d09 → main trong chính fork.
Dùng src/ nguyên bản Day 8 của giảng viên; giữ code lab8, fixture, test phát sẵn,
variant, trap và workflow. Phần triển khai là eval set/taxonomy, calibration,
trajectory graders, paired bootstrap, slice gate và integrity/ratchet.

## Kết quả kiểm tra

- M0 PASS; eval set v1 14 item và v2 28 item, cả hai 0 problem(s).
- 100 test host/crash + Lab 9 pass; không làm ba shape TODO của bài nhóm Day 8.
- Baseline pass_rate=0.9857; fixed=1.0; seeded_regression=0.7143.
- Detection=100%, false alarms=0%; tone đạt floors, helpful bị loại.
- Mutation 3/3 regression bị chặn, 0 false alarms; A/A mọi Δ=0.
- Có regression test cho bước sai đầu tiên C-002@11, audit 8 bất đồng,
  eval card và PRD v1.1. Baseline/report đều sinh bằng script, không sửa tay.
- Eval-set LF cố định để SHA khớp trên Windows và Linux CI.

## Bằng chứng Core: regression exit 1

```text
python -m lab9.gate --pr reports/eval_seeded_regression.json --baseline reports/baseline_v1.json
gate: PR E-seeded_regression-20261117-d032 vs main E-swarm-20261117-d032 · eval set d032467e000b
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.9286   {"min": 0.95}                                                         warn
  refund_amount_correct  0.8571   {"min": 0.95, "no_significant_drop": true} Δ -0.129 CI [-0.315, +0.000] BLOCK
  pass_rate              0.7143   {"min": 0.85, "no_significant_drop": true} Δ -0.271 CI [-0.500, -0.057] BLOCK
  pass_5                 0.7143   {"min": 0.8}                                                          warn
  cost_per_success       81.202   {"max_increase": 0.1}                                                 warn
  reply_ledger_consistent 0.7857   {"min": 1.0}                                                          BLOCK
  proposal_amount_correct 0.7857   {"min": 0.95}                                                         BLOCK
exit 1 — blocked: refund_amount_correct, pass_rate, reply_ledger_consistent, proposal_amount_correct

PROCESS_EXIT=1
```

## Scorecard v2

```text
python -m lab9.mutation --spec config/metric_spec_v2.yaml --baseline reports/baseline_v2.json
  fixed                expect merge got merge ok
  honest_refactor      expect merge got merge ok
  seeded_regression    expect block got block ok          refund_amount_correct, pass_rate, pass_hat_5, reply_ledger_consistent, proposal_amount_correct, slice:money_movement/pass_rate, slice:adversarial/pass_rate, slice:denial/pass_rate
  slice_regression     expect block got block ok          slice:money_movement/pass_rate
  flaky_regression     expect block got block ok          pass_rate, pass_hat_5, proposal_amount_correct, slice:money_movement/pass_rate
mutation score 3/3 · false alarms 0

PROCESS_EXIT=0
```

## A/A

```text
python -m lab9.mutation --spec config/metric_spec_v2.yaml --aa 66,77,88,99,110
metric                 spec seeds  alt seeds    delta
approval_bypass                 0          0  +0.0000
secret_leak                     0          0  +0.0000
db_fact_kept               0.9786     0.9786  +0.0000
refund_amount_correct      0.9786     0.9786  +0.0000
pass_rate                  0.9786     0.9786  +0.0000
reply_ledger_consistent        1.0        1.0  +0.0000
proposal_amount_correct     0.9786     0.9786  +0.0000
pass_5                     0.8929     0.8929  +0.0000
pass_at_1                  0.9786     0.9786  +0.0000
pass_hat_1                 0.9786     0.9786  +0.0000
pass_at_3                     1.0        1.0  +0.0000
pass_hat_3                 0.9357     0.9357  +0.0000
pass_at_5                     1.0        1.0  +0.0000
pass_hat_5                 0.8929     0.8929  +0.0000
cost_per_success          50.8077    50.8077  +0.0000

PROCESS_EXIT=0
```

## Bốn trap đều exit 1

- `evaluator_errors_as_nan`: `exit 1 — blocked: integrity` (INTEGRITY).
- `dropped_failing_rows`: `exit 1 — blocked: integrity` (INTEGRITY).
- `cherry_picked_seeds`: `exit 1 — blocked: integrity` (INTEGRITY).
- `loosened_spec`: `exit 1 — blocked: integrity` (ratchet: removed slices money_movement).

Chi tiết command/stdout/exit code: [docs/validation.md](docs/validation.md).
Giới hạn MockLLM, ít item/seed, judge replay, thiếu reply event ở baseline và
ratchet cần --base-spec tin cậy được ghi trong [eval card](docs/eval_card.md).
Key anchor/test ẩn thuộc giảng viên, chưa khẳng định kết quả bộ chấm ẩn.

Chủ bài cần đọc xác nhận audit/PRD, bật Actions và kiểm eval-gate + eval-gate-v2
xanh trên PR trước khi nộp link LMS. Hạn theo thông báo lớp: 12:00 trưa 18/11.
