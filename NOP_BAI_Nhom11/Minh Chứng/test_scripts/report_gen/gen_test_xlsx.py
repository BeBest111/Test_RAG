"""Sinh 02_KetQua_KiemThu_Nhom11.xlsx từ kết quả chạy thật (logs/*.json, *.xml)."""

import json
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.drawing.image import Image as XLImage

from bugs import BUGS, ENV_BUGS
from xlsx_style import MEMBERS, data_rows, header_row, kv_table, section, title_block

ROOT = Path(__file__).resolve().parents[3]
LOGS = ROOT / "03_MinhChung" / "logs"
SHOTS = ROOT / "03_MinhChung" / "screenshots"
OUT = ROOT / "02_KetQua_KiemThu_Nhom11.xlsx"
SUB = "Nhóm 11 – PrivateGPT v1.0.1 – Môi trường: Windows 10 Pro, Python 3.11.9, Ollama (qwen2.5:3b, nomic-embed-text), Qdrant 1.20 – Thực hiện 29/10/2026 – 04/11/2026"

bb = json.loads((LOGS / "blackbox_results.json").read_text(encoding="utf-8"))
ui = json.loads((LOGS / "ui_results.json").read_text(encoding="utf-8"))
perf = json.loads((LOGS / "perf_results.json").read_text(encoding="utf-8")) if (LOGS / "perf_results.json").exists() else []

# Unit test (JUnit XML)
unit = {}
for tcase in ET.parse(LOGS / "unit_nhom11.xml").getroot().iter("testcase"):
    name = tcase.get("name")
    failed = tcase.find("failure") is not None or tcase.find("error") is not None
    msg = ""
    f = tcase.find("failure")
    if f is not None:
        msg = (f.get("message") or "")[:200]
    unit[name] = (not failed, float(tcase.get("time", 0)), msg)

repo_total = repo_fail = 0
repo_fail_names = []
for tcase in ET.parse(LOGS / "repo_unit_tests.xml").getroot().iter("testcase"):
    repo_total += 1
    if tcase.find("failure") is not None or tcase.find("error") is not None:
        repo_fail += 1
        repo_fail_names.append(tcase.get("name"))

