"""Sinh file Hướng dẫn demo & thuyết trình cho Nhóm 11."""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

OUT = Path(__file__).resolve().parents[3] / "HUONG_DAN_Demo_va_Thuyet_trinh_Nhom11.docx"
doc = Document()
st = doc.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(13)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
for s in ("Heading 1", "Heading 2", "Title"):
    doc.styles[s].font.name = "Times New Roman"
    doc.styles[s].font.color.rgb = RGBColor(0x1F, 0x38, 0x64)


def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:fill"), color)
    tcPr.append(sh)


def table(rows):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            c = t.cell(i, j)
            c.text = str(v)
            for p in c.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(11)
                    if i == 0:
                        r.bold = True
            if i == 0:
                shade(c, "DDEBF7")
    doc.add_paragraph()


def bullets(items, style="List Bullet"):
    for it in items:
        doc.add_paragraph(it, style=style)


t = doc.add_paragraph("HƯỚNG DẪN DEMO & THUYẾT TRÌNH – NHÓM 11", style="Title")
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph("Đề tài: Kiểm thử ứng dụng RAG (PrivateGPT) – Môn Đảm bảo chất lượng phần mềm").alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_heading("1. Những gì cần biết", 1)
table([
    ["Thứ", "Ở đâu"],
    ["Shortcut demo", "Desktop › “DEMO Nhom 11 - RAG” (nhấn đúp là chạy)"],
    ["Slide thuyết trình", "https://claude.ai/artifact/KvsUK16oTMJfcz665FCgMw (mục 8 trong menu demo). Tải .pptx/PDF: Share › Export"],
    ["File nộp cho thầy", "Thư mục NOP_BAI_Nhom11 (mục 7 trong menu demo)"],
    ["Giao diện hệ thống", "http://localhost:8080/ui"],
    ["Tài liệu API (Swagger)", "http://localhost:8080/docs"],
])

doc.add_heading("2. Chuẩn bị trước buổi thuyết trình (trước 20–30 phút)", 1)
bullets([
    "Cắm sạc máy (mô hình AI chạy bằng CPU, tốn pin). Không cần Internet – mọi thứ chạy cục bộ (riêng slide cần mạng; nên tải sẵn bản .pptx/PDF dự phòng).",
    "Nhấn đúp shortcut “DEMO Nhom 11 - RAG”. Cửa sổ sẽ tự bật Ollama → Qdrant → PrivateGPT. Lần đầu mất 1–3 phút; khi cả 3 dòng báo SẴN SÀNG là xong. Hai cửa sổ thu nhỏ (Qdrant, PrivateGPT) KHÔNG được tắt.",
    "Chọn 2 một lần để “làm nóng” mô hình (câu hỏi đầu tiên luôn chậm nhất). Sau đó các câu hỏi khác nhanh hơn.",
    "Chọn 1 để mở giao diện. Nếu hiện màn hình Onboarding: giữ URL http://localhost:8080, ô Collection nhập nhom11, bấm “Save and check”, rồi “Finish setup” (hoặc bỏ qua bước 2).",
    "Trong giao diện: vào Context › Documents › bấm Refresh để thấy danh sách tài liệu (bắt buộc – nếu không, chat sẽ không dùng tài liệu; đây chính là lỗi BUG-25 nhóm phát hiện).",
    "Mở sẵn: slide, file 02_KetQua_KiemThu_Nhom11.xlsx (sheet “11. Tong hop” và “7. Bao cao loi”), báo cáo BTLSo1.pdf.",
])

