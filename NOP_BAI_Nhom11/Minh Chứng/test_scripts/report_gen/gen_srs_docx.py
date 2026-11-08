"""Sinh tài liệu đặc tả yêu cầu bổ sung (use case + NFR) cho 4 chức năng được kiểm thử."""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

OUT = Path(__file__).resolve().parents[2] / "DacTa_YeuCau_BoSung_Nhom11.docx"
doc = Document()
st = doc.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(13)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
for s in ("Heading 1", "Heading 2", "Heading 3", "Title"):
    doc.styles[s].font.name = "Times New Roman"
    doc.styles[s].font.color.rgb = RGBColor(0x1F, 0x38, 0x64)


def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), color)
    tcPr.append(sh)


def table(rows, header=True, widths=None):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            cell = t.cell(i, j)
            cell.text = str(v)
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(11)
                    if header and i == 0:
                        r.bold = True
                        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            if header and i == 0:
                shade(cell, "2E75B6")
    doc.add_paragraph()
    return t


t = doc.add_paragraph("TÀI LIỆU ĐẶC TẢ YÊU CẦU BỔ SUNG", style="Title")
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
p = doc.add_paragraph("Hệ thống: PrivateGPT v1.0.1 (Workbench + API) – Nhóm 11 – Môn Đảm bảo chất lượng phần mềm")
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
table([
    ["Phiên bản", "Ngày", "Người thực hiện", "Nội dung"],
    ["0.1", "18/10/2026", "Cả nhóm", "Khởi tạo khung tài liệu từ PRD.md, STYLE_GUIDE.md, tài liệu API"],
    ["0.2", "22/10/2026", "Tiến, Vinh, Duy, Mạnh", "Bổ sung use case & mã yêu cầu cho 4 chức năng"],
    ["1.0", "25/10/2026", "Nguyễn Minh Tiến", "Bổ sung yêu cầu phi chức năng, chốt sau buổi review"],
])

doc.add_heading("1. Mục đích và phạm vi", 1)
doc.add_paragraph(
    "Tài liệu gốc của PrivateGPT (ui/docs/PRD.md, STYLE_GUIDE.md và fern/docs) mô tả sản phẩm ở mức tổng quan, "
    "chưa có mã định danh yêu cầu, chưa có đặc tả use case và hoàn toàn thiếu yêu cầu phi chức năng (lỗi DOC-06, DOC-13). "
    "Nhóm 11 lập tài liệu này để (1) làm cơ sở thiết kế test case, (2) truy vết yêu cầu – test case, "
    "(3) đề xuất bổ sung cho dự án gốc. Phạm vi gồm 4 chức năng được phân công kiểm thử.")
table([
    ["Mã", "Chức năng", "Phụ trách"],
    ["UC01", "Nạp tài liệu (upload & lập chỉ mục)", "Nguyễn Minh Tiến – B22DVCN308"],
    ["UC02", "Quản lý tài liệu (liệt kê, xem nội dung, xóa)", "Nguyễn Bá Quang Vinh – B22DVCN348"],
    ["UC03", "Hỏi đáp RAG có trích dẫn nguồn", "Vũ Đức Duy – B22DVCN397"],
    ["UC04", "Quản lý hội thoại, mô hình & cấu hình", "Bùi Văn Mạnh – B22DVCN212"],
])

doc.add_heading("2. Tổng quan hệ thống", 1)
doc.add_paragraph(
    "PrivateGPT là lớp API mã nguồn mở (Python/FastAPI, LlamaIndex) biến mô hình ngôn ngữ chạy cục bộ thành ứng dụng AI. "
    "Luồng RAG: tài liệu được phân tích (parse), chia đoạn (chunk), tạo vector nhúng (embedding) và lưu vào Qdrant; "
    "khi người dùng hỏi, LLM gọi công cụ semantic_search để truy xuất các đoạn liên quan rồi sinh câu trả lời có trích dẫn. "
    "Giao diện Workbench (ui/index.html) là một trang tĩnh lưu trạng thái trong localStorage.")
table([
    ["Thành phần", "Công nghệ (môi trường kiểm thử của nhóm)"],
    ["API server", "PrivateGPT 1.0.1 – FastAPI/Uvicorn, Python 3.11, cổng 8080"],
    ["Giao diện", "Workbench – HTML/CSS/JS thuần, /ui"],
    ["LLM", "Ollama 0.40.15 – qwen2.5:3b (mặc định), llama3.2:3b (đối chứng)"],
    ["Embedding", "nomic-embed-text (768 chiều) qua Ollama"],
    ["Vector store", "Qdrant 1.20.0 (chế độ server, cổng 6333)"],
    ["Lưu trữ metadata", "SQLite (local_data)"],
])