UNIT_DESC = {
    "TIEN": {
        "01": ("_is_valid_base64 với chuỗi base64 hợp lệ", "b64('Xin chào RAG')", "True"),
        "02": ("_is_valid_base64 với chuỗi rỗng (biên)", "''", "False"),
        "03": ("_is_valid_base64 với ký tự không hợp lệ", "'@@@###'", "False"),
        "04": ("_is_valid_base64 thiếu padding/có khoảng trắng", "'YWJj ZA'", "False"),
        "05": ("_is_valid_base64 với data-URI", "'data:text/plain;base64,...'", "False"),
        "06": ("IngestBody dùng collection mặc định", "không truyền collection", "collection = 'pgpt_collection'"),
        "07": ("IngestBody artifact rỗng", "artifact=''", "ValidationError"),
        "08": ("IngestBody artifact 255 ký tự (biên trên)", "'a'*255", "Hợp lệ"),
        "09": ("IngestBody artifact 256 ký tự (vượt biên)", "'a'*256", "ValidationError"),
        "10": ("IngestBody type không hỗ trợ", "type='video'", "ValidationError"),
        "11": ("FileArtifact giải mã đúng UTF-8", "b64('Nội dung tiếng Việt')", "Bytes giải mã khớp nội dung gốc"),
        "12": ("IngestBody chấp nhận '../' (ghi nhận lỗ hổng)", "artifact='../../etc/passwd'", "Ghi nhận hành vi thực tế: được chấp nhận"),
        "13": ("_is_valid_uri phân biệt URL/đường dẫn cục bộ", "https://..., C:\\Windows\\win.ini", "True / False"),
    },
    "VINH": {
        "01": ("DeleteIngestedDocumentBody hợp lệ", "collection=c1, artifact=a1", "Tạo được đối tượng"),
        "02": ("Thiếu collection", "chỉ artifact", "ValidationError"),
        "03": ("collection rỗng (biên dưới)", "collection=''", "ValidationError"),
        "04": ("artifact rỗng", "artifact=''", "ValidationError"),
        "05": ("artifact 255 ký tự (biên trên)", "'x'*255", "Hợp lệ"),
        "06": ("artifact 256 ký tự", "'x'*256", "ValidationError"),
        "07": ("artifact sai kiểu dữ liệu", "artifact=['a']", "ValidationError"),
        "08": ("collection '../x' (ghi nhận lỗ hổng)", "collection='../x'", "Ghi nhận: được chấp nhận"),
    },
    "DUY": {
        "01": ("ChatBody RAG hợp lệ", "tools + tool_context + citations", "Tạo được đối tượng"),
        "02": ("messages rỗng", "messages=[]", "ValidationError"),
        "03": ("content rỗng", "content=''", "ValidationError"),
        "04": ("role không hợp lệ", "role='hacker'", "ValidationError"),
        "05": ("semantic_search thiếu tool_context", "tools=[semantic_search]", "ValidationError/ValueError"),
        "06": ("Chuyển [AB12] thành thẻ citation", "'Câu trả lời [AB12].'", "1 citation, đúng format"),
        "07": ("Citation không phân biệt hoa thường", "'[ab12]'", "1 citation"),
        "08": ("Loại mã trích dẫn bịa trong danh sách", "'[ZZ99, AB12]'", "Chỉ giữ AB12"),
        "09": ("Mã trích dẫn bịa hoàn toàn", "'[ZZ99]'", "0 citation (ghi nhận: text thô còn lại)"),
        "10": ("Trích dẫn lặp giữ cùng index", "'[AB12] ... [AB12]'", "index = 0, 0"),
    },
    "MANH": {
        "01": ("Hội thoại 5 lượt hợp lệ", "11 messages", "Tạo được, đủ 11 messages"),
        "02": ("Thiếu model -> mặc định", "không truyền model", "Ghi nhận: model='default'"),
        "03": ("temperature = 0.0 (biên dưới)", "0.0", "Hợp lệ"),
        "04": ("temperature = 1.0 (biên trên)", "1.0", "Hợp lệ"),
        "05": ("temperature = 1.5 (vượt biên)", "1.5", "ValidationError"),
        "06": ("temperature = -0.1 (dưới biên)", "-0.1", "ValidationError"),
        "07": ("top_p = 1.01", "1.01", "ValidationError"),
        "08": ("Tin nhắn cuối có role system", "role='system'", "ValidationError"),
        "09": ("max_tokens = 0", "0", "Ghi nhận: bị bỏ qua (None)"),
    },
}

DATES = {"UI": "29/10/2026", "UT": "31/10/2026", "BB": "01/11/2026", "PERF": "03/11/2026"}
DATE2 = {"DUY": "02/11/2026", "MANH": "02/11/2026"}

bug_by_tc = {}
for b in BUGS + ENV_BUGS:
    for t in b["tcs"]:
        bug_by_tc.setdefault(t, []).append(b["id"])

