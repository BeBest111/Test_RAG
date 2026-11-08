# =====================================================================
#  DEMO NHÓM 11 – KIỂM THỬ ỨNG DỤNG RAG (PrivateGPT)
#  Nhấn đúp shortcut "DEMO Nhom 11 - RAG" trên Desktop để chạy file này.
#  Tự khởi động: Ollama -> Qdrant -> PrivateGPT, rồi hiện menu demo.
# =====================================================================
param([switch]$Auto)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "DEMO Nhom 11 - Kiem thu ung dung RAG (PrivateGPT)"
$ROOT = $PSScriptRoot
$SRC  = Join-Path $ROOT "source_code"
$PY   = Join-Path $SRC ".venv\Scripts\python.exe"
$TS   = Join-Path $ROOT "03_MinhChung\test_scripts"
$OUT  = Join-Path $ROOT "03_MinhChung\demo_output"
$SLIDES = "https://claude.ai/artifact/KvsUK16oTMJfcz665FCgMw"
New-Item -ItemType Directory -Force $OUT | Out-Null
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

function Test-Url($u) {
    try { return (Invoke-WebRequest $u -UseBasicParsing -TimeoutSec 3).StatusCode -eq 200 } catch { return $false }
}

function Wait-Url($u, $name, $seconds) {
    Write-Host -NoNewline "   Đang chờ $name "
    for ($i = 0; $i -lt $seconds; $i += 3) {
        if (Test-Url $u) { Write-Host " SẴN SÀNG" -ForegroundColor Green; return $true }
        Write-Host -NoNewline "."
        Start-Sleep 3
    }
    Write-Host " QUÁ THỜI GIAN" -ForegroundColor Red
    return $false
}

