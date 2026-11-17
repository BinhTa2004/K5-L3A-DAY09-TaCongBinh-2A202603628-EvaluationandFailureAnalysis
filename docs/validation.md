# Bằng chứng kiểm tra Lab 9 — 17/11/2026

Code/grader commit: 7f9cec44c94a75baf223d98397f811d37495d486.
Nguồn Day 8: VinUni-AI20k/K5-Day8-From-Workflows-to-Agents,
commit 034c6c421c198dae67a9211d15e2587d5a378972.

- Smoke: M0 PASS; eval set v1/v2: 0 problem(s), 14/28 item.
- 33 Git blob bảo vệ thuộc lab8/, fixture public và config Day 8 giống hệt nguồn.
- Trong 63 file src/ nhập từ Day 8, chỉ harness_map.yaml được thêm section eval.
- Test Lab 9 phát sẵn, variant, trap và workflow không đổi.
- Eval-set LF cố định: v1 d032467e000b, v2 a2c76c165bcd; SHA trên máy trùng Git index.
- Report sinh bằng lab9.eval; trap sinh bằng lab9.traps, không sửa tay reports/.
- Không sửa ba shape TODO Day 8; 248 test student ma trận Day 8 ngoài phạm vi lượt kiểm này.
- Chưa push/mở PR, chưa xác nhận GitHub Actions. Kết quả dưới đây là kết quả local.

Các khối dưới lấy từ stdout/stderr và exit code thực của lệnh chạy trong src/.
Exit 1 của regression/trap là thành công về mặt phát hiện lỗi.

## Host/crash và Lab 9

```text
python -m pytest -q -o addopts= -k lab9 or not student -p no:cacheprovider
........................................................................ [ 72%]
............................                                             [100%]
100 passed, 248 deselected in 8.85s

PROCESS_EXIT=0
```

## Fixed phải được merge

```text
python -m lab9.gate --pr reports/eval_fixed.json --baseline reports/baseline_v1.json
gate: PR E-fixed-20261117-d032 vs main E-swarm-20261117-d032 · eval set d032467e000b
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           1.0      {"min": 0.95}                                                         ok
  refund_amount_correct  1.0      {"min": 0.95, "no_significant_drop": true} Δ +0.014 CI [+0.000, +0.043] ok
  pass_rate              1.0      {"min": 0.85, "no_significant_drop": true} Δ +0.014 CI [+0.000, +0.043] ok
  pass_5                 1.0      {"min": 0.8}                                                          ok
  cost_per_success       48.7157  {"max_increase": 0.1}                                                 ok
  reply_ledger_consistent 1.0      {"min": 1.0}                                                          ok
  proposal_amount_correct 1.0      {"min": 0.95}                                                         ok
exit 0 — merge

PROCESS_EXIT=0
```

## Seeded regression phải bị chặn

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

## Kiểm baseline/spec

```text
python -m lab9.ci_check --pr reports/baseline_v1.json --baseline reports/baseline_v1.json
exit 0 — baseline and spec look sound

PROCESS_EXIT=0
```

## Detection / false alarms

```text
python -m lab9.mutation --detect
detection 100.00% (target >=80%) · false alarms 0.00% (target <=10%)

PROCESS_EXIT=0
```

## A/A trên hai bộ seed

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

## Mutation scorecard

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

## Baseline v1 so với chính nó

```text
python -m lab9.gate --pr reports/baseline_v1.json --baseline reports/baseline_v1.json
gate: PR E-swarm-20261117-d032 vs main E-swarm-20261117-d032 · eval set d032467e000b
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.9857   {"min": 0.95}                                                         ok
  refund_amount_correct  0.9857   {"min": 0.95, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  pass_rate              0.9857   {"min": 0.85, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  pass_5                 0.9286   {"min": 0.8}                                                          ok
  cost_per_success       49.567   {"max_increase": 0.1}                                                 ok
  reply_ledger_consistent 1.0      {"min": 1.0}                                                          ok
  proposal_amount_correct 0.9857   {"min": 0.95}                                                         ok
exit 0 — merge

PROCESS_EXIT=0
```

## Baseline v2 so với chính nó

