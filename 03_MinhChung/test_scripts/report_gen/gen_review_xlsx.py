"""Sinh file 01_KetQua_Review_Nhom11.xlsx (kết quả review tài liệu + review code)."""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference

from xlsx_style import (MEMBERS, data_rows, header_row, kv_table, section,
                        title_block)

OUT = Path(__file__).resolve().parents[3] / "01_KetQua_Review_Nhom11.xlsx"
SUB = "Nhóm 11 – Hệ thống: PrivateGPT (github.com/zylon-ai/private-gpt, commit 42ce052) – Thời gian review: 18/10/2026 – 25/10/2026"

wb = Workbook()

# ------------------------------------------------------------------ 1. Thông tin
ws = wb.active
ws.title = "1. Thong tin chung"
title_block(ws, "KẾT QUẢ REVIEW – BÀI TẬP NHÓM MÔN ĐẢM BẢO CHẤT LƯỢNG PHẦN MỀM", SUB, 2)
r = kv_table(ws, 4, [
    ("Môn học", "Đảm bảo chất lượng phần mềm (SQA) – GVHD: Đào Ngọc Phong"),
    ("Nhóm", "Nhóm 11 – STT trình bày thứ 3 – Lớp D22VHCNPM02"),
    ("Chủ đề", "Kiểm thử ứng dụng RAG (Retrieval-Augmented Generation)"),
    ("Hệ thống được chọn", "PrivateGPT v1.0.1 – Zylon AI. Mã nguồn mở Apache-2.0, ~57.600 sao GitHub. "
                          "Link: https://github.com/zylon-ai/private-gpt (commit 42ce052, 29/10/2026 được dùng để kiểm thử lại)"),
    ("Tài liệu được review", "(1) ui/docs/PRD.md – đặc tả yêu cầu sản phẩm Workbench (1.000 dòng)\n"
                             "(2) ui/docs/STYLE_GUIDE.md – đặc tả giao diện\n"
                             "(3) fern/docs/pages/** – tài liệu cài đặt, API guide (ingestion, messages), provider Ollama\n"
                             "(4) fern/openapi/openapi.json – hợp đồng API\n"
                             "(5) Tài liệu đặc tả bổ sung của nhóm: 03_MinhChung/DacTa_YeuCau_BoSung_Nhom11.docx"),
    ("Hình thức review", "Inspection theo checklist (mỗi thành viên đọc trước độc lập, họp review chung ngày 21/10/2026 và 25/10/2026)"),
    ("Vai trò trong buổi review", "Moderator: Nguyễn Minh Tiến | Thư ký: Bùi Văn Mạnh | Reviewer: Nguyễn Bá Quang Vinh, Vũ Đức Duy | "
                                  "Tác giả tài liệu: Zylon AI (không tham dự – nhóm ghi nhận lỗi để báo cáo)"),
    ("Thang đánh giá", "Đạt / Không đạt / Đạt một phần / N/A. Mức độ lỗi: Cao – Trung bình – Thấp"),
])
r = section(ws, r + 1, "PHÂN CÔNG CHỨC NĂNG", 2)
for k, (n, msv, f) in MEMBERS.items():
    r = kv_table(ws, r, [(f"{n} ({msv})", f)])

