$env:PYTHONUTF8 = "1"
Set-Location $PSScriptRoot
$py = "..\..\..\source_code\.venv\Scripts\python.exe"
# Dọn các tài liệu đã nạp ở smoke test để chạy lại TIEN_01..04 trên dữ liệu sạch
& $py -c "import sys; sys.path.insert(0,'..'); import pgpt_client as c; [print(a, c.delete_doc(a).status_code) for a in ['bao_mat','hoan_tien','bang_gia','nghi_phep','faq']]"
& $py blackbox_runner.py BB_TIEN_01 BB_TIEN_02 BB_TIEN_03 BB_TIEN_04 BB_TIEN_21 BB_TIEN_22
& $py -c "import sys; sys.path.insert(0,'..'); import pgpt_client as c; print(c.ingest_file('product_faq_en.md','faq').status_code)"
& $py blackbox_runner.py DUY MANH