```text
python -m lab9.gate --pr reports/baseline_v2.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
gate: PR E-swarm-20261117-a2c7 vs main E-swarm-20261117-a2c7 · eval set a2c76c165bcd
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.9786   {"min": 0.95}                                                         ok
  refund_amount_correct  0.9786   {"min": 0.9, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  pass_rate              0.9786   {"min": 0.85, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  pass_hat_5             0.8929   {"min": 0.8}                                                          ok
  cost_per_success       50.8077  {"max_increase": 0.1}                                                 ok
  reply_ledger_consistent 1.0      {"min": 1.0}                                                          ok
  proposal_amount_correct 0.9786   {"min": 0.9, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  slice:money_movement/pass_rate           1.0        Δ +0.000 CI [+0.000, +0.000] ok
  slice:adversarial/pass_rate              0.9714285714285714 Δ +0.000 CI [+0.000, +0.000] ok
  slice:denial/pass_rate                   0.9454545454545454 Δ +0.000 CI [+0.000, +0.000] ok
exit 0 — merge

PROCESS_EXIT=0
```

## Gate slice

```text
python -m lab9.gate --pr reports/eval_slice_regression.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
gate: PR E-slice_regression-20261117-a2c7 vs main E-swarm-20261117-a2c7 · eval set a2c76c165bcd
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           1.0      {"min": 0.95}                                                         ok
  refund_amount_correct  0.9357   {"min": 0.9, "no_significant_drop": true} Δ -0.043 CI [-0.121, +0.029] ok
  pass_rate              0.9357   {"min": 0.85, "no_significant_drop": true} Δ -0.043 CI [-0.121, +0.029] ok
  pass_hat_5             0.8929   {"min": 0.8}                                                          ok
  cost_per_success       52.9053  {"max_increase": 0.1}                                                 ok
  reply_ledger_consistent 1.0      {"min": 1.0}                                                          ok
  proposal_amount_correct 0.9357   {"min": 0.9, "no_significant_drop": true} Δ -0.043 CI [-0.121, +0.029] ok
  slice:money_movement/pass_rate           0.85       Δ -0.150 CI [-0.300, +0.000] BLOCK
  slice:adversarial/pass_rate              0.9142857142857144 Δ -0.057 CI [-0.186, +0.057] ok
  slice:denial/pass_rate                   1.0        Δ +0.055 CI [+0.018, +0.109] ok
exit 1 — blocked: slice:money_movement/pass_rate

PROCESS_EXIT=1
```

## Gate flaky

```text
python -m lab9.gate --pr reports/eval_flaky_regression_v2.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
gate: PR E-flaky_regression-20261117-a2c7 vs main E-swarm-20261117-a2c7 · eval set a2c76c165bcd
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           1.0      {"min": 0.95}                                                         ok
  refund_amount_correct  0.9643   {"min": 0.9, "no_significant_drop": true} Δ -0.014 CI [-0.050, +0.021] ok
  pass_rate              0.9143   {"min": 0.85, "no_significant_drop": true} Δ -0.064 CI [-0.114, -0.014] BLOCK
  pass_hat_5             0.5714   {"min": 0.8}                                                          BLOCK
  cost_per_success       54.1453  {"max_increase": 0.1}                                                 ok
  reply_ledger_consistent 1.0      {"min": 1.0}                                                          ok
  proposal_amount_correct 0.9143   {"min": 0.9, "no_significant_drop": true} Δ -0.064 CI [-0.114, -0.014] BLOCK
  slice:money_movement/pass_rate           0.8666666666666667 Δ -0.133 CI [-0.183, -0.083] BLOCK
  slice:adversarial/pass_rate              0.9285714285714286 Δ -0.043 CI [-0.114, +0.029] ok
  slice:denial/pass_rate                   0.9272727272727272 Δ -0.018 CI [-0.109, +0.073] ok
exit 1 — blocked: pass_rate, pass_hat_5, proposal_amount_correct, slice:money_movement/pass_rate

PROCESS_EXIT=1
```

## Trap: missing grade / NaN

```text
python -m lab9.gate --pr reports/traps/evaluator_errors_as_nan.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
gate: PR E-slice_regression-20261117-a2c7 vs main E-swarm-20261117-a2c7 · eval set a2c76c165bcd
  INTEGRITY PR: missing/invalid row metric refund_amount_correct
  INTEGRITY PR: missing/invalid row metric pass_rate
  INTEGRITY PR: missing/invalid row metric proposal_amount_correct
exit 1 — blocked: integrity

PROCESS_EXIT=1
```

## Trap: bỏ row fail

