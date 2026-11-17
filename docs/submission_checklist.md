# Checklist nộp Lab 9 cá nhân

Repo: BinhTa2004/K5-L3A-DAY09-TaCongBinh-2A202603628-EvaluationandFailureAnalysis.
Nhánh bài làm: starter/d09; base PR: main trong chính fork cá nhân.
Theo ảnh thông báo lớp: hạn **12:00 trưa 18/11**; không theo hướng dẫn nhóm/23:59
còn lưu trong README và SUBMISSION gốc.

## Phần đã chuẩn bị

- Core M0–M4 và Advanced/Expert M5–M7; eval set v1/v2, report sinh bằng script.
- Tài liệu taxonomy, trace case + regression test, judge audit, eval card, PRD v1.1.
- Section eval trong harness_map; giữ nguyên code src/lab8 và fixture Day 8.
- .gitignore giữ bí mật/runtime output; .gitattributes chỉ cố định LF của eval set
  để SHA trùng Windows/Linux CI. Workflow gốc không đổi.
- Bằng chứng kiểm tra: [validation.md](validation.md).
- Nội dung mô tả PR để copy: [PR_DESCRIPTION.md](PR_DESCRIPTION.md).

## Những việc cần chủ bài can thiệp

1. Đọc và xác nhận [judge_audit.md](judge_audit.md), [eval_card.md](eval_card.md),
   [PRD_v1.1.md](PRD_v1.1.md). Audit là phân tích hỗ trợ AI dựa trên nhãn người được
   phát sẵn; không mạo nhận bạn đã tự gán nhãn mới. Kiểm lại họ tên/MSSV trước nộp.
2. Push nhánh bằng tài khoản GitHub của bạn (lệnh dưới). Nếu Git yêu cầu đăng nhập,
   hoàn tất đăng nhập trong trình quản lý Git của máy; không đưa token vào repo.
3. Trong fork, tab Actions → bật workflows nếu GitHub đang tắt workflow ở fork.
4. Tạo PR trong **fork cá nhân**: base main ← compare starter/d09. Không chọn repo
   giảng viên hoặc repo nhóm Day 8 làm base. Copy nội dung PR_DESCRIPTION.md.
5. Đợi cả eval-gate và eval-gate-v2 xanh. Nếu mở PR khi Actions còn tắt, bật rồi
   chạy workflow bằng Run workflow trên starter/d09. Kết quả local không thay cho
   trạng thái GitHub Actions thực tế.
6. Dán **link PR** vào LMS “Day 9 Lab Assignment 3A” trước hạn theo thông báo lớp.
   Giảng viên chấm commit cuối trước hạn. Không cần merge PR để nộp.

```powershell
cd D:\VINAI20K\K5-L3A-DAY09-TaCongBinh-2A202603628-EvaluationandFailureAnalysis
git status
git push -u origin starter/d09
```

Mở trang tạo PR sau khi push:
https://github.com/BinhTa2004/K5-L3A-DAY09-TaCongBinh-2A202603628-EvaluationandFailureAnalysis/compare/main...starter/d09

## Chạy lại trên máy

Môi trường riêng đã dùng: D:\VINAI20K\.venv-day09 (ngoài repo).

```powershell
cd D:\VINAI20K\K5-L3A-DAY09-TaCongBinh-2A202603628-EvaluationandFailureAnalysis\src
$env:PYTHONUTF8='1'
& D:\VINAI20K\.venv-day09\Scripts\python.exe -m lab9.smoke
& D:\VINAI20K\.venv-day09\Scripts\python.exe -m pytest -q -o addopts= -k "lab9 or not student" -p no:cacheprovider
& D:\VINAI20K\.venv-day09\Scripts\python.exe -m lab9.mutation --spec config/metric_spec_v2.yaml --baseline reports/baseline_v2.json
```

248 test student Day 8 của ba shape chưa làm và ma trận gốc không thuộc phạm vi triển
khai Lab 9; không sửa ba shape đó để làm xanh toàn bộ bài nhóm. Các test host/crash
và test Lab 9 được chạy cùng nhau. Không cần API key, Langfuse hoặc dịch vụ bên ngoài.

## Giới hạn cần biết

Test ẩn và key anchor thuộc giảng viên. Ratchet cần --base-spec tin cậy; workflow
được phát sẵn chưa tự nạp spec main. Các hạn chế được nêu trong eval card/PRD,
không sửa workflow hoặc bộ chấm để che giới hạn này.