wb = Workbook()
# ------------------------------------------------------------ 1. Kế hoạch kiểm thử
ws = wb.active
ws.title = "1. Ke hoach kiem thu"
title_block(ws, "KẾ HOẠCH KIỂM THỬ (TEST PLAN) – NHÓM 11", SUB, 2)
r = kv_table(ws, 4, [
    ("Mục tiêu", "Đánh giá chất lượng 4 chức năng cốt lõi của ứng dụng RAG PrivateGPT; phát hiện lỗi chức năng, giao diện, bảo mật, hiệu năng và độ tin cậy của câu trả lời."),
    ("Phạm vi", "UC01 Nạp tài liệu (Tiến) – UC02 Quản lý tài liệu (Vinh) – UC03 Hỏi đáp RAG có trích dẫn (Duy) – UC04 Hội thoại, mô hình & cấu hình (Mạnh). Ngoài phạm vi: Databases, MCP, Skills, Custom Tools, Code Execution."),
    ("Mức / loại kiểm thử", "Kiểm thử giao diện (Playwright tự động + quan sát), kiểm thử đơn vị (pytest, white-box), kiểm thử hộp đen API (EP, BVA, bảng quyết định, đoán lỗi), kiểm thử bảo mật cơ bản, kiểm thử hiệu năng (tải đồng thời), chạy lại bộ test có sẵn của dự án."),
    ("Công cụ", "pytest 9.2, Playwright 1.x + Microsoft Edge (headless), httpx, openpyxl; Claude (AI) hỗ trợ sinh test case/đọc mã; Ollama; Qdrant."),
    ("Môi trường", "Windows 10 Pro 22H2, CPU (không GPU), RAM 16GB; Python 3.11.9; PrivateGPT commit 42ce052; Ollama 0.40.15: qwen2.5:3b (LLM), llama3.2:3b (đối chứng), nomic-embed-text (embedding 768); Qdrant 1.20.0 server."),
    ("Dữ liệu kiểm thử", "6 tài liệu giả lập công ty 'Sao Mai' (.md, .txt, .docx, .pdf, FAQ tiếng Anh), file rỗng, file 2,7MB, file zip, PNG giả mạo – thư mục 03_MinhChung/test_data."),
    ("Tiêu chí bắt đầu", "Hệ thống khởi động được, /health trả 'ok', có ≥ 1 LLM và 1 model embedding."),
    ("Tiêu chí kết thúc", "100% test case đã thực thi; mọi lỗi mức Cao được ghi nhận kèm minh chứng; có báo cáo tổng hợp."),
    ("Rủi ro", "LLM chạy CPU chậm (30-120s/câu); model nhỏ cho kết quả không ổn định (non-deterministic) -> mỗi case RAG chạy lại khi nghi ngờ; ổ đĩa còn ít dung lượng."),
])
r = section(ws, r + 1, "LỊCH THỰC HIỆN", 2)
r = kv_table(ws, r, [
    ("15/10 – 16/10/2026", "Chọn chủ đề, chọn hệ thống PrivateGPT trên GitHub, phân công chức năng"),
    ("16/10 – 17/10/2026", "Cài đặt môi trường, phát hiện và xử lý 6 lỗi môi trường Windows (ENV-01..06)"),
    ("18/10 – 23/10/2026", "Review tài liệu đặc tả theo checklist (cả nhóm), viết đặc tả bổ sung"),
    ("22/10 – 25/10/2026", "Review code chức năng cá nhân"),
    ("26/10 – 28/10/2026", "Thiết kế test case (UI, unit, hộp đen, hiệu năng)"),
    ("29/10 – 03/11/2026", "Thực thi kiểm thử, ghi nhận kết quả & lỗi"),
    ("04/11 – 06/11/2026", "Kiểm thử hồi quy, tổng hợp báo cáo, slide thuyết trình"),
])

# ------------------------------------------------------------ 2. Lỗi môi trường
ws = wb.create_sheet("2. Cai dat & loi moi truong")
H = ["Mã", "Hiện tượng", "Nguyên nhân (mã nguồn)", "Mức độ", "Cách xử lý của nhóm (không sửa mã nguồn gốc)", "Ngày"]
title_block(ws, "CÀI ĐẶT HỆ THỐNG & CÁC LỖI MÔI TRƯỜNG PHÁT HIỆN", SUB, len(H))
header_row(ws, 4, H, [10, 44, 44, 11, 52, 12])
data_rows(ws, 5, [[b["id"], b["title"], b["cause"], b["severity"], b["workaround"], b["date"]] for b in ENV_BUGS], center_cols=(1, 4, 6))

# ------------------------------------------------------------ 3-6. Test case từng thành viên
summary = {}
for idx, (key, (name, msv, func)) in enumerate(MEMBERS.items(), start=3):
    ws = wb.create_sheet(f"{idx}. TC {key.title()}")
    H = ["Mã TC", "Loại kiểm thử", "Kỹ thuật / mục tiêu", "Tên test case", "Bước thực hiện / dữ liệu", "Kết quả mong đợi",
         "Kết quả thực tế", "Trạng thái", "Mã lỗi", "Minh chứng", "Ngày", "Người thực hiện"]
    title_block(ws, f"TEST CASE & KẾT QUẢ – {name.upper()} ({msv}) – {func}", SUB, len(H))
    header_row(ws, 4, H, [13, 13, 22, 30, 38, 32, 46, 10, 10, 18, 11, 14])
    rows = []
    cnt = Counter()
    # Giao diện
    for tid, v in ui.items():
        if v["owner"] == key:
            rows.append([tid, "Giao diện (Playwright)", "Kiểm thử GUI tự động", v["title"], v["steps"], v["expected"], v["actual"],
                         v["status"], ", ".join(bug_by_tc.get(tid, [])), "screenshots/" + v.get("screenshot", ""), DATES["UI"], name])
            cnt["UI_" + v["status"]] += 1
    # Đơn vị
    for num, (title, data, exp) in UNIT_DESC[key].items():
        tname = [n for n in unit if n.startswith(f"test_UT_{key}_{num}_")]
        ok, secs, msg = unit[tname[0]] if tname else (False, 0, "Không chạy")
        tid = f"UT_{key}_{num}"
        rows.append([tid, "Đơn vị (pytest)", "White-box: EP/BVA trên hàm/model", title, f"Dữ liệu: {data}\nHàm: {tname[0] if tname else ''}", exp,
                     ("Đúng như mong đợi" if ok else f"Sai khác: {msg}") + f" ({secs:.2f}s)", "Pass" if ok else "Fail",
                     ", ".join(bug_by_tc.get(tid, [])), "logs/unit_nhom11.xml", DATES["UT"], name])
        cnt["UT_" + ("Pass" if ok else "Fail")] += 1
    # Hộp đen
    for tid, v in bb.items():
        if tid.startswith("_") or v["owner"] != key:
            continue
        rows.append([tid, "Hộp đen (API)", v["technique"], v["title"], v["data"], v["expected"], v["actual"], v["status"],
                     ", ".join(bug_by_tc.get(tid, [])), "logs/blackbox_results.json", DATE2.get(key, DATES["BB"]), name])
        cnt["BB_" + v["status"]] += 1
    data_rows(ws, 5, rows, status_col=8, center_cols=(1, 2, 8, 9, 11))
    summary[key] = cnt