# ------------------------------------------------------------------ 2. Checklist tài liệu (cả nhóm)
ws = wb.create_sheet("2. CL Review dac ta (nhom)")
H = ["STT", "Nhóm tiêu chí", "Câu hỏi kiểm tra (checklist)", "Tài liệu / vị trí", "Kết quả", "Bằng chứng / nhận xét", "Mã lỗi", "Người review", "Ngày"]
title_block(ws, "CHECKLIST REVIEW TÀI LIỆU ĐẶC TẢ YÊU CẦU (CÔNG VIỆC CHUNG CỦA NHÓM)", SUB, len(H))
header_row(ws, 4, H, [6, 16, 46, 26, 13, 60, 10, 16, 12])
CL = [
    ("Tính đầy đủ", "Tài liệu có mô tả mục tiêu, phạm vi, đối tượng sử dụng của hệ thống?", "PRD.md – Purpose, Primary Goals, Non-Goals", "Đạt", "Có mục Project Context, Purpose, Primary Goals (4 mục tiêu) và Non-Goals rõ ràng.", "", "Tiến", "18/10/2026"),
    ("Tính đầy đủ", "Tất cả chức năng chính đều được đặc tả (nạp, liệt kê, xóa tài liệu, hỏi đáp, hội thoại, cấu hình)?", "PRD.md – Context Screen, Chat Screen, Settings", "Đạt", "Có đủ các màn hình Context/Documents, Chat, Settings, API Debugger và 23 tiêu chí chấp nhận MVP.", "", "Vinh", "18/10/2026"),
    ("Tính đầy đủ", "Có yêu cầu phi chức năng: thời gian phản hồi, giới hạn kích thước file, số lượng tài liệu, tải đồng thời?", "PRD.md (toàn bộ)", "Không đạt", "Không có bất kỳ chỉ tiêu hiệu năng nào. Giới hạn file chỉ nằm trong settings.yaml (max_file_size) và chỉ cảnh báo.", "DOC-06", "Duy", "19/10/2026"),
    ("Tính đầy đủ", "Có đặc tả hành vi khi lỗi (nạp lỗi, xóa tài liệu không tồn tại, LLM không phản hồi)?", "PRD.md – UX Principles; api-guide/ingestion.mdx", "Không đạt", "Chỉ ghi chung chung 'Errors clearly shown', 'All errors should be visible'. Không định nghĩa mã lỗi/thông báo cho từng tình huống.", "DOC-07", "Mạnh", "19/10/2026"),
    ("Tính đầy đủ", "Có định nghĩa hành vi khi nạp lại tài liệu trùng mã artifact (ghi đè/từ chối)?", "api-guide/ingestion.mdx; PRD.md – Upload behavior", "Không đạt", "Không đề cập. Thực tế: nạp trùng nội dung trả 200 với data rỗng, nạp trùng mã khác nội dung thì ghi đè.", "DOC-11", "Tiến", "19/10/2026"),
    ("Tính đầy đủ", "Có yêu cầu về giới hạn lịch sử hội thoại / cửa sổ ngữ cảnh?", "PRD.md – Chat Screen; providers/ollama.mdx", "Đạt một phần", "Ollama doc cảnh báo context 4k, nhưng PRD không quy định độ dài lịch sử tối đa (settings maximum_history_length=0).", "DOC-15", "Mạnh", "20/10/2026"),
    ("Tính đầy đủ", "Có yêu cầu phần cứng/mô hình tối thiểu để hệ thống hoạt động đúng (khả năng gọi tool)?", "providers/ollama.mdx; README.md", "Không đạt", "Chỉ gợi ý qwen3.5:35b (~24GB). Không nêu yêu cầu model phải hỗ trợ tool calling; llama3.2 3B gọi sai tool -> RAG không hoạt động.", "DOC-16", "Duy", "20/10/2026"),
    ("Tính nhất quán", "Các tài liệu thống nhất về địa chỉ API mặc định?", "PRD.md dòng 174, 197; settings.yaml dòng 7", "Không đạt", "PRD ghi http://127.0.0.1:8001; server chạy cổng 8080; UI dùng window.location.origin.", "DOC-01", "Mạnh", "20/10/2026"),
    ("Tính nhất quán", "Cơ chế xác thực được mô tả thống nhất?", "PRD.md dòng 182, 198, 461, 963", "Không đạt", "Chỗ ghi 'API key / bearer token', chỗ ghi 'chỉ hỗ trợ HTTP Basic auth'.", "DOC-02", "Mạnh", "20/10/2026"),
    ("Tính nhất quán", "Đặc tả giao diện (STYLE_GUIDE) khớp với PRD?", "STYLE_GUIDE.md dòng 476-480 vs PRD.md dòng 749", "Không đạt", "STYLE_GUIDE còn mô tả 'Thinking Button' trong khi PRD nói effort chọn trong dropdown model.", "DOC-03", "Duy", "21/10/2026"),
    ("Tính nhất quán", "Thao tác trên dòng tài liệu nhất quán giữa PRD và STYLE_GUIDE?", "STYLE_GUIDE.md – Documents; PRD.md dòng 500-501", "Không đạt", "STYLE_GUIDE yêu cầu menu Preview/Search/Delete + trạng thái Indexed/Processing/Failed; PRD để Preview/Search là tùy chọn. Bản cài đặt chỉ có Delete, trạng thái gán cứng 'Indexed'.", "DOC-05", "Vinh", "21/10/2026"),
    ("Tính nhất quán", "Mã HTTP trong tài liệu API khớp với hành vi thực tế?", "OpenAPI: response 422; global_handler.py", "Không đạt", "Tài liệu khai báo 422 cho lỗi validation; server trả 400 (đã xác nhận bằng BB_TIEN_08).", "DOC-04", "Tiến", "21/10/2026"),
    ("Tính nhất quán", "Ví dụ trong tài liệu API khớp định dạng request thực tế?", "api-guide/ingestion.mdx – 'curl -F file=@...'", "Không đạt", "Tài liệu hướng dẫn upload multipart (-F file=@), nhưng endpoint chỉ nhận JSON base64 (BB_TIEN_22).", "DOC-08", "Tiến", "21/10/2026"),
    ("Tính rõ ràng", "Mỗi yêu cầu có một cách hiểu duy nhất, không dùng từ mơ hồ ('nhanh', 'đẹp', 'phù hợp')?", "PRD.md – UX Principles", "Đạt một phần", "Nhiều câu mơ hồ: 'polished enough', 'dense but readable', 'Errors clearly shown'.", "DOC-07", "Vinh", "21/10/2026"),
    ("Tính rõ ràng", "Thuật ngữ (artifact, collection, tool_context) được định nghĩa?", "PRD.md; getting-started/how-it-works.mdx", "Đạt một phần", "Được dùng xuyên suốt, có giải thích trong how-it-works nhưng PRD không có bảng thuật ngữ.", "", "Duy", "21/10/2026"),
    ("Tính kiểm thử được", "Các tiêu chí chấp nhận có thể kiểm chứng (đo được, có điều kiện đạt)?", "PRD.md – MVP Acceptance Criteria (23 mục)", "Đạt", "23 tiêu chí dạng 'User can ...' kiểm chứng được bằng kiểm thử chức năng.", "", "Tiến", "22/10/2026"),
    ("Tính kiểm thử được", "Yêu cầu có định danh (ID) để truy vết với test case?", "PRD.md", "Không đạt", "Yêu cầu không có ID (chỉ đánh số MVP 1-23). Nhóm phải tự gán mã REQ-xx trong tài liệu bổ sung.", "DOC-13", "Vinh", "22/10/2026"),
    ("Tính khả thi", "Hướng dẫn cài đặt chạy được trên các nền tảng tuyên bố hỗ trợ (Windows)?", "installation/local.mdx – tab Windows", "Không đạt", "Thiếu lệnh con 'serve'; bản 'core' thiếu celery, import fcntl (Unix-only), libmagic không có sẵn, Qdrant local lock lỗi WinError 32.", "DOC-09, DOC-10", "Mạnh", "17/10/2026"),
    ("Tính khả thi", "Yêu cầu bảo mật khả thi và được nêu rõ (lưu mật khẩu, phân quyền collection)?", "PRD.md – Not For Production", "Đạt một phần", "PRD thừa nhận rủi ro localStorage/no access-control nhưng không có yêu cầu giảm thiểu; không có yêu cầu kiểm tra đầu vào artifact/collection.", "DOC-12", "Duy", "22/10/2026"),
    ("Tổ chức tài liệu", "Tài liệu có cấu trúc mục lục rõ ràng, phiên bản, ngày cập nhật?", "PRD.md, STYLE_GUIDE.md", "Đạt một phần", "Cấu trúc tốt nhưng không có số phiên bản/ngày/tác giả/lịch sử thay đổi.", "DOC-14", "Tiến", "22/10/2026"),
    ("Tổ chức tài liệu", "Có sơ đồ kiến trúc/luồng dữ liệu?", "getting-started/how-it-works.mdx; README", "Đạt", "README có sơ đồ App -> PrivateGPT API -> Inference server; how-it-works mô tả luồng ingest/retrieval.", "", "Vinh", "22/10/2026"),
    ("Truy vết", "Yêu cầu giao diện (PRD) truy vết được tới endpoint API (OpenAPI)?", "PRD.md – API Client, Endpoints used", "Đạt", "PRD liệt kê endpoint dùng cho từng chức năng và chỉ định openapi.json là nguồn sự thật.", "", "Duy", "23/10/2026"),
    ("Truy vết", "Tài liệu và mã nguồn đồng bộ (test UI tồn tại khớp code)?", "tests/server/test_ui_mount.py dòng 9; launcher.py dòng 260", "Đạt", "Ban đầu nghi ngờ test kiểm tra chuỗi DEFAULT_BASE_URL cũ; khi chạy thực tế test PASS (launcher thay chuỗi lúc mount) -> không phải lỗi.", "", "Mạnh", "23/10/2026"),
    ("Hiệu năng (NFR)", "Có quy định thời gian phản hồi chấp nhận được cho hỏi đáp và nạp tài liệu?", "Toàn bộ tài liệu", "Không đạt", "Không có. Đo thực tế: nạp file 1KB ~10-20s, file 2,7MB > 600s; hỏi đáp RAG 30-90s trên CPU.", "DOC-06", "Duy", "23/10/2026"),
    ("Khả năng sử dụng", "Đặc tả giao diện có yêu cầu responsive, đa ngôn ngữ?", "STYLE_GUIDE.md – Responsive Behavior", "Đạt một phần", "Có yêu cầu tối thiểu cho màn hình hẹp; không đề cập đa ngôn ngữ/tiếng Việt (IME).", "", "Vinh", "23/10/2026"),
]
rows = [[i + 1, *row] for i, row in enumerate(CL)]
data_rows(ws, 5, rows, status_col=5, center_cols=(1, 5, 7, 8, 9))

