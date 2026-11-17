# Judge audit — replay public, 17/11/2026

Positive class là **FAIL**: judge cần tìm lỗi. Số liệu tính bằng lab9.judge.calibrate
trên CSV gốc, không sửa nhãn/verdict.

| Tiêu chí | n | TP / FP / FN / TN | κ | Precision | Recall | Quyết định |
|---|---:|---|---:|---:|---:|---|
| tone_ok | 100 | 24 / 4 / 6 / 66 | 0.757 | 0.857 | 0.800 | Đạt κ≥0.6, P≥0.8, R≥0.7; đủ điều kiện dùng cho tone. |
| helpful | 100 | 9 / 0 / 21 / 70 | 0.375 | 1.000 | 0.300 | Loại khỏi gate: bỏ sót 21/30 lỗi; precision không bù recall thấp. |

Rogan–Gladen: tone observed=0.28, sensitivity=0.8, specificity=66/70, corrected=0.30.
Helpful observed=0.09, sensitivity=0.3, specificity=1, corrected=0.30.
Hiệu chỉnh tỉ lệ cấp tập không biến helpful thành bộ phát hiện từng case đáng tin.
κ không xác định phải FAIL calibration; mẫu số P/R bằng 0 trả 0.

## Audit bất đồng

Phân tích có hỗ trợ AI, đối chiếu nhãn người và ghi chú có sẵn trong CSV; chủ bài cần
đọc xác nhận trước nộp. Đây không phải vòng gán nhãn người mới.

| Case | Judge / người | Kết luận đối chiếu | Sửa rubric đề xuất |
|---|---|---|---|
| H-008 | PASS / FAIL | Nhãn người hợp lý: “em”, “nha”, “anh check” suồng sã theo chuẩn CS của tập. | Tách lịch sự/thân thiện; thêm ví dụ FAIL với đại từ và đuôi câu suồng sã. |
| H-017 | PASS / FAIL | Theo ghi chú, “bạn ơi…nha” không phù hợp đối tượng khách của case. | Nêu chuẩn xưng hô anh/chị; không tự đoán tuổi khi thiếu context. |
| H-029 | PASS / FAIL | “không cần nhắn thêm” mang giọng ra lệnh dù đầu câu có “Dạ”. | Chấm toàn câu; không cho từ lịch sự che phần gây khó chịu. |
| H-042 | FAIL / PASS | Câu ngắn đủ thông tin, có thời gian tiền về và “ạ”. | Không bắt buộc xin lỗi trong mọi thông báo đã hoàn thành. |
| H-051 | FAIL / PASS | “refund” là từ CS được phép theo ghi chú bộ dữ liệu. | Thêm từ nghiệp vụ được phép; không phạt tiếng Anh tự động. |
| H-063 | PASS / FAIL | Hứa “sẽ hoàn thêm” ngoài kết quả hệ thống. | Thêm tiêu chí không hứa vượt quyết định host; kiểm factual riêng. |
| HL-015 | PASS / FAIL | Nói 55.000 trong khi ghi chú ledger là 40.000. | So tiền với ledger bằng code, không chấm theo độ lịch sự. |
| HL-016 | PASS / FAIL | Xin lỗi dài không sửa số 55.000 sai so với ledger 35.000. | Tách helpfulness, tone và amount consistency. |

Các sửa rubric là đề xuất; verdict replay không đổi. Cần held-out có nhãn người mới
để kiểm chứng cải thiện, tránh đo trên chính ví dụ vừa dùng sửa rubric.

```powershell
python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 5
python -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5
```

Helpful exit 1 là mong đợi. Gate dùng code cho tiền/approval. Tone đạt calibration
nhưng chưa được thêm làm điều kiện blocking trong metric spec hiện tại.
