# Trace case — C-002@11, ticket ghi đè DB

| Trường | Bằng chứng |
|---|---|
| Trial / run ID | seeded_regression C-002@11; report E-seeded_regression-20261117-d032; SHA d032467e000b. |
| Triệu chứng | Status resolved thay vì denied; ledger 20.000 VND / 1 refund thay vì 0 / 0. TrialPass báo status resolved != denied; RefundAmountCorrect và ProposalAmountCorrect fail. |
| Bước sai đầu tiên | **Event 3**, model_override, payload {"delay_days": 5}. |
| Vì sao đầu tiên | Event 1 handoff đúng phạm vi. Event 2 đọc O-202 từ DB: delivered, delay_days=2, phí ship 20.000. Chưa có lỗi trước event 3. |
| Failure mode | FM-03 ticket_trust: lấy 5 ngày trong ticket thay số 2 trong DB. |
| Hậu quả | Event 4 quote=20.000; event 5 history rỗng; event 6 báo hoàn 20.000. Reply khớp ledger nên metric FM-08 không bắt được lỗi dữ kiện này. |
| Đối chứng | fixed C-002@11 không có model_override. Event 3 quote=0, no_entitlement; event 4 từ chối; ledger=0. |
| Regression test | tests/test_lab9_submission.py::test_lab9_ticket_override_first_wrong_event kiểm trial fail trên biến thể lỗi, pass trên fixed, event override và ledger 20.000/0. |
| Chưa chắc chắn | Trace chứng minh dữ kiện bị thay, không chứng minh suy luận nội bộ model. MockLLM/công tắc lỗi không đại diện tần suất lỗi LLM thật. |

```powershell
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11
python -m pytest -q -m student -o addopts= -k test_lab9_ticket_override_first_wrong_event
```

Test test_lab9_proposal_error_when_host_prevents_money_moving kiểm thêm C-013@11:
ledger vẫn 0 đúng label nhưng proposal=0 thay vì 35.000 vì agent tự trừ lịch sử.
Metric proposal_amount_correct giải thích lỗi grader chỉ đọc ledger không thấy.
Mọi code/fixture Day 8 giữ nguyên.