# ------------------------------------------------------------------ 3. Danh sách lỗi tài liệu
ws = wb.create_sheet("3. Loi tai lieu")
H = ["Mã lỗi", "Tài liệu", "Vị trí", "Mô tả lỗi", "Loại lỗi", "Mức độ", "Đề xuất sửa", "Người phát hiện", "Ngày", "Trạng thái"]
title_block(ws, "DANH SÁCH LỖI PHÁT HIỆN TRONG TÀI LIỆU", SUB, len(H))
header_row(ws, 4, H, [9, 20, 22, 52, 15, 11, 45, 15, 12, 12])
DOC_DEFECTS = [
    ("DOC-01", "PRD.md", "Dòng 174, 197", "URL API mặc định là http://127.0.0.1:8001, trong khi server chạy cổng 8080 và UI lấy window.location.origin.", "Không nhất quán", "Trung bình", "Sửa thành 'cùng origin với UI, mặc định 8080'.", "Mạnh", "20/10/2026", "Mở"),
    ("DOC-02", "PRD.md", "Dòng 182, 198, 461, 963", "Mâu thuẫn về cơ chế xác thực: bearer token vs chỉ Basic auth.", "Không nhất quán", "Trung bình", "Thống nhất: Basic auth (username/password); bỏ cụm 'API key/bearer token'.", "Mạnh", "20/10/2026", "Mở"),
    ("DOC-03", "STYLE_GUIDE.md", "Dòng 476-480", "Còn mô tả 'Thinking Button' đã bị thay bằng effort rail trong dropdown model.", "Lỗi thời", "Thấp", "Xóa mục Thinking Button khỏi Style Guide.", "Duy", "21/10/2026", "Mở"),
    ("DOC-04", "openapi.json / router docstring", "Các endpoint ingest, delete, content, messages", "Khai báo lỗi validation trả 422 nhưng server trả 400.", "Không nhất quán", "Trung bình", "Cập nhật OpenAPI hoặc sửa global handler trả 422.", "Tiến", "21/10/2026", "Mở"),
    ("DOC-05", "STYLE_GUIDE.md vs PRD.md", "Mục Documents", "Yêu cầu Preview/Search/Delete và trạng thái Indexed/Processing/Failed không thống nhất với PRD và chưa được cài đặt.", "Không nhất quán / thiếu", "Trung bình", "Xác định rõ chức năng bắt buộc; cài đặt trạng thái thực.", "Vinh", "21/10/2026", "Mở"),
    ("DOC-06", "PRD.md", "Toàn bộ", "Thiếu yêu cầu phi chức năng (thời gian phản hồi, giới hạn file, số tài liệu, tải đồng thời).", "Thiếu", "Cao", "Bổ sung mục Non-functional Requirements với chỉ tiêu đo được.", "Duy", "19/10/2026", "Mở"),
    ("DOC-07", "PRD.md", "UX Principles, Chat Screen", "Đặc tả xử lý lỗi mơ hồ ('Errors clearly shown'), không có danh mục thông báo lỗi.", "Mơ hồ", "Trung bình", "Bổ sung bảng tình huống lỗi – mã HTTP – thông báo hiển thị.", "Mạnh", "19/10/2026", "Mở"),
    ("DOC-08", "api-guide/ingestion.mdx", "Mục 'Ingest a file'", "Ví dụ dùng multipart 'curl -F file=@...' nhưng endpoint chỉ nhận JSON base64.", "Sai", "Cao", "Sửa ví dụ sang JSON {artifact, collection, input{type:file,value:<base64>}}.", "Tiến", "21/10/2026", "Mở"),
    ("DOC-09", "installation/local.mdx", "Tab Windows (PowerShell/CMD)", "Lệnh 'uv run python -m private_gpt' thiếu lệnh con 'serve' -> chỉ in trợ giúp.", "Sai", "Trung bình", "Sửa thành 'uv run python -m private_gpt serve'.", "Mạnh", "17/10/2026", "Mở"),
    ("DOC-10", "installation/local.mdx; pyproject.toml", "Extra 'core'", "Hướng dẫn tuyên bố hỗ trợ Windows nhưng bản core không khởi động được (thiếu celery, fcntl Unix-only, libmagic, Qdrant lock).", "Sai / thiếu", "Cao", "Ghi rõ Windows chỉ hỗ trợ qua Docker/WSL hoặc sửa mã (BUG-ENV-01..05).", "Mạnh", "17/10/2026", "Mở"),
    ("DOC-11", "api-guide/ingestion.mdx", "Ingest", "Không quy định hành vi khi nạp trùng artifact / trùng nội dung.", "Thiếu", "Trung bình", "Quy định rõ: ghi đè và trả về thông tin tài liệu, hoặc từ chối 409.", "Tiến", "19/10/2026", "Mở"),
    ("DOC-12", "PRD.md; api-guide", "Bảo mật", "Không có yêu cầu kiểm tra ký tự hợp lệ cho artifact/collection, giới hạn URI ingest.", "Thiếu", "Cao", "Bổ sung ràng buộc ^[A-Za-z0-9_-]{1,255}$ và whitelist scheme http(s)/s3.", "Duy", "22/10/2026", "Mở"),
    ("DOC-13", "PRD.md", "Toàn bộ", "Yêu cầu không có mã định danh -> khó truy vết test case.", "Thiếu", "Thấp", "Gán mã REQ-xxx cho từng yêu cầu.", "Vinh", "22/10/2026", "Mở"),
    ("DOC-14", "PRD.md, STYLE_GUIDE.md", "Đầu tài liệu", "Không có phiên bản, ngày, tác giả, lịch sử thay đổi.", "Định dạng", "Thấp", "Thêm bảng Document Control.", "Tiến", "22/10/2026", "Mở"),
    ("DOC-15", "PRD.md", "Chat Screen", "Không quy định giới hạn độ dài lịch sử hội thoại/xử lý tràn context window.", "Thiếu", "Trung bình", "Quy định số lượt tối đa và chiến lược rút gọn lịch sử.", "Mạnh", "20/10/2026", "Mở"),
    ("DOC-16", "providers/ollama.mdx", "Setup", "Không nêu yêu cầu model phải hỗ trợ tool calling; model nhỏ (llama3.2) làm RAG không hoạt động.", "Thiếu", "Cao", "Bổ sung danh sách model tối thiểu đã kiểm chứng và cảnh báo tool calling.", "Duy", "20/10/2026", "Mở"),
]
data_rows(ws, 5, DOC_DEFECTS, center_cols=(1, 5, 6, 8, 9, 10))