doc.add_heading("3. Đặc tả use case", 1)
UCS = [
    ("UC01 – Nạp tài liệu", "Người dùng (Workbench) / Ứng dụng client (API)",
     "Server đang chạy; collection đã cấu hình trong Settings",
     ["Người dùng mở Context > Documents và bấm Upload.", "Chọn một hoặc nhiều file.",
      "Hệ thống mã hóa base64, gửi POST /v1/artifacts/ingest với artifact = tên file + timestamp.",
      "Server kiểm tra kích thước, phần mở rộng, MIME; phân tích, chia đoạn, tạo embedding, lưu Qdrant.",
      "Hệ thống thông báo thành công và hiển thị tài liệu trong danh sách."],
     ["3a. File rỗng/định dạng bị cấm/MIME không khớp → HTTP 400, hiển thị thông báo lỗi.",
      "3b. artifact/collection sai độ dài (0 hoặc >255) → HTTP 400.",
      "4a. Nạp lại cùng artifact → ghi đè nội dung cũ (đề xuất trả về thông tin tài liệu)."],
     "Tài liệu ở trạng thái populated, xuất hiện trong /v1/artifacts/list"),
    ("UC02 – Quản lý tài liệu", "Người dùng",
     "Đã có tài liệu trong collection",
     ["Người dùng mở Context > Documents, bấm Refresh.", "Hệ thống gọi GET /v1/artifacts/list?collection=.",
      "Hiển thị mỗi tài liệu: tên, artifact · collection, badge loại file, trạng thái.",
      "Người dùng bấm Delete → hộp xác nhận → OK.", "Hệ thống gọi POST /v1/artifacts/delete, xóa vector & metadata, cập nhật danh sách."],
     ["4a. Người dùng bấm Cancel → không xóa.", "5a. Tài liệu không tồn tại → đề xuất HTTP 404.",
      "5b. Xóa lần 2 → đề xuất HTTP 404 (idempotent), không được lỗi 500."],
     "Tài liệu không còn trong danh sách và không còn được truy xuất khi hỏi đáp"),
    ("UC03 – Hỏi đáp RAG có trích dẫn", "Người dùng",
     "Có tài liệu trong collection; chat bật Documents; LLM hỗ trợ tool calling",
     ["Người dùng nhập câu hỏi và nhấn Enter/Send.",
      "Hệ thống gửi POST /v1/messages kèm tool semantic_search và tool_context (collection).",
      "LLM gọi semantic_search; server truy xuất top-k đoạn liên quan (ngưỡng tương đồng 0,4).",
      "LLM sinh câu trả lời, gắn mã trích dẫn [ID]; server chuyển thành thẻ <citation>.",
      "Giao diện hiển thị câu trả lời Markdown, nút số trích dẫn; bấm vào mở popup đoạn nguồn."],
     ["3a. Không có đoạn liên quan → trả lời 'không tìm thấy thông tin' (không bịa).",
      "2a. Thiếu tool_context → HTTP 400.", "3b. LLM backend lỗi → đề xuất HTTP 503 với thông báo rõ ràng."],
     "Câu trả lời trung thực với tài liệu, có trích dẫn trỏ đúng tài liệu nguồn"),
    ("UC04 – Hội thoại, mô hình & cấu hình", "Người dùng",
     "Workbench đã qua onboarding",
     ["Người dùng bấm New Chat → tạo hội thoại 'New chat'.", "Chọn mô hình trong dropdown (GET /v1/models).",
      "Đổi tên / xóa / chuyển hội thoại trên sidebar; dữ liệu lưu localStorage.",
      "Vào Settings cấu hình Base URL, Basic auth, system prompt, collection, Save / Test API.",
      "Xem API Debugger: các request/response với header xác thực đã được che."],
     ["4a. Base URL sai định dạng → đề xuất báo lỗi, không lưu.", "4b. Chỉ nhập username hoặc password → báo lỗi.",
      "2a. Model không tồn tại → đề xuất HTTP 404."],
     "Hội thoại và cấu hình được lưu, khôi phục sau khi tải lại trang"),
]
for name, actor, pre, main, alt, post in UCS:
    doc.add_heading(name, 2)
    table([["Thuộc tính", "Mô tả"], ["Tác nhân", actor], ["Tiền điều kiện", pre],
           ["Luồng chính", "\n".join(f"{i+1}. {s}" for i, s in enumerate(main))],
           ["Luồng thay thế / ngoại lệ", "\n".join(alt)], ["Hậu điều kiện", post]])