doc.add_heading("3. Kịch bản thuyết trình (~15 phút, 17 slide)", 1)
doc.add_paragraph("Mỗi slide có sẵn lời gợi ý trong phần ghi chú (bấm Present để xem). Phân chia người nói gợi ý:")
table([
    ["Slide", "Nội dung", "Người trình bày", "Thời lượng"],
    ["1–3", "Giới thiệu, thành viên, vì sao chọn PrivateGPT", "Nguyễn Minh Tiến", "2 phút"],
    ["4–5", "Luồng RAG; cài đặt và 6 lỗi môi trường Windows", "Bùi Văn Mạnh", "1,5 phút"],
    ["6–7", "Review tài liệu (25 tiêu chí, 16 lỗi) và review code", "Nguyễn Bá Quang Vinh", "2 phút"],
    ["8–9", "Chiến lược kiểm thử; kết quả 143 TC, 113 Pass, 25 lỗi", "Vũ Đức Duy", "1,5 phút"],
    ["10", "Kết quả chức năng Nạp tài liệu", "Nguyễn Minh Tiến", "1,5 phút"],
    ["11", "Kết quả chức năng Quản lý tài liệu", "Nguyễn Bá Quang Vinh", "1,5 phút"],
    ["12", "Kết quả chức năng Hỏi đáp RAG", "Vũ Đức Duy", "1,5 phút"],
    ["13", "Kết quả chức năng Hội thoại & cấu hình", "Bùi Văn Mạnh", "1,5 phút"],
    ["14–16", "Hiệu năng, 5 lỗi nghiêm trọng, kết luận & bài học", "Nguyễn Minh Tiến", "2 phút"],
    ["17", "Cảm ơn → chuyển sang demo", "Cả nhóm", "–"],
])
doc.add_paragraph("Ý chính cần nhấn mạnh:")
bullets([
    "Hệ thống thật, nhiều sao (57,6 nghìn sao GitHub), không phải đồ án tự viết; mọi kết quả đều chạy thật, có log và ảnh minh chứng.",
    "Ngoài kiểm thử phần mềm truyền thống, nhóm đánh giá chất lượng AI: trả lời đúng, không bịa, trích dẫn đúng nguồn, chống prompt injection.",
    "Lỗi giá trị nhất: nạp đồng thời làm mất tài liệu (BUG-01), đọc file hệ thống qua URI (BUG-02), giao diện tự tắt Documents (BUG-25).",
    "Bài học: đổi mô hình (llama3.2 → qwen2.5) là đổi hẳn kết quả; CI chỉ chạy Ubuntu nên bỏ sót lỗi Windows.",
])

doc.add_heading("4. Kịch bản demo (~6–8 phút) – dùng menu của shortcut", 1)
table([
    ["Bước", "Chọn", "Làm gì / nói gì", "Thời gian"],
    ["1", "1", "Mở giao diện. Vào Context › Documents › Refresh: chỉ các tài liệu đã nạp (.md, .txt, .docx, .pdf). New Chat, hỏi: “Phòng máy chủ của công ty Sao Mai đặt ở tầng mấy?” → đáp án đúng: tầng 7. Nếu bong bóng trả lời bị trống hoặc trả lời “không có thông tin”, đó chính là lỗi nhóm đã ghi nhận (UI_DUY_01, BUG-25) – nói điều này rồi chuyển sang bước 2 (API) để thấy RAG trả lời đúng. Mở API Debugger cho thầy xem request semantic_search.", "2–3 phút"],
    ["2", "2", "Demo RAG qua API: nạp tài liệu mới → liệt kê → hỏi “đi muộn quá 15 phút bị phạt bao nhiêu?” → đáp án 50.000 đồng. Lưu ý: mô hình hay trả lời tiếng Anh – đúng lỗi BUG-18 nhóm đã ghi nhận.", "1–1,5 phút"],
    ["3", "5", "Test giao diện tự động: Edge tự mở, tự tạo/đổi tên chat, gõ Shift+Enter, nhập Base URL sai “abc xyz” và vẫn được lưu (lỗi BUG-21).", "1 phút"],
    ["4", "4", "Test hộp đen API 12 case: chỉ ra BB_TIEN_17 Fail – hệ thống đọc được C:\\Windows\\win.ini (lỗ hổng bảo mật BUG-02).", "1 phút"],
    ["5", "6", "Nạp đồng thời 6 tài liệu → chỉ còn 1 trong danh sách: lỗi mất dữ liệu BUG-01.", "1 phút"],
    ["6", "3", "(Nếu còn thời gian) Unit test pytest: 39/40 pass, ca UT_DUY_05 fail là phát hiện thật.", "~1 phút"],
    ["7", "7", "Mở thư mục nộp bài, mở file Excel kết quả kiểm thử, sheet Tổng hợp & Báo cáo lỗi.", "30 giây"],
])
doc.add_paragraph("Mẹo: nếu thời gian ít, chỉ demo bước 1, 2 và 5. Bước 2 và câu hỏi trên giao diện mất 30–90 giây/câu vì mô hình chạy CPU – trong lúc chờ hãy giải thích luồng RAG trên slide 4.")