# ------------------------------------------------------------------ 4. Review đặc tả từng chức năng
ws = wb.create_sheet("4. Review dac ta chuc nang")
H = ["Thành viên", "Mã YC", "Nội dung yêu cầu (trích/diễn giải)", "Nguồn", "Đầy đủ", "Rõ ràng", "Kiểm thử được", "Nhất quán", "Nhận xét / đề xuất", "Ngày"]
title_block(ws, "REVIEW CỤ THỂ TÀI LIỆU ĐẶC TẢ PHẦN CHỨC NĂNG CỦA TỪNG CÁ NHÂN", SUB, len(H))
header_row(ws, 4, H, [18, 11, 50, 22, 10, 10, 11, 10, 50, 12])
SPEC = [
    ("Nguyễn Minh Tiến", "REQ-ING-01", "Người dùng tải file lên và nạp qua POST /v1/artifacts/ingest", "PRD 497; MVP #8", "Đạt", "Đạt", "Đạt", "Đạt", "Rõ ràng, có ví dụ body.", "18/10/2026"),
    ("Nguyễn Minh Tiến", "REQ-ING-02", "File được chuyển sang base64, artifact id = tên file + timestamp/UUID, metadata.file_name", "PRD 515-535", "Đạt", "Đạt", "Đạt", "Không đạt", "Mâu thuẫn với api-guide dùng multipart (DOC-08).", "19/10/2026"),
    ("Nguyễn Minh Tiến", "REQ-ING-03", "Hỗ trợ các định dạng .pdf .docx .pptx .md .csv .json ... ; định dạng khác đọc như text", "ingestion.mdx", "Đạt một phần", "Không đạt", "Đạt", "Không đạt", "'Định dạng khác đọc như text' mâu thuẫn với việc .zip bị từ chối; không nêu danh sách bị cấm.", "19/10/2026"),
    ("Nguyễn Minh Tiến", "REQ-ING-04", "Giới hạn kích thước file / thời gian nạp", "(không có)", "Không đạt", "N/A", "Không đạt", "N/A", "Thiếu hoàn toàn (DOC-06). Đề xuất: ≤ 25MB, nạp ≤ 60s/MB.", "20/10/2026"),
    ("Nguyễn Minh Tiến", "REQ-ING-05", "Hành vi khi nạp trùng artifact", "(không có)", "Không đạt", "N/A", "Không đạt", "N/A", "DOC-11.", "20/10/2026"),
    ("Nguyễn Bá Quang Vinh", "REQ-DOC-01", "Liệt kê tài liệu đã nạp qua GET /v1/artifacts/list?collection=", "PRD 498; MVP #9", "Đạt", "Đạt", "Đạt", "Đạt", "Không quy định phân trang/sắp xếp.", "18/10/2026"),
    ("Nguyễn Bá Quang Vinh", "REQ-DOC-02", "Xóa tài liệu qua POST /v1/artifacts/delete", "PRD 499", "Đạt một phần", "Đạt", "Đạt", "Đạt", "Không mô tả kết quả khi tài liệu không tồn tại / xóa 2 lần.", "19/10/2026"),
    ("Nguyễn Bá Quang Vinh", "REQ-DOC-03", "Xem trước nội dung qua /v1/artifacts/content (tùy chọn)", "PRD 501; STYLE_GUIDE Documents", "Đạt một phần", "Không đạt", "Đạt", "Không đạt", "PRD 'optional' nhưng STYLE_GUIDE bắt buộc menu Preview (DOC-05).", "19/10/2026"),
    ("Nguyễn Bá Quang Vinh", "REQ-DOC-04", "Dòng tài liệu hiển thị icon, tên, collection, badge loại file, trạng thái Indexed/Processing/Failed", "STYLE_GUIDE Documents", "Đạt", "Đạt", "Đạt", "Đạt", "Đặc tả rõ nhưng chưa được cài đặt đúng (trạng thái gán cứng).", "20/10/2026"),
    ("Nguyễn Bá Quang Vinh", "REQ-DOC-05", "Collection cấu hình trong Settings, áp dụng toàn cục", "PRD 505-513", "Đạt", "Đạt", "Đạt", "Đạt", "Rõ ràng.", "20/10/2026"),
    ("Vũ Đức Duy", "REQ-RAG-01", "Chat bật Documents -> thêm tool semantic_search + tool_context ingested_artifact (artifacts: [] = toàn collection)", "PRD 537-570; MVP #10-11", "Đạt", "Đạt", "Đạt", "Đạt", "Có ví dụ request cụ thể.", "18/10/2026"),
    ("Vũ Đức Duy", "REQ-RAG-02", "Câu trả lời có trích dẫn inline dạng nút số, bấm mở popup trích đoạn nguồn", "PRD 778-783", "Đạt", "Đạt", "Đạt", "Đạt", "Chi tiết tốt (index+1, popup, ghép nodes[].id).", "19/10/2026"),
    ("Vũ Đức Duy", "REQ-RAG-03", "Chất lượng câu trả lời: đúng theo tài liệu, không bịa khi không có thông tin", "(không có)", "Không đạt", "N/A", "Không đạt", "N/A", "Không có tiêu chí chất lượng RAG (faithfulness, answer relevancy). Nhóm đề xuất bổ sung.", "20/10/2026"),
    ("Vũ Đức Duy", "REQ-RAG-04", "Ngôn ngữ trả lời theo ngôn ngữ câu hỏi", "(không có)", "Không đạt", "N/A", "Đạt", "N/A", "Không đặc tả; thực tế model trả lời tiếng Anh cho câu hỏi tiếng Việt.", "21/10/2026"),
    ("Vũ Đức Duy", "REQ-RAG-05", "Yêu cầu model hỗ trợ tool calling", "ollama.mdx", "Không đạt", "N/A", "Đạt", "N/A", "DOC-16.", "21/10/2026"),
    ("Bùi Văn Mạnh", "REQ-SES-01", "Tạo/đổi tên/xóa/chuyển hội thoại; lưu localStorage; sắp xếp updatedAt DESC", "PRD 360-374; MVP #4-6", "Đạt", "Đạt", "Đạt", "Đạt", "Rõ ràng, kiểm thử được.", "18/10/2026"),
    ("Bùi Văn Mạnh", "REQ-SES-02", "Chọn model từ GET /v1/models; effort lưu theo chat", "PRD 745-750", "Đạt", "Đạt", "Đạt", "Không đạt", "Mâu thuẫn STYLE_GUIDE Thinking Button (DOC-03).", "19/10/2026"),
    ("Bùi Văn Mạnh", "REQ-SES-03", "Settings: Base URL, Basic auth, system prompt, citations, collection, Test API, Save, Clear local data", "PRD 395-419", "Đạt", "Đạt một phần", "Đạt", "Không đạt", "Mâu thuẫn URL mặc định (DOC-01) và auth (DOC-02); không quy định validate URL.", "20/10/2026"),
    ("Bùi Văn Mạnh", "REQ-SES-04", "API Debugger che Authorization/token/cookie, không lưu qua reload", "PRD 866-907", "Đạt", "Đạt", "Đạt", "Đạt", "Rõ ràng.", "20/10/2026"),
    ("Bùi Văn Mạnh", "REQ-SES-05", "Enter gửi, Shift+Enter xuống dòng", "PRD 764-769", "Đạt", "Đạt", "Đạt", "Đạt", "Không đề cập bộ gõ IME (tiếng Việt).", "21/10/2026"),
]
r = data_rows(ws, 5, SPEC, center_cols=(1, 2, 5, 6, 7, 8, 10))
for row in ws.iter_rows(min_row=5, max_row=r - 1, min_col=5, max_col=8):
    for cell in row:
        from xlsx_style import FAIL_FILL, NA_FILL, PART_FILL, PASS_FILL
        cell.fill = {"Đạt": PASS_FILL, "Không đạt": FAIL_FILL, "Đạt một phần": PART_FILL, "N/A": NA_FILL}.get(cell.value, cell.fill)