# ------------------------------------------------------------ 7. Báo cáo lỗi
ws = wb.create_sheet("7. Bao cao loi")
H = ["Mã lỗi", "Tiêu đề", "Chức năng", "Người phát hiện", "Mức độ", "Ưu tiên", "Các bước tái hiện", "Kết quả mong đợi", "Kết quả thực tế", "Nguyên nhân (mã nguồn)", "Test case", "Ngày", "Trạng thái"]
title_block(ws, "BÁO CÁO LỖI (BUG REPORT)", SUB, len(H))
header_row(ws, 4, H, [10, 36, 16, 15, 10, 9, 40, 30, 36, 34, 18, 11, 10])
data_rows(ws, 5, [[b["id"], b["title"], b["func"], MEMBERS[b["owner"]][0], b["severity"], b["priority"], b["steps"], b["expected"],
                   b["actual"], b["cause"], ", ".join(b["tcs"]), b["date"], "Mở"] for b in BUGS], center_cols=(1, 4, 5, 6, 12, 13))

# ------------------------------------------------------------ 8. Hiệu năng
ws = wb.create_sheet("8. Hieu nang")
H = ["Kịch bản", "Số request", "Lỗi", "Tỉ lệ lỗi (%)", "TB (s)", "p50 (s)", "p95 (s)", "Max (s)", "Throughput (req/s)", "Đánh giá so với NFR"]
title_block(ws, "KẾT QUẢ KIỂM THỬ HIỆU NĂNG", SUB, len(H))
header_row(ws, 4, H, [58, 11, 8, 11, 9, 9, 9, 9, 15, 40])
NFR = {"PERF_LIST": "NFR-04: p95 ≤ 2s, 0% lỗi", "PERF_MODELS": "Tham khảo", "PERF_INGEST": "NFR-01: ≤ 30s/tài liệu nhỏ", "PERF_RAG": "NFR-03: trung vị ≤ 60s"}
prow = []
for p in perf:
    k = p["test"].split(" ")[0]
    verdict = NFR.get(k, "")
    if k == "PERF_LIST":
        verdict += " -> " + ("Đạt" if p["p95_s"] <= 2 and p["errors"] == 0 else "Không đạt")
    elif k == "PERF_INGEST":
        verdict += " -> " + ("Đạt" if p["max_s"] <= 30 else "Không đạt")
    elif k == "PERF_RAG":
        verdict += " -> " + ("Đạt" if p["p50_s"] <= 60 else "Không đạt")
    prow.append([p["test"], p["requests"], p["errors"], p["error_rate_pct"], p["avg_s"], p["p50_s"], p["p95_s"], p["max_s"], p["throughput_rps"], verdict])
end = data_rows(ws, 5, prow, center_cols=(2, 3, 4, 5, 6, 7, 8, 9))
big = bb.get("BB_TIEN_18", {})
data_rows(ws, end, [["Nạp file lớn 2,7MB (BB_TIEN_18)", 1, 1 if big.get("status") == "Fail" else 0, "", "", "", "", "", "", "NFR-02: ≤ 120s -> " + big.get("actual", "")[:60]]])
if perf:
    ch = BarChart()
    ch.title = "Thời gian phản hồi p50 / p95 (giây)"
    ch.add_data(Reference(ws, min_col=6, max_col=7, min_row=4, max_row=4 + len(perf)), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=5, max_row=4 + len(perf)))
    ch.height, ch.width = 8, 22
    ws.add_chart(ch, f"A{end + 3}")