doc.add_heading("5. Xử lý sự cố khi demo", 1)
table([
    ["Hiện tượng", "Cách xử lý"],
    ["Menu báo “CHƯA SẴN SÀNG”", "Chọn 9 (khởi động lại hệ thống) và chờ 1–3 phút."],
    ["Chat trả lời “không có thông tin”", "Vào Context › Documents › Refresh rồi tạo New Chat và hỏi lại (lỗi BUG-25)."],
    ["Dropdown hiện “No models”", "Bấm nút làm mới (biểu tượng ↻) cạnh dropdown, chờ vài giây."],
    ["Câu trả lời quá lâu (> 2 phút)", "Bình thường với CPU; chuyển sang giải thích slide, hoặc dùng ảnh minh chứng trong thư mục screenshots."],
    ["Lỡ đóng cửa sổ PrivateGPT", "Mở lại shortcut, hệ thống sẽ tự bật lại phần bị tắt."],
    ["Không mở được slide (mất mạng)", "Dùng file .pptx/PDF đã tải trước (Share › Export)."],
])
doc.add_paragraph("Sau buổi demo: chọn 0 để tắt hệ thống (giải phóng RAM).")

doc.add_heading("6. Câu hỏi thầy có thể hỏi – gợi ý trả lời", 1)
QA = [
    ("Vì sao chọn PrivateGPT?", "Nằm trong nhóm dự án RAG nhiều sao nhất (57,6 nghìn), có cả API và giao diện, có tài liệu PRD để review, có bộ test sẵn để đánh giá hiện trạng, chạy được trên máy 16GB không GPU (RAGFlow cần nhiều tài nguyên hơn)."),
    ("Kiểm thử ứng dụng RAG khác gì phần mềm thường?", "Kết quả của AI không xác định (non-deterministic): phải có bộ câu hỏi có đáp án biết trước, chấm tự động rồi người xem lại; phải kiểm thử thêm hallucination, trích dẫn, prompt injection, ngôn ngữ và sự phụ thuộc vào mô hình."),
    ("Các nhóm có sửa mã nguồn không?", "Không sửa dòng nào của dự án. Chỉ xử lý môi trường (cài thêm gói, biến môi trường, chạy Qdrant ở chế độ server) để chạy được trên Windows và ghi lại thành lỗi ENV-01..06."),
    ("Kỹ thuật thiết kế test case đã dùng?", "Phân hoạch tương đương, phân tích giá trị biên (độ dài 0/255/256, temperature 0/1/1,5), bảng quyết định (câu hỏi theo từng định dạng tài liệu), đoán lỗi (xóa 2 lần, MIME giả), kiểm thử bảo mật, hiệu năng và đồng thời."),
    ("Kiểm thử tự động thế nào?", "Unit test bằng pytest; test API bằng httpx; test giao diện bằng Playwright điều khiển Microsoft Edge, có chụp ảnh; kết quả xuất JSON/JUnit XML rồi sinh file Excel tự động."),
    ("Ứng dụng AI vào kiểm thử ở đâu?", "Dùng trợ lý AI (Claude) để đọc nhanh mã nguồn, gợi ý tiêu chí review, sinh khung test case; mọi kết quả đều được nhóm chạy lại và kiểm chứng (ví dụ: AI nghi lỗi test_ui_mount nhưng chạy thực tế pass nên nhóm gỡ lỗi đó)."),
    ("Lỗi nghiêm trọng nhất là gì, tái hiện thế nào?", "BUG-01: gửi song song 6 request nạp tài liệu → chỉ 1/6 còn trong danh sách. Tái hiện bằng mục 6 trong menu demo (script concurrency_ingest_test.py)."),
    ("Tỉ lệ pass 79% nói lên điều gì?", "Luồng chính hoạt động tốt; các ca fail tập trung ở nhánh ngoại lệ, bảo mật đầu vào, đồng thời và chất lượng AI – đúng những chỗ bộ test sẵn có của dự án chưa bao phủ."),
]
for q, a in QA:
    p = doc.add_paragraph()
    r = p.add_run("Hỏi: " + q)
    r.bold = True
    doc.add_paragraph("Đáp: " + a)

doc.save(OUT)
print("saved", OUT)