# ------------------------------------------------------------------ 5-8. Review code từng thành viên
CODE = {
    "TIEN": ("private_gpt/server/ingest/ingest_router.py, ingest_service.py, server/utils/artifact_input.py, components/ingestion/ingestion_scheduler.py, components/ingest/ingest_helper.py, uri_loader.py", [
        ("Kiểm tra trường bắt buộc / độ dài", "Đạt", "ingest_router.py:88-101", "artifact, collection min 1 / max 255."),
        ("Từ chối dữ liệu rỗng", "Đạt một phần", "artifact_input.py:26; ingest_helper.py:31", "Base64 rỗng bị chặn ở model; text rỗng chỉ bị chặn sau khi ghi file tạm."),
        ("Kiểm tra base64 hợp lệ", "Đạt", "artifact_input.py:22-31", "So khớp mã hóa lại (canonical); từ chối data-URI, thiếu padding."),
        ("Giới hạn kích thước file", "Không đạt", "ingest_helper.py:59-64", "File > max_file_size chỉ sinh cảnh báo, không chặn; không giới hạn body request."),
        ("Kiểm tra định dạng / MIME", "Đạt", "ingest_helper.py:35-57", "Từ chối thiếu đuôi, đuôi bị cấm, MIME không khớp."),
        ("Ràng buộc ký tự artifact/collection", "Không đạt", "ingest_router.py:88-101", "Chấp nhận '../', khoảng trắng – nguy cơ path traversal (đã xác nhận BB_TIEN_16)."),
        ("Kiểm tra URI đầu vào", "Không đạt", "artifact_input.py:85-89; uri_loader.py:91-105", "Không có validator; đường dẫn cục bộ được open() trực tiếp (xác nhận BB_TIEN_17)."),
        ("Mã HTTP trả về đúng ngữ nghĩa", "Đạt một phần", "global_handler.py:53-64; event_errors.py:176-195", "Validation trả 400 (docs 422); KeyError->413, ConnectionError->403."),
        ("Xác thực (auth) cho endpoint", "Đạt một phần", "ingest_router.py:34; auth.py:48-56", "Có Depends(authenticated) nhưng auth tắt mặc định, 1 secret chung."),
        ("Giải phóng tài nguyên (file tạm)", "Đạt", "ingest_service.py:125-149", "Xóa file tạm trong finally."),
        ("Sử dụng bộ nhớ với file lớn", "Không đạt", "artifact_input.py:28,80; ingest_service.py:122", "Giải mã base64 2 lần + read(): ~4x kích thước file."),
        ("Ghi log", "Đạt một phần", "ingest_router.py:29-30", "setLevel cứng; router không log; trộn f-string và %-format."),
        ("Trùng lặp mã / độ phức tạp", "Không đạt", "ingestion_scheduler.py:160-236 vs 294-394", "parse/store sao chép giữa 2 scheduler; docstring lỗi thời (ingest_router.py:477)."),
        ("Tương thích nền tảng", "Không đạt", "ingestion_scheduler.py:9; celery/bootsteps.py:1", "Import celery & fcntl vô điều kiện -> không chạy trên Windows bản core."),
        ("Unit test sẵn có bao phủ", "Đạt một phần", "tests/server/ingest/*", "Có happy path; thiếu test base64 sai, path traversal, URI cục bộ, auth."),
    ]),
    "VINH": ("private_gpt/server/ingest/ingest_router.py (list/delete), ingest_service.py, artifact_index/base_artifact_index.py, server/content/content_router.py, content_service.py, ui/index.html (renderDocuments, deleteDocument)", [
        ("Kiểm tra body xóa (bắt buộc, độ dài)", "Đạt", "ingest_router.py:320-333", "min 1 / max 255."),
        ("Kiểm tra tham số collection khi liệt kê", "Đạt một phần", "ingest_router.py:858-865", "Thiếu tham số bị chặn, nhưng không ràng buộc ký tự."),
        ("Ký tự đặc biệt / path trong collection", "Không đạt", "node_store_component.py:34; base_artifact_index.py:143", "Collection dùng làm đường dẫn/tên bảng không được làm sạch."),
        ("Xóa tài liệu không tồn tại trả 404", "Không đạt", "base_artifact_index.py:85-89", "ValueError -> 400 thay vì 404 (BB_VINH_06)."),
        ("Xóa 2 lần (idempotent)", "Không đạt", "base_artifact_index.py:141", "Trạng thái reset 'initialized' -> IndexNotReadyException -> HTTP 500 (BB_VINH_05)."),
        ("Collection không tồn tại", "Đạt một phần", "node_store_component.py:36-38", "Trả 200 data rỗng – không phân biệt gõ sai tên."),
        ("Nhất quán vector store / doc store khi xóa", "Đạt một phần", "base_artifact_index.py:121-143", "Không atomic; có TODO dòng 142."),
        ("Giới hạn nội dung trả về", "Đạt", "content_service.py:183,295,328,344", "20 artifact, 10.000 node, 50MB."),
        ("Phân trang khi liệt kê", "Không đạt", "ingest_service.py:181-203", "Không limit/offset; N+1 truy vấn; thứ tự set() không ổn định."),
        ("Lỗi logic vòng lặp liệt kê", "Không đạt", "ingest_service.py:187-188", "'return' thay vì 'continue' – một artifact rỗng làm mất các artifact sau."),
        ("Cô lập giữa các collection (multi-tenant)", "Không đạt", "context_filter.py:22-26", "Mọi caller đã xác thực đọc/xóa được mọi collection."),
        ("UI: chống XSS khi hiển thị tên file", "Đạt", "index.html:4958-4995", "Dùng textContent."),
        ("UI: trạng thái lập chỉ mục thực", "Không đạt", "index.html:4975", "status: 'Indexed' gán cứng cho mọi dòng."),
        ("Thông tin lỗi lộ chi tiết nội bộ", "Không đạt", "_errors.py:162-166", "Trả về exception.type/message của Python."),
        ("Unit test sẵn có bao phủ", "Đạt một phần", "tests/server/ingest/test_ingest_routes.py:272", "Thiếu test negative (không tồn tại, xóa 2 lần, cô lập)."),
    ]),
    "DUY": ("private_gpt/server/chat/chat_router.py, chat_models.py, chat_request_mapper.py, components/tools/builders/semantic_search_builder.py, tools/artifact_refs.py, components/engines/citations/*, ui/index.html (citation render)", [
        ("Từ chối messages/content rỗng", "Đạt", "chat_models.py:317-322", "400; nhưng chuỗi chỉ có khoảng trắng vẫn được chấp nhận."),
        ("Kiểm tra role hợp lệ", "Đạt", "input_models.py:366", "Literal."),
        ("Model bắt buộc", "Không đạt", "input_models.py:1293", "Tự gán 'default' dù schema ghi required (UT_MANH_02)."),
        ("Ràng buộc max_tokens", "Không đạt", "chat_models.py:100-106, 314-315", "≤0 bị bỏ qua âm thầm; không có cận trên so với context window."),
        ("semantic_search thiếu tool_context", "Đạt một phần", "semantic_search_processor.py:40-45", "Chỉ báo lỗi lúc chạy, model ChatBody không chặn (UT_DUY_05 Fail)."),
        ("Phạm vi truy xuất theo context_filter", "Đạt", "semantic_search_builder.py:147-153", "Lọc collection/artifacts/metadata."),
        ("Ngữ nghĩa artifacts: []", "Không đạt", "semantic_search_builder.py:102-104", "Danh sách rỗng = tìm toàn collection."),
        ("Bền vững với tham số tool do LLM sinh", "Không đạt", "tools/artifact_refs.py:70-84", "LLM truyền artifacts=[null] -> 'artifacts rejected, nothing was searched'; không fallback tìm toàn bộ."),
        ("Phân tích thẻ trích dẫn sai định dạng", "Đạt", "tests/engines/test_citation_parser_robustness.py", "19 test robustness."),
        ("Mã trích dẫn bịa đặt", "Đạt một phần", "citations/parser.py:70-75", "Mã bịa hoàn toàn để nguyên text '[XYZ9]' (UT_DUY_09)."),
        ("Chống giả mạo trích dẫn / prompt injection", "Không đạt", "citations/utils.py:186-197", "Text <citation ...> do model sinh được parse như thật; context không có delimiter dữ liệu không tin cậy."),
        ("Xử lý LLM backend lỗi / timeout", "Không đạt", "event_errors.py:165-167, 189-192", "Map theo type chính xác: ConnectionError->403, timeout->500."),
        ("Tràn context window (Ollama 4k)", "Không đạt", "semantic_search_builder.py:131,172-176", "top_k=32 + mở rộng chunk có thể chiếm hết cửa sổ."),
        ("Hiệu năng streaming trích dẫn", "Không đạt", "processors/events/citations/citations.py:58-64", "Mỗi delta parse lại toàn bộ text: O(n²)."),
        ("Độ phức tạp hàm validate", "Không đạt", "chat_models.py:290-400", "validate_properties ~140 dòng, có mã chết (335, 290-312)."),
    ]),
    "MANH": ("private_gpt/server/models/models_router.py, models_service.py, chat_router.py (count_tokens, validate), ui/index.html (chat sessions, Settings, model dropdown, API Debugger)", [
        ("Kiểm tra tham số phân trang /v1/models", "Đạt", "models_router.py:22-25", "limit 1..1000."),
        ("Model không tồn tại trả 404", "Không đạt", "llm_component.py:162; event_errors.py:177", "Trả 400 InvalidRequest."),
        ("count_tokens / validate", "Đạt", "chat_router.py:269-290", "Có test trong test_chat_routes.py."),
        ("URL mặc định khớp đặc tả", "Không đạt", "PRD.md:174; index.html:3986", "8001 vs 8080/origin (DOC-01)."),
        ("Test UI sẵn có khớp code", "Đạt", "tests/server/test_ui_mount.py:9; launcher.py:260", "Ban đầu nghi ngờ lỗi; chạy thực tế PASS (launcher thay chuỗi khi mount)."),
        ("Lưu thông tin xác thực an toàn", "Không đạt", "index.html:4075-4076, 4497", "Mật khẩu lưu plaintext localStorage (UI_MANH_11)."),
        ("API Debugger che secret", "Đạt", "index.html:8172-8176", "redactHeaders theo tên header; chưa che trong URL/body."),
        ("Validate Basic auth đủ cặp", "Đạt", "index.html:7713-7719", "Thiếu 1 trong 2 bị từ chối (UI_MANH_09)."),
        ("Validate Base URL", "Không đạt", "index.html:7723", "Lưu mọi chuỗi (UI_MANH_08)."),
        ("CRUD hội thoại theo PRD", "Đạt", "index.html:4518, 4699, 4716, 4656", "Có xác nhận khi xóa; rename rỗng -> 'New chat'."),
        ("Cắt tiêu đề dài", "Đạt", "index.html:392-399", "text-overflow: ellipsis."),
        ("Enter / Shift+Enter, IME tiếng Việt", "Đạt một phần", "index.html:7962-7966", "Không kiểm tra isComposing; Enter và nút Send kiểm tra điều kiện khác nhau."),
        ("Xử lý lỗi ghi localStorage", "Không đạt", "index.html:4497", "saveState không try/catch QuotaExceededError."),
        ("Phát hiện model mới không cần khởi động lại", "Không đạt", "models_service.py", "Model pull sau khi server chạy không xuất hiện (BB phát hiện 26/10)."),
        ("Khả năng bảo trì (kích thước file UI)", "Không đạt", "ui/index.html", "8.210 dòng, 320KB HTML+CSS+JS trong 1 file, không có unit test JS."),
    ]),
}
DATES = {"TIEN": "22/10/2026", "VINH": "23/10/2026", "DUY": "24/10/2026", "MANH": "25/10/2026"}
summary = []
for idx, (k, (files, items)) in enumerate(CODE.items(), start=5):
    n, msv, f = MEMBERS[k]
    ws = wb.create_sheet(f"{idx}. Review code {k.title()}")
    H = ["STT", "Tiêu chí review code", "Kết quả", "Vị trí (file:dòng)", "Nhận xét / bằng chứng", "Đề xuất", "Ngày"]
    title_block(ws, f"REVIEW CODE – {n.upper()} ({msv}) – {f}", "Phạm vi mã nguồn: " + files, len(H))
    header_row(ws, 4, H, [6, 36, 14, 34, 58, 36, 12])
    suggest = {
        "Không đạt": "Cần sửa – đã ghi nhận trong danh sách lỗi",
        "Đạt một phần": "Nên cải thiện",
        "Đạt": "–",
    }
    rows = [[i + 1, a, b, c_, d, suggest[b], DATES[k]] for i, (a, b, c_, d) in enumerate(items)]
    data_rows(ws, 5, rows, status_col=3, center_cols=(1, 3, 7))
    cnt = {s: sum(1 for x in items if x[1] == s) for s in ("Đạt", "Đạt một phần", "Không đạt")}
    summary.append((n, f, len(items), cnt["Đạt"], cnt["Đạt một phần"], cnt["Không đạt"]))