# ------------------------------------------------------------ 9. Bộ test có sẵn của dự án
ws = wb.create_sheet("9. Bo test san co")
title_block(ws, "KẾT QUẢ CHẠY LẠI BỘ UNIT TEST CÓ SẴN CỦA DỰ ÁN (pytest)", SUB, 2)
kv_table(ws, 4, [
    ("Phạm vi chạy", "tests/server/ingest/test_file_validation.py, test_uri_loader.py, tests/engines/test_citation_*.py (3 file), tests/server/models, tests/server/test_ui_mount.py"),
    ("Tổng số test", str(repo_total)),
    ("Pass", str(repo_total - repo_fail)),
    ("Fail", f"{repo_fail}: " + ", ".join(repo_fail_names)),
    ("Phân tích", "3 test PDF thật bị lỗi MISMATCHED_MIME_TYPE trên Windows (đoán MIME khác libmagic) -> ENV-06. Các test còn lại đạt."),
    ("Ngày chạy", "04/11/2026 (hồi quy)"),
    ("Minh chứng", "03_MinhChung/logs/repo_unit_tests.xml"),
])

# ------------------------------------------------------------ 10. Truy vết
ws = wb.create_sheet("10. Ma tran truy vet")
H = ["Mã yêu cầu", "Mô tả", "Test case", "Kết quả"]
title_block(ws, "MA TRẬN TRUY VẾT YÊU CẦU – TEST CASE", "Theo tài liệu 03_MinhChung/DacTa_YeuCau_BoSung_Nhom11.docx", len(H))
header_row(ws, 4, H, [18, 50, 46, 22])
ALL = {**{k: v["status"] for k, v in bb.items() if not k.startswith("_")}, **{k: v["status"] for k, v in ui.items()}}
for key in UNIT_DESC:
    for num in UNIT_DESC[key]:
        t = [n for n in unit if n.startswith(f"test_UT_{key}_{num}_")]
        ALL[f"UT_{key}_{num}"] = "Pass" if (t and unit[t[0]][0]) else "Fail"


def expand(spec):
    out = []
    for part in spec.split(", "):
        if "-" in part.split("_")[-1]:
            pre, rng = part.rsplit("_", 1)
            a, b = rng.split("-")
            out += [f"{pre}_{i:02d}" for i in range(int(a), int(b) + 1)]
        else:
            out.append(part)
    return out


TRACE = [
    ("REQ-ING-01", "Nạp file qua API/UI", "BB_TIEN_01-05, UI_TIEN_03-04"),
    ("REQ-ING-02", "Kiểm tra dữ liệu đầu vào", "BB_TIEN_06-12, UT_TIEN_01-10"),
    ("REQ-ING-03", "Từ chối định dạng cấm, MIME giả", "BB_TIEN_13-14, UI_TIEN_05"),
    ("REQ-ING-04", "Bảo mật tên & URI", "BB_TIEN_16-17, UT_TIEN_12-13"),
    ("REQ-DOC-01", "Liệt kê tài liệu", "BB_VINH_01-03, UI_VINH_01-02"),
    ("REQ-DOC-02", "Xóa tài liệu", "BB_VINH_04-09, UI_VINH_03-04"),
    ("REQ-DOC-03", "Xem nội dung", "BB_VINH_10-13"),
    ("REQ-DOC-04", "Cô lập collection", "BB_VINH_14-16"),
    ("REQ-RAG-01", "Trả lời đúng theo tài liệu", "BB_DUY_01-05, UI_DUY_01"),
    ("REQ-RAG-02", "Không bịa, đúng phạm vi", "BB_DUY_06-07, BB_DUY_12"),
    ("REQ-RAG-03", "Trích dẫn nguồn", "BB_DUY_08-09, UI_DUY_03-04"),
    ("REQ-RAG-04", "Chống injection, đúng ngôn ngữ", "BB_DUY_13-14"),
    ("REQ-SES-01", "CRUD hội thoại", "UI_MANH_01-05"),
    ("REQ-SES-02", "Danh sách & chọn mô hình", "BB_MANH_01-05, UI_MANH_06"),
    ("REQ-SES-03", "Nhiều lượt, streaming, tham số", "BB_MANH_08-15, UT_MANH_01-09"),
    ("REQ-SES-04", "Settings & bảo mật phía client", "UI_MANH_08-11"),
]
trows = []
for rid, desc, spec in TRACE:
    ids = [i for i in expand(spec) if i in ALL]
    p = sum(ALL[i] == "Pass" for i in ids)
    trows.append([rid, desc, spec, f"{p}/{len(ids)} Pass"])