doc.add_heading("4. Danh sách yêu cầu chức năng (có mã truy vết)", 1)
table([
    ["Mã YC", "Mô tả", "Nguồn", "Test case liên quan"],
    ["REQ-ING-01", "Nạp file qua API/UI, trả về thông tin tài liệu", "PRD MVP#8", "BB_TIEN_01-05, UI_TIEN_03-04"],
    ["REQ-ING-02", "Kiểm tra dữ liệu đầu vào (base64, độ dài, type, file rỗng)", "OpenAPI", "BB_TIEN_06-12, UT_TIEN_01-10"],
    ["REQ-ING-03", "Từ chối định dạng bị cấm và MIME giả", "ingestion.mdx", "BB_TIEN_13-14, UI_TIEN_05"],
    ["REQ-ING-04 (bổ sung)", "Từ chối artifact/collection chứa ký tự đường dẫn; URI chỉ http(s)/s3", "Nhóm đề xuất", "BB_TIEN_16-17, UT_TIEN_12-13"],
    ["REQ-DOC-01", "Liệt kê tài liệu theo collection", "PRD MVP#9", "BB_VINH_01-03, UI_VINH_01-02"],
    ["REQ-DOC-02", "Xóa tài liệu có xác nhận, nhất quán vector store", "PRD 499", "BB_VINH_04-09, UI_VINH_03-04"],
    ["REQ-DOC-03", "Xem nội dung tài liệu", "PRD 501", "BB_VINH_10-13"],
    ["REQ-DOC-04", "Cô lập dữ liệu giữa các collection", "PRD 503", "BB_VINH_14-16"],
    ["REQ-RAG-01", "Trả lời đúng theo tài liệu (.md/.txt/.docx/.pdf)", "PRD MVP#10-11", "BB_DUY_01-05, UI_DUY_01"],
    ["REQ-RAG-02 (bổ sung)", "Không bịa khi tài liệu không có thông tin; tuân thủ phạm vi truy xuất", "Nhóm đề xuất", "BB_DUY_06-07, BB_DUY_12"],
    ["REQ-RAG-03", "Trích dẫn nguồn inline, bật/tắt được", "PRD 778-795", "BB_DUY_08-09, UI_DUY_03-04"],
    ["REQ-RAG-04 (bổ sung)", "Chống prompt injection gián tiếp; trả lời đúng ngôn ngữ câu hỏi", "Nhóm đề xuất", "BB_DUY_13-14"],
    ["REQ-SES-01", "CRUD hội thoại, lưu sau reload", "PRD MVP#4-6", "UI_MANH_01-05"],
    ["REQ-SES-02", "Danh sách & chọn mô hình", "PRD MVP#3", "BB_MANH_01-05, UI_MANH_06"],
    ["REQ-SES-03", "Hội thoại nhiều lượt, streaming, system prompt, tham số sinh", "API messages", "BB_MANH_08-15, UT_MANH_01-09"],
    ["REQ-SES-04", "Settings: validate URL, Basic auth, che secret trong Debugger", "PRD 395-419, 903", "UI_MANH_08-11"],
])

doc.add_heading("5. Yêu cầu phi chức năng (nhóm đề xuất bổ sung)", 1)
table([
    ["Mã", "Yêu cầu", "Chỉ tiêu đo", "Kiểm chứng"],
    ["NFR-01", "Thời gian nạp tài liệu nhỏ (< 100KB)", "≤ 30 giây trên CPU 4 nhân", "BB_TIEN_01-05, PERF"],
    ["NFR-02", "Nạp file lớn", "File 2,7MB ≤ 120 giây; giới hạn cứng 25MB", "BB_TIEN_18"],
    ["NFR-03", "Thời gian phản hồi hỏi đáp RAG", "Trung vị ≤ 60 giây (CPU, model 3B)", "PERF_RAG"],
    ["NFR-04", "API liệt kê tài liệu dưới tải", "20 request đồng thời, p95 ≤ 2 giây, 0% lỗi", "PERF_LIST"],
    ["NFR-05", "Bảo mật đầu vào", "Từ chối 100% tên chứa '../', URI cục bộ", "BB_TIEN_16-17, BB_VINH_16"],
    ["NFR-06", "Không lưu mật khẩu dạng rõ phía trình duyệt", "Không có plaintext trong localStorage", "UI_MANH_11"],
    ["NFR-07", "Tương thích nền tảng", "Cài đặt theo tài liệu chạy được trên Windows 10/11", "ENV-01..05"],
    ["NFR-08", "Giao diện responsive", "Không cuộn ngang ở 375px", "UI_MANH_12"],
])
doc.save(OUT)
print("saved", OUT)