# ------------------------------------------------------------------ 9. Tổng hợp
ws = wb.create_sheet("9. Tong hop")
title_block(ws, "TỔNG HỢP KẾT QUẢ REVIEW", SUB, 7)
header_row(ws, 4, ["Hạng mục", "Phạm vi", "Tổng tiêu chí", "Đạt", "Đạt một phần", "Không đạt", "Tỉ lệ đạt"], [26, 46, 13, 10, 14, 12, 12])
doc_cnt = {s: sum(1 for x in CL if x[3] == s) for s in ("Đạt", "Đạt một phần", "Không đạt")}
rows = [("Review tài liệu đặc tả (nhóm)", "PRD.md, STYLE_GUIDE.md, docs, OpenAPI", len(CL), doc_cnt["Đạt"], doc_cnt["Đạt một phần"], doc_cnt["Không đạt"])]
rows += [(f"Review code – {s[0]}", s[1], *s[2:]) for s in summary]
rows = [list(x) + [f"=ROUND(D{5+i}/C{5+i}*100,1)&\"%\""] for i, x in enumerate(rows)]
end = data_rows(ws, 5, rows, center_cols=(3, 4, 5, 6, 7))
data_rows(ws, end, [["Tổng số lỗi tài liệu phát hiện", "Sheet '3. Loi tai lieu'", len(DOC_DEFECTS), "", "", "", ""]], center_cols=(3,))
ch = BarChart()
ch.type = "bar"
ch.grouping = "stacked"
ch.overlap = 100
ch.title = "Kết quả review theo hạng mục"
ch.add_data(Reference(ws, min_col=4, max_col=6, min_row=4, max_row=4 + len(rows)), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=1, min_row=5, max_row=4 + len(rows)))
ch.height, ch.width = 8, 22
ws.add_chart(ch, f"A{end + 3}")

wb.save(OUT)
print("saved", OUT)