data_rows(ws, 5, trows, center_cols=(1, 4))

# ------------------------------------------------------------ 11. Tổng hợp
ws = wb.create_sheet("11. Tong hop", 0)
title_block(ws, "TỔNG HỢP KẾT QUẢ KIỂM THỬ – NHÓM 11", SUB, 8)
H = ["Thành viên", "Chức năng", "Giao diện (Pass/Tổng)", "Đơn vị (Pass/Tổng)", "Hộp đen (Pass/Tổng)", "Tổng Pass", "Tổng Fail", "Tỉ lệ Pass"]
header_row(ws, 4, H, [24, 44, 18, 18, 18, 11, 11, 11])
rows = []
for key, (name, msv, func) in MEMBERS.items():
    c = summary[key]
    tp = c["UI_Pass"] + c["UT_Pass"] + c["BB_Pass"]
    tf = c["UI_Fail"] + c["UT_Fail"] + c["BB_Fail"]
    rows.append([name, func, f"{c['UI_Pass']}/{c['UI_Pass'] + c['UI_Fail']}", f"{c['UT_Pass']}/{c['UT_Pass'] + c['UT_Fail']}",
                 f"{c['BB_Pass']}/{c['BB_Pass'] + c['BB_Fail']}", tp, tf, f"{tp / (tp + tf) * 100:.1f}%"])
TP = sum(r_[5] for r_ in rows)
TF = sum(r_[6] for r_ in rows)
rows.append(["TỔNG CỘNG", "", "", "", "", TP, TF, f"{TP / (TP + TF) * 100:.1f}%"])
end = data_rows(ws, 5, rows, center_cols=(3, 4, 5, 6, 7, 8))
sev = Counter(b["severity"] for b in BUGS)
end = section(ws, end + 1, "THỐNG KÊ LỖI", 8)
ws.cell(end, 1, "Mức độ")
ws.cell(end, 2, "Số lỗi")
srow = end + 1
for i, s in enumerate(["Cao", "Trung bình", "Thấp"]):
    ws.cell(srow + i, 1, s)
    ws.cell(srow + i, 2, sev.get(s, 0))
data_rows(ws, srow + 3, [["Lỗi chức năng/bảo mật/hiệu năng", len(BUGS)], ["Lỗi môi trường cài đặt", len(ENV_BUGS)], ["Lỗi tài liệu (file Review)", 16]])
ch = BarChart()
ch.title = "Pass / Fail theo thành viên"
ch.add_data(Reference(ws, min_col=6, max_col=7, min_row=4, max_row=8), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=1, min_row=5, max_row=8))
ch.height, ch.width = 8, 16
ws.add_chart(ch, "D" + str(end + 1))
pie = PieChart()
pie.title = "Lỗi theo mức độ"
pie.add_data(Reference(ws, min_col=2, min_row=srow, max_row=srow + 2))
pie.set_categories(Reference(ws, min_col=1, min_row=srow, max_row=srow + 2))
pie.height, pie.width = 7, 10
ws.add_chart(pie, "A" + str(srow + 8))

# ------------------------------------------------------------ 12. Ảnh minh chứng
ws = wb.create_sheet("12. Anh minh chung")
title_block(ws, "MỘT SỐ ẢNH CHỤP MINH CHỨNG KIỂM THỬ GIAO DIỆN", "Toàn bộ ảnh: 03_MinhChung/screenshots", 12)
row = 4
for nm in ["UI_TIEN_03", "UI_VINH_04", "UI_DUY_01", "UI_DUY_03", "UI_MANH_06", "UI_MANH_10"]:
    p = SHOTS / f"{nm}.png"
    if not p.exists():
        continue
    ws.cell(row, 1, nm)
    img = XLImage(str(p))
    img.width, img.height = 720, 450
    ws.add_image(img, f"A{row + 1}")
    row += 25

wb.save(OUT)
print("saved", OUT, "| tổng pass/fail:", TP, TF)