function Start-System {
    Write-Host "`n[1/3] Ollama (máy chủ mô hình ngôn ngữ)" -ForegroundColor Cyan
    if (-not (Test-Url "http://localhost:11434/api/version")) {
        Start-Process (Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama app.exe")
        Wait-Url "http://localhost:11434/api/version" "Ollama" 60 | Out-Null
    } else { Write-Host "   Đã chạy sẵn" -ForegroundColor Green }
    # nạp sẵn mô hình vào RAM để câu hỏi đầu tiên nhanh hơn
    Start-Job { try { Invoke-RestMethod -Method Post http://localhost:11434/api/generate -Body '{"model":"qwen2.5:3b","prompt":"hi","keep_alive":"60m","stream":false}' -TimeoutSec 300 | Out-Null } catch {} } | Out-Null

    Write-Host "[2/3] Qdrant (cơ sở dữ liệu vector)" -ForegroundColor Cyan
    if (-not (Test-Url "http://localhost:6333/healthz")) {
        $q = Join-Path $SRC "qdrant_server"
        Start-Process (Join-Path $q "qdrant.exe") -WorkingDirectory $q -WindowStyle Minimized
        Wait-Url "http://localhost:6333/healthz" "Qdrant" 60 | Out-Null
    } else { Write-Host "   Đã chạy sẵn" -ForegroundColor Green }

    Write-Host "[3/3] PrivateGPT (API + giao diện Workbench, cổng 8080)" -ForegroundColor Cyan
    if (-not (Test-Url "http://localhost:8080/health")) {
        Start-Process powershell -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$(Join-Path $SRC 'run_nhom11.ps1')`"") -WindowStyle Minimized
        Wait-Url "http://localhost:8080/health" "PrivateGPT (lần đầu mất 1-3 phút)" 300 | Out-Null
    } else { Write-Host "   Đã chạy sẵn" -ForegroundColor Green }
}

function Stop-System {
    Write-Host "Đang tắt PrivateGPT và Qdrant..." -ForegroundColor Yellow
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*private_gpt*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
    Get-Process qdrant -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "Đã tắt. (Ollama vẫn chạy nền như bình thường)" -ForegroundColor Green
}

function Run-Py($dir, [string[]]$pyArgs) {
    Push-Location $dir
    & $PY @pyArgs
    Pop-Location
}

function Pause-Menu { Write-Host "`nNhấn Enter để quay lại menu..." -ForegroundColor DarkGray; Read-Host | Out-Null }

function Wait-Next($seconds) {
    # Chờ vài giây rồi tự chạy tiếp; nhấn phím bất kỳ để đi tiếp ngay
    Write-Host ""
    for ($i = $seconds; $i -gt 0; $i--) {
        Write-Host -NoNewline "`r   → Bước tiếp theo sau $i giây (nhấn phím bất kỳ để chạy ngay)...   " -ForegroundColor DarkGray
        for ($j = 0; $j -lt 10; $j++) {
            if ([Console]::KeyAvailable) { [Console]::ReadKey($true) | Out-Null; Write-Host ""; return }
            Start-Sleep -Milliseconds 100
        }
    }
    Write-Host ""
}

function Step-Banner($n, $total, $title, [string[]]$say) {
    Write-Host ""
    Write-Host ("#" * 78) -ForegroundColor Yellow
    Write-Host ("  BƯỚC $n/$total – $title") -ForegroundColor Yellow
    Write-Host ("#" * 78) -ForegroundColor Yellow
    foreach ($s in $say) { Write-Host "  ▸ $s" -ForegroundColor Cyan }
    Write-Host ""
}

function Run-AutoDemo {
    $T = 7
    Clear-Host
    Write-Host "==============================================================================" -ForegroundColor Green
    Write-Host "   DEMO TỰ ĐỘNG – NHÓM 11 – KIỂM THỬ ỨNG DỤNG RAG (PrivateGPT)" -ForegroundColor Green
    Write-Host "   Mỗi bước chạy thật trên hệ thống; giữa các bước dừng 8 giây để giải thích." -ForegroundColor Green
    Write-Host "==============================================================================" -ForegroundColor Green

    Step-Banner 1 $T "Hệ thống đang chạy những gì?" @(
        "Ollama: chạy mô hình AI qwen2.5:3b ngay trên máy (không cần Internet).",
        "Qdrant: 'thư viện' lưu tài liệu dưới dạng vector để tìm kiếm theo ý nghĩa.",
        "PrivateGPT: phần mềm được kiểm thử – API + giao diện ở http://localhost:8080.")
    foreach ($s in @(@("Ollama (AI)", "http://localhost:11434/api/version"), @("Qdrant (thư viện vector)", "http://localhost:6333/healthz"), @("PrivateGPT (hệ thống kiểm thử)", "http://localhost:8080/health"))) {
        $ok = Test-Url $s[1]
        Write-Host ("   {0,-34} {1}" -f $s[0], $(if ($ok) { "ĐANG CHẠY" } else { "KHÔNG PHẢN HỒI" })) -ForegroundColor $(if ($ok) { "Green" } else { "Red" })
    }
    Wait-Next 8

    Step-Banner 2 $T "Demo RAG: nạp tài liệu mới → hỏi → AI trả lời có căn cứ" @(
        "Giống bài thi mở sách: AI TÌM đoạn tài liệu, ĐỌC, rồi TRẢ LỜI.",
        "Câu hỏi: 'Đi muộn quá 15 phút bị phạt bao nhiêu?' – đáp án đúng trong tài liệu: 50.000 đồng.",
        "Chờ khoảng 30–90 giây vì AI chạy bằng CPU.")
    Run-Py $TS @("demo_rag.py")
    Write-Host "  ▸ Nhận xét: trả lời đúng nội dung; nếu trả lời bằng tiếng Anh thì đó là lỗi BUG-18 nhóm đã ghi nhận." -ForegroundColor Cyan
    Wait-Next 8

    Step-Banner 3 $T "Kiểm thử giao diện tự động – trình duyệt tự thao tác" @(
        "Playwright điều khiển Microsoft Edge: tự tạo chat, đổi tên, tải lại trang, gõ Shift+Enter.",
        "UI_MANH_08 nhập địa chỉ sai 'abc xyz' → hệ thống vẫn lưu (lỗi BUG-21).")
    $env:DEMO_HEADED = "1"; $env:DEMO_UI_LOG = Join-Path $OUT "ui_demo.json"; $env:DEMO_SHOTS = Join-Path $OUT "screenshots"
    Run-Py (Join-Path $TS "ui") @("ui_tests.py", "UI_MANH_01", "UI_MANH_02", "UI_MANH_05", "UI_MANH_07", "UI_MANH_08")
    Remove-Item Env:DEMO_HEADED, Env:DEMO_UI_LOG, Env:DEMO_SHOTS
    Wait-Next 8

    Step-Banner 4 $T "Kiểm thử hộp đen API – 12 ca (đầu vào sai, biên, bảo mật)" @(
        "Mỗi dòng: mã ca – Pass/Fail – thời gian – phản hồi thật của hệ thống.",
        "Chú ý BB_TIEN_17 FAIL: hệ thống đọc được file C:\Windows\win.ini của máy chủ (lỗ hổng BUG-02).",
        "BB_TIEN_16 FAIL: tên tài liệu chứa '../' vẫn được chấp nhận (BUG-03).")
    $env:DEMO_BB_LOG = Join-Path $OUT "blackbox_demo.json"
    Run-Py (Join-Path $TS "blackbox") @("blackbox_runner.py", "BB_TIEN_06", "BB_TIEN_07", "BB_TIEN_10", "BB_TIEN_13", "BB_TIEN_16", "BB_TIEN_17", "BB_VINH_03", "BB_VINH_06", "BB_VINH_11", "BB_MANH_01", "BB_MANH_03", "BB_MANH_11")
    Remove-Item Env:DEMO_BB_LOG
    Wait-Next 8

    Step-Banner 5 $T "Lỗi nghiêm trọng nhất: gửi 6 tài liệu CÙNG LÚC" @(
        "Gửi lần lượt thì không sao; 6 yêu cầu song song thì tài liệu bị mất.",
        "Xem 'listed' (còn lại) và 'missing_from_list' (bị mất) – lần chạy chính thức chỉ còn 1/6 (BUG-01).")
    Run-Py (Join-Path $TS "performance") @("concurrency_ingest_test.py")
    Wait-Next 8

    Step-Banner 6 $T "Kiểm thử đơn vị (unit test) bằng pytest – 40 ca" @(
        "Kiểm tra từng hàm nhỏ: kiểm tra base64, giới hạn độ dài, tham số AI, bộ đọc trích dẫn.",
        "Kết quả mong đợi: 39 passed, 1 failed – ca UT_DUY_05 fail là phát hiện thật.")
    Run-Py $SRC @("-m", "pytest", (Join-Path $TS "unit"), "-q", "-p", "no:cacheprovider", "--rootdir=$SRC")
    Wait-Next 8

    Step-Banner 7 $T "Tổng kết toàn bộ kết quả kiểm thử chính thức" @("Số liệu lấy từ log chạy thật – trùng với file 02_KetQua_KiemThu_Nhom11.xlsx.")
    Run-Py $TS @("show_summary.py")
    Write-Host ""
    Write-Host "  DEMO HOÀN TẤT. Cảm ơn thầy và các bạn!" -ForegroundColor Green
}

Clear-Host
Write-Host "==============================================================" -ForegroundColor Yellow
Write-Host "   NHÓM 11 – KIỂM THỬ ỨNG DỤNG RAG – HỆ THỐNG PrivateGPT" -ForegroundColor Yellow
Write-Host "==============================================================" -ForegroundColor Yellow
Start-System
if ($Auto) { Run-AutoDemo; Pause-Menu }

while ($true) {
    $ok = Test-Url "http://localhost:8080/health"
    Write-Host "`n==================== MENU DEMO ====================" -ForegroundColor Yellow
    Write-Host ("Trạng thái hệ thống: " + $(if ($ok) { "ĐANG CHẠY" } else { "CHƯA SẴN SÀNG – chọn 9 để khởi động lại" })) -ForegroundColor $(if ($ok) { "Green" } else { "Red" })
    Write-Host " A. CHẠY DEMO TỰ ĐỘNG TOÀN BỘ (~6-8 phút, có giải thích từng bước)" -ForegroundColor Green
    Write-Host " S. Xem bảng tổng kết kết quả kiểm thử"
    Write-Host " 1. Mở giao diện PrivateGPT Workbench (trình duyệt)"
    Write-Host " 2. DEMO RAG trực tiếp: nạp tài liệu -> hỏi đáp có trích dẫn (~1 phút)"
    Write-Host " 3. Chạy unit test của nhóm (pytest, ~20 giây)"
    Write-Host " 4. Chạy test hộp đen API – bộ nhanh 12 case (~1-2 phút)"
    Write-Host " 5. Chạy test giao diện tự động – HIỆN TRÌNH DUYỆT (~1 phút)"
    Write-Host " 6. Demo lỗi nghiêm trọng: nạp đồng thời làm mất tài liệu (~1 phút)"
    Write-Host " 7. Mở thư mục nộp bài (Excel, báo cáo, minh chứng)"
    Write-Host " 8. Mở slide thuyết trình"
    Write-Host " 9. Khởi động lại hệ thống"
    Write-Host " 0. Tắt hệ thống và thoát"
    $c = Read-Host "Chọn"
    switch ($c) {
        { $_ -in "A", "a" } { Run-AutoDemo; Pause-Menu }
        { $_ -in "S", "s" } { Run-Py $TS @("show_summary.py"); Pause-Menu }
        "1" { Start-Process "http://localhost:8080/ui"; Write-Host "Lần đầu mở: ô URL giữ http://localhost:8080, Collection nhập: nhom11, bấm 'Save and check'." -ForegroundColor Cyan }
        "2" { Run-Py $TS @("demo_rag.py"); Pause-Menu }
        "3" { Run-Py (Join-Path $SRC "") @("-m", "pytest", (Join-Path $TS "unit"), "-v", "-p", "no:cacheprovider", "--rootdir=$SRC"); Pause-Menu }
        "4" {
            $env:DEMO_BB_LOG = Join-Path $OUT "blackbox_demo.json"
            Run-Py (Join-Path $TS "blackbox") @("blackbox_runner.py", "BB_TIEN_06", "BB_TIEN_07", "BB_TIEN_10", "BB_TIEN_13", "BB_TIEN_16", "BB_TIEN_17", "BB_VINH_03", "BB_VINH_06", "BB_VINH_11", "BB_MANH_01", "BB_MANH_03", "BB_MANH_11")
            Remove-Item Env:DEMO_BB_LOG; Pause-Menu }
        "5" {
            $env:DEMO_HEADED = "1"; $env:DEMO_UI_LOG = Join-Path $OUT "ui_demo.json"; $env:DEMO_SHOTS = Join-Path $OUT "screenshots"
            Run-Py (Join-Path $TS "ui") @("ui_tests.py", "UI_MANH_01", "UI_MANH_02", "UI_MANH_05", "UI_MANH_07", "UI_MANH_08", "UI_TIEN_01")
            Remove-Item Env:DEMO_HEADED, Env:DEMO_UI_LOG, Env:DEMO_SHOTS; Pause-Menu }
        "6" { Run-Py (Join-Path $TS "performance") @("concurrency_ingest_test.py"); Pause-Menu }
        "7" { Start-Process explorer.exe (Join-Path $ROOT "NOP_BAI_Nhom11") }
        "8" { Start-Process $SLIDES }
        "9" { Start-System }
        "0" { Stop-System; Start-Sleep 2; exit }
        default { Write-Host "Chọn từ 0 đến 9." -ForegroundColor Red }
    }
}