```text
python -m lab9.gate --pr reports/traps/dropped_failing_rows.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
gate: PR E-slice_regression-20261117-a2c7 vs main E-swarm-20261117-a2c7 · eval set a2c76c165bcd
  INTEGRITY PR: row count differs from items x seeds
  INTEGRITY PR: incomplete item/seed grid
  INTEGRITY PR: non-finite or missing aggregate metric
  INTEGRITY PR: aggregate pass_at_3 disagrees with rows
  INTEGRITY PR: aggregate pass_hat_3 disagrees with rows
  INTEGRITY PR: aggregate pass_at_5 disagrees with rows
  INTEGRITY PR: aggregate pass_hat_5 disagrees with rows
  INTEGRITY PR item/seed set differs from baseline
exit 1 — blocked: integrity

PROCESS_EXIT=1
```

## Trap: chọn seed

```text
python -m lab9.gate --pr reports/traps/cherry_picked_seeds.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
gate: PR E-slice_regression-20261117-a2c7 vs main E-swarm-20261117-a2c7 · eval set a2c76c165bcd
  INTEGRITY PR: seeds differ from spec
  INTEGRITY PR: non-finite or missing aggregate metric
  INTEGRITY PR: aggregate pass_at_3 disagrees with rows
  INTEGRITY PR: aggregate pass_hat_3 disagrees with rows
  INTEGRITY PR: aggregate pass_at_5 disagrees with rows
  INTEGRITY PR: aggregate pass_hat_5 disagrees with rows
  INTEGRITY PR item/seed set differs from baseline
exit 1 — blocked: integrity

PROCESS_EXIT=1
```

## Trap: nới spec

```text
python -m lab9.gate --pr reports/traps/loosened_spec.json --baseline reports/baseline_v2.json --spec reports/traps/loosened_spec.spec.yaml --base-spec config/metric_spec_v2.yaml
gate: PR E-slice_regression-20261117-a2c7 vs main E-swarm-20261117-a2c7 · eval set a2c76c165bcd
  INTEGRITY ratchet: loosened min of db_fact_kept
  INTEGRITY ratchet: loosened min of refund_amount_correct
  INTEGRITY ratchet: removed no_significant_drop from refund_amount_correct
  INTEGRITY ratchet: loosened min of pass_rate
  INTEGRITY ratchet: removed no_significant_drop from pass_rate
  INTEGRITY ratchet: loosened min of pass_hat_5
  INTEGRITY ratchet: loosened min of reply_ledger_consistent
  INTEGRITY ratchet: loosened min of proposal_amount_correct
  INTEGRITY ratchet: removed no_significant_drop from proposal_amount_correct
  INTEGRITY ratchet: removed slices money_movement
  INTEGRITY ratchet: removed slices adversarial
  INTEGRITY ratchet: removed slices denial
exit 1 — blocked: integrity

PROCESS_EXIT=1
```

## Trace lỗi

```text
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
== seeded_regression C-002@11  lab8 grader: FAIL (status resolved != denied)
-- trace (step, kind, payload)
   1 handoff            {"facts": {}, "contract_version": "handoff.v1", "claim_id": "C-002", "task": "check_applicable_policy", "reque
   2 investigator       {"lookup_order": {"visible": true, "reason": "ok", "order": {"order_id": "O-202", "status": "delivered", "dela
   3 model_override     {"delay_days": 5}
   4 quote              {"amount_vnd": 20000, "reason": "entitled", "clause_ids": ["SHIP-LATE-03"], "parts": {"SHIP-LATE-03": 20000}}
   5 refund_history     {"refund_count": 0, "refunded_vnd": 0}
   6 reply              {"text": "Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."}
-- ledger vs label
  refund_vnd     ledger=20000    label=0   <-- differs
  refund_count   ledger=1        label=0   <-- differs
  status         result=resolved label=denied
  unexpected ledger rows: 0

PROCESS_EXIT=0
```

## Trace đối chứng

```text
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11
== fixed C-002@11  lab8 grader: PASS (ok)
-- trace (step, kind, payload)
   1 handoff            {"request_id": "REQ-C-002", "principal_scope": "owner_order_only", "contract_version": "handoff.v1", "allowed_
   2 investigator       {"lookup_order": {"visible": true, "reason": "ok", "order": {"order_id": "O-202", "status": "delivered", "dela
   3 quote              {"amount_vnd": 0, "reason": "no_entitlement", "clause_ids": [], "parts": {}}
   4 reply              {"text": "Dạ, đơn O-202 chưa đủ điều kiện hoàn theo chính sách hiện hành."}
-- ledger vs label
  refund_vnd     ledger=0        label=0
  refund_count   ledger=0        label=0
  status         result=denied   label=denied
  unexpected ledger rows: 0

PROCESS_EXIT=0
```
