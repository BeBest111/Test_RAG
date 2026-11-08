"""Chỉnh sửa trực tiếp BTLSo1.docx: điền trang bìa và viết toàn bộ nội dung báo cáo theo bố cục yêu cầu.

Nguồn dữ liệu: 01_KetQua_Review_Nhom11.xlsx, logs/*.json, logs/*.xml, bugs.py, ảnh screenshots/.
Chạy lại được nhiều lần: luôn bắt đầu từ bản gốc BTLSo1_original.docx (sao lưu).
"""

import copy
import json
import shutil
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT  # noqa: F401
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from openpyxl import load_workbook

from bugs import BUGS, ENV_BUGS
from narrative import MEMBER_TEXT, PART1, PART3

ROOT = Path(__file__).resolve().parents[3]
EVI = ROOT / "03_MinhChung"
LOGS = EVI / "logs"
SHOTS = EVI / "screenshots"
REPORT = ROOT / "BTLSo1.docx"
ORIG = Path(r"C:\Users\Admin\AppData\Local\Temp\claude\51d388c47cb6a1bf\b7d57d9e-2826-4ff1-bdc0-4542745b7b07\scratchpad\backup\BTLSo1_original.docx")
if not ORIG.exists():
    shutil.copy(REPORT, ORIG)

MEMBERS = {
    "TIEN": ("Nguyễn Minh Tiến", "B22DVCN308", "Nạp tài liệu (Ingest) – upload và lập chỉ mục tài liệu"),
    "VINH": ("Nguyễn Bá Quang Vinh", "B22DVCN348", "Quản lý tài liệu – liệt kê, xem nội dung, xóa tài liệu"),
    "DUY": ("Vũ Đức Duy", "B22DVCN397", "Hỏi đáp RAG có trích dẫn nguồn"),
    "MANH": ("Bùi Văn Mạnh", "B22DVCN212", "Quản lý hội thoại, mô hình và cấu hình (Settings)"),
}

bb = json.loads((LOGS / "blackbox_results.json").read_text(encoding="utf-8"))
ui = json.loads((LOGS / "ui_results.json").read_text(encoding="utf-8"))
perf = json.loads((LOGS / "perf_results.json").read_text(encoding="utf-8"))
unit = {}
for t in ET.parse(LOGS / "unit_nhom11.xml").getroot().iter("testcase"):
    f = t.find("failure")
    unit[t.get("name")] = (f is None and t.find("error") is None, (f.get("message") if f is not None else "") or "")
repo = list(ET.parse(LOGS / "repo_unit_tests.xml").getroot().iter("testcase"))
repo_fail = [t.get("name") for t in repo if t.find("failure") is not None or t.find("error") is not None]
rv = load_workbook(ROOT / "01_KetQua_Review_Nhom11.xlsx")


def sheet_rows(name, start=5):
    ws = rv[name]
    out = []
    for row in ws.iter_rows(min_row=start, values_only=True):
        if row[0] is None:
            break
        out.append(row)
    return out


# ============================================================ helpers
doc = Document(ORIG)
for sname, size, lvl in [("Heading 1", 15, 0), ("Heading 2", 13.5, 1), ("Heading 3", 13, 2), ("Heading 4", 13, 3)]:
    try:
        st = doc.styles[sname]
    except KeyError:
        st = doc.styles.add_style(sname, WD_STYLE_TYPE.PARAGRAPH)
    st.base_style = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(size)
    st.font.bold = True
    st.font.italic = lvl == 3
    st.font.color.rgb = RGBColor(0x1F, 0x38, 0x64) if lvl < 2 else RGBColor(0, 0, 0)
    pf = st.paragraph_format
    pf.space_before = Pt(12 if lvl == 0 else 8)
    pf.space_after = Pt(6)
    pf.keep_with_next = True
    pPr = st.element.get_or_add_pPr()
    ol = OxmlElement("w:outlineLvl")
    ol.set(qn("w:val"), str(lvl))
    pPr.append(ol)
    rpr = st.element.get_or_add_rPr()
    rf = OxmlElement("w:rFonts")
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), "Times New Roman")
    rpr.append(rf)
normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(13)

body = doc.element.body
sectPr = body[-1] if body[-1].tag == qn("w:sectPr") else None


def para(text="", bold=False, italic=False, size=13, align=None, indent=True, style=None, color=None):
    p = doc.add_paragraph(style=style)
    if text:
        r = p.add_run(text)
        r.bold = bold
        r.italic = italic
        r.font.size = Pt(size)
        r.font.name = "Times New Roman"
        if color:
            r.font.color.rgb = RGBColor.from_string(color)
    pf = p.paragraph_format
    pf.space_after = Pt(4)
    pf.line_spacing = 1.3
    if indent and align is None:
        pf.first_line_indent = Cm(1)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if align is not None:
        p.alignment = align
    return p


def rich(parts, indent=True):
    """parts: list of (text, bold)."""
    p = para(indent=indent)
    for t, b in parts:
        r = p.add_run(t)
        r.bold = b
        r.font.size = Pt(13)
    return p


def bullet(text, level=0, bold_prefix=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(1.0 + 0.8 * level)
    pf.first_line_indent = Cm(-0.5)
    pf.space_after = Pt(2)
    pf.line_spacing = 1.25
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(("–  " if level else "•  "))
    r.font.size = Pt(13)
    if bold_prefix:
        rb = p.add_run(bold_prefix)
        rb.bold = True
        rb.font.size = Pt(13)
    r2 = p.add_run(text)
    r2.font.size = Pt(13)
    return p


def h(text, lvl):
    return doc.add_paragraph(text, style=f"Heading {lvl}")


def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), color)
    tcPr.append(sh)


def set_borders(t):
    tblPr = t._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), "4")
        e.set(qn("w:space"), "0")
        e.set(qn("w:color"), "8EA9C1")
        b.append(e)
    tblPr.append(b)


TABLE_NO = [0]
FIG_NO = [0]


def caption(text, kind="Bảng"):
    if kind == "Bảng":
        TABLE_NO[0] += 1
        n = TABLE_NO[0]
    else:
        FIG_NO[0] += 1
        n = FIG_NO[0]
    p = para(f"{kind} {n}. {text}", italic=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER)
    return p


STATUS_COLOR = {"Pass": "C6EFCE", "Đạt": "C6EFCE", "Fail": "FFC7CE", "Không đạt": "FFC7CE", "Đạt một phần": "FFEB9C",
                "Partial": "FFEB9C", "Cao": "FFC7CE", "Trung bình": "FFEB9C", "Thấp": "DDEBF7"}


def table(header, rows, widths=None, size=10.5, cap=None, status_cols=()):
    if cap:
        caption(cap)
    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    set_borders(t)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, hd in enumerate(header):
        c = t.cell(0, j)
        c.text = ""
        r = c.paragraphs[0].add_run(str(hd))
        r.bold = True
        r.font.size = Pt(size)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        shade(c, "2E75B6")
    # lặp lại hàng tiêu đề khi sang trang
    trPr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    th.set(qn("w:val"), "true")
    trPr.append(th)
    for i, row in enumerate(rows, 1):
        for j, v in enumerate(row):
            c = t.cell(i, j)
            c.text = ""
            r = c.paragraphs[0].add_run("" if v is None else str(v))
            r.font.size = Pt(size)
            if j in status_cols and str(v) in STATUS_COLOR:
                shade(c, STATUS_COLOR[str(v)])
                c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if widths:
        for row in t.rows:
            for j, w in enumerate(widths):
                row.cells[j].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def image(name, cap, width=15.5):
    p = SHOTS / f"{name}.png"
    if not p.exists():
        return
    doc.add_picture(str(p), width=Cm(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption(cap, "Hình")


def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def toc():
    p = doc.add_paragraph()
    r = p.add_run()
    for tag, txt in [("begin", None), (None, 'TOC \\o "1-3" \\h \\z \\u'), ("separate", None), (None, None), ("end", None)]:
        if tag:
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), tag)
            if tag == "begin":
                fc.set(qn("w:dirty"), "true")
            r._r.append(fc)
        elif txt:
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = txt
            r._r.append(it)
        else:
            t_ = OxmlElement("w:t")
            t_.text = "Nhấn chuột phải > Update Field (hoặc F9) để cập nhật mục lục."
            r._r.append(t_)
    # yêu cầu Word cập nhật field khi mở
    settings = doc.settings.element
    uf = OxmlElement("w:updateFields")
    uf.set(qn("w:val"), "true")
    settings.append(uf)


def short(s, n=170):
    s = (s or "").replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"


# ============================================================ TRANG BÌA
paras = doc.paragraphs
# Ngày tháng
date_p = [p for p in paras if p.text.strip().startswith("Hà")][0]
for r in date_p.runs[1:]:
    r.text = ""
date_p.runs[0].text = "Hà Nội, ngày 06 tháng 11 năm 2026"
date_p.runs[0].bold = True
# Trang bìa: nhãn "Tên sinh viên" + mỗi thành viên một dòng kèm chức năng đảm nhiệm
name_ps = [p_ for p_ in paras if any(k in p_.text for k in ("Minh Tiến", "Quang Vinh", "Vũ Đức Duy", "Bùi Văn Mạnh"))]
label_p = name_ps[0]
base_indent = label_p.paragraph_format.left_indent or Cm(0)
SHORT = ["Nạp tài liệu", "Quản lý tài liệu", "Hỏi đáp RAG", "Hội thoại & cấu hình"]
# dòng nhãn: giữ run in đậm 'Tên sinh viên :', bỏ phần tên
keep = True
for r_ in label_p.runs:
    if keep and r_.bold:
        continue
    keep = False
    r_.text = ""
for p_, (k_, (n_, m_, f_)), sh in zip(name_ps, MEMBERS.items(), SHORT):
    if p_ is not label_p:
        for r_ in p_.runs:
            r_.text = ""
newp = []
anchor = label_p
for (k_, (n_, m_, f_)), sh in zip(MEMBERS.items(), SHORT):
    np_ = copy.deepcopy(label_p._p)
    anchor._p.addnext(np_) if hasattr(anchor, "_p") else anchor.addnext(np_)
    from docx.text.paragraph import Paragraph
    P = Paragraph(np_, label_p._parent)
    for r_ in P.runs:
        r_.text = ""
    P.paragraph_format.left_indent = base_indent + Cm(1.2)
    P.paragraph_format.first_line_indent = Cm(0)
    P.paragraph_format.space_after = Pt(0)
    rr = P.add_run(f"{n_} – {m_}")
    rr.font.size = Pt(13)
    rr.font.name = "Times New Roman"
    rr2 = P.add_run(f"  ({sh})")
    rr2.italic = True
    rr2.font.size = Pt(12)
    rr2.font.name = "Times New Roman"
    anchor = P
for p_ in name_ps:
    if p_ is not label_p:
        p_._p.getparent().remove(p_._p)

# Xóa các đoạn trống (style Body Text) giữa "Lớp" và ngày tháng để trang bìa vừa 1 trang
for p_ in [p_ for p_ in paras if p_.style.name == "Body Text" and not p_.text.strip()]:
    if p_._p.getparent() is not None:
        p_._p.getparent().remove(p_._p)

# Xóa các đoạn trống sau dòng ngày tháng (tránh trang trắng)
nxt = date_p._p.getnext()
while nxt is not None and nxt.tag == qn("w:p") and not "".join(nxt.itertext()).strip() and not nxt.findall(".//" + qn("w:drawing")):
    rm = nxt
    nxt = nxt.getnext()
    rm.getparent().remove(rm)

# Từ đây thêm nội dung vào cuối tài liệu (trước sectPr)
mucluc = para("MỤC LỤC", bold=True, size=15, align=WD_ALIGN_PARAGRAPH.CENTER)
mucluc.paragraph_format.page_break_before = True
toc()
page_break()

# ============================================================ PHẦN 1
h("PHẦN 1 – CÔNG VIỆC CHUNG CỦA NHÓM", 1)
para("Danh sách thành viên và chức năng đảm nhiệm đảm bảo chất lượng:", indent=False)
table(["STT", "Họ và tên", "Mã SV", "Chức năng đảm nhiệm đảm bảo chất lượng"],
      [[i, n_, m_, f_] for i, (n_, m_, f_) in enumerate(MEMBERS.values(), 1)], widths=[1.2, 4.6, 3, 7.7], cap="Phân công thành viên")
h("1.1. Mô tả hệ thống của nhóm", 2)
h("1.1.1. Giới thiệu về hệ thống", 3)
for t in PART1["intro"]:
    para(t)
table(["Thuộc tính", "Thông tin"], PART1["intro_table"], widths=[4.5, 12], cap="Thông tin chung về hệ thống PrivateGPT")
h("1.1.2. Công nghệ được sử dụng", 3)
para(PART1["tech_intro"])
table(["Thành phần", "Công nghệ", "Vai trò"], PART1["tech_table"], widths=[3.5, 5.5, 7.5], cap="Công nghệ sử dụng trong hệ thống và môi trường kiểm thử")
h("1.1.3. Các chức năng chính của hệ thống", 3)
para(PART1["func_intro"])
for b, t in PART1["functions"]:
    bullet(t, bold_prefix=b)
para(PART1["rag_flow"])
image("explore_context", "Giao diện Workbench – màn hình Context > Documents (chụp trong quá trình kiểm thử)")
h("1.1.4. Hiện trạng đảm bảo chất lượng của hệ thống", 3)
for t in PART1["qa_status"]:
    para(t)
table(["Hạng mục", "Hiện trạng", "Nhận xét của nhóm"], PART1["qa_table"], widths=[3.8, 6.2, 6.5], cap="Hiện trạng đảm bảo chất lượng của PrivateGPT")
h("1.1.5. Cài đặt môi trường kiểm thử", 3)
for t in PART1["install"]:
    para(t)
table(["Mã", "Hiện tượng", "Nguyên nhân", "Mức độ", "Cách xử lý"],
      [[b["id"], b["title"], b["cause"], b["severity"], b["workaround"]] for b in ENV_BUGS],
      widths=[1.5, 4.5, 5.2, 1.8, 3.6], size=9.5, cap="Các lỗi môi trường phát hiện khi cài đặt trên Windows", status_cols=(3,))

h("1.2. Kết quả thực hiện rà soát theo checklist", 2)
cl = sheet_rows("2. CL Review dac ta (nhom)")
cnt = Counter(r[4] for r in cl)
for t in PART1["review_intro"]:
    para(t)
rich([("Kết quả tổng hợp: ", True), (f"{len(cl)} tiêu chí – Đạt {cnt['Đạt']}, Đạt một phần {cnt['Đạt một phần']}, "
                                     f"Không đạt {cnt['Không đạt']}; phát hiện {len(sheet_rows('3. Loi tai lieu'))} lỗi tài liệu "
                                     f"(chi tiết trong file 01_KetQua_Review_Nhom11.xlsx).", False)])
table(["STT", "Nhóm tiêu chí", "Câu hỏi kiểm tra", "Kết quả", "Bằng chứng / nhận xét", "Mã lỗi"],
      [[r[0], r[1], r[2], r[4], short(r[5], 150), r[6]] for r in cl], widths=[1, 2.5, 5, 2, 5.5, 1.5], size=9.5,
      cap="Kết quả rà soát tài liệu đặc tả theo checklist (cả nhóm)", status_cols=(3,))
dd = sheet_rows("3. Loi tai lieu")
table(["Mã lỗi", "Tài liệu", "Mô tả lỗi", "Loại", "Mức độ", "Đề xuất sửa"],
      [[r[0], r[1], r[3], r[4], r[5], r[6]] for r in dd], widths=[1.6, 2.6, 5.6, 2, 1.8, 4], size=9.5,
      cap="Danh sách lỗi phát hiện trong tài liệu", status_cols=(4,))
para(PART1["review_conclusion"])

h("1.3. Kế hoạch kiểm thử và tổng hợp kết quả của nhóm", 2)
for t in PART1["plan"]:
    para(t)
table(["Thời gian", "Công việc", "Thực hiện"], PART1["schedule"], widths=[3.6, 9.4, 3.5], cap="Lịch thực hiện của nhóm (15/10/2026 – 06/11/2026)")


def member_counts(key):
    c = Counter()
    for v in ui.values():
        if v["owner"] == key:
            c["UI_" + v["status"]] += 1
    for n, (ok, _) in unit.items():
        if n.startswith(f"test_UT_{key}_"):
            c["UT_" + ("Pass" if ok else "Fail")] += 1
    for k, v in bb.items():
        if not k.startswith("_") and v["owner"] == key:
            c["BB_" + v["status"]] += 1
    return c


rows = []
TP = TF = 0
for key, (n, msv, f) in MEMBERS.items():
    c = member_counts(key)
    p_ = c["UI_Pass"] + c["UT_Pass"] + c["BB_Pass"]
    f_ = c["UI_Fail"] + c["UT_Fail"] + c["BB_Fail"]
    TP += p_
    TF += f_
    nb = sum(1 for b in BUGS if b["owner"] == key)
    rows.append([n, f"{c['UI_Pass']}/{c['UI_Pass'] + c['UI_Fail']}", f"{c['UT_Pass']}/{c['UT_Pass'] + c['UT_Fail']}",
                 f"{c['BB_Pass']}/{c['BB_Pass'] + c['BB_Fail']}", p_ + f_, f"{p_ / (p_ + f_) * 100:.1f}%", nb])
rows.append(["Tổng cộng", "", "", "", TP + TF, f"{TP / (TP + TF) * 100:.1f}%", len(BUGS)])
table(["Thành viên", "Giao diện (Pass/Tổng)", "Đơn vị (Pass/Tổng)", "Hộp đen (Pass/Tổng)", "Tổng TC", "Tỉ lệ Pass", "Số lỗi"], rows,
      widths=[4.2, 2.5, 2.5, 2.5, 1.6, 1.8, 1.4], cap="Tổng hợp kết quả kiểm thử của nhóm")
sev = Counter(b["severity"] for b in BUGS)
rich([("Tổng số lỗi chức năng/bảo mật/hiệu năng: ", True),
      (f"{len(BUGS)} lỗi (Cao: {sev['Cao']}, Trung bình: {sev['Trung bình']}, Thấp: {sev['Thấp']}); "
       f"thêm {len(ENV_BUGS)} lỗi môi trường cài đặt và {len(dd)} lỗi tài liệu.", False)])
para(f"Ngoài các test case do nhóm tự xây dựng, nhóm chạy lại {len(repo)} unit test có sẵn của dự án liên quan đến 4 chức năng: "
     f"{len(repo) - len(repo_fail)} pass, {len(repo_fail)} fail ({', '.join(repo_fail)}) – các test fail đều do lỗi môi trường ENV-06 trên Windows.")
prow = [[p_["test"], p_["requests"], p_["errors"], p_["p50_s"], p_["p95_s"], p_["max_s"], p_["throughput_rps"]] for p_ in perf]
table(["Kịch bản hiệu năng", "Số request", "Lỗi", "p50 (s)", "p95 (s)", "Max (s)", "req/s"], prow,
      widths=[7.5, 1.6, 1.2, 1.6, 1.6, 1.6, 1.5], size=9.5, cap="Kết quả kiểm thử hiệu năng")
for t in PART1["perf_comment"]:
    para(t)

# ============================================================ PHẦN 2
page_break()
h("PHẦN 2 – KẾT QUẢ TỪNG THÀNH VIÊN", 1)
SHEET_CODE = {"TIEN": "5. Review code Tien", "VINH": "6. Review code Vinh", "DUY": "7. Review code Duy", "MANH": "8. Review code Manh"}
spec = sheet_rows("4. Review dac ta chuc nang")
UT_DESC = {
    "TIEN": "Kiểm thử các hàm/model kiểm tra đầu vào của chức năng nạp: _is_valid_base64, _is_valid_uri, IngestBody, FileArtifact (file test_scripts/unit/test_unit_nhom11.py, class TestIngest_Tien).",
    "VINH": "Kiểm thử model DeleteIngestedDocumentBody (ràng buộc collection/artifact) theo phân hoạch tương đương và giá trị biên (class TestDocMgmt_Vinh).",
    "DUY": "Kiểm thử model ChatBody cho request RAG và bộ phân tích trích dẫn extract_citations_by_original_text (class TestRagChat_Duy).",
    "MANH": "Kiểm thử ChatBody cho hội thoại nhiều lượt và ràng buộc tham số sinh (temperature, top_p, max_tokens, role) (class TestSession_Manh).",
}
for idx, (key, (n, msv, f)) in enumerate(MEMBERS.items(), 1):
    T = MEMBER_TEXT[key]
    h(f"2.{idx}. {n} – {msv} (thực hiện chức năng: {f})", 2)
    para(T["scope"])
    # --- review đặc tả
    h(f"2.{idx}.1. Kết quả review tài liệu đặc tả phần chức năng", 3)
    para(T["spec_review"])
    rows = [[r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8]] for r in spec if r[0] == n]
    table(["Mã YC", "Nội dung yêu cầu", "Nguồn", "Đầy đủ", "Rõ ràng", "Kiểm thử được", "Nhất quán", "Nhận xét"], rows,
          widths=[1.8, 4.2, 2.2, 1.4, 1.4, 1.5, 1.4, 3.6], size=9, cap=f"Review đặc tả chức năng – {n}", status_cols=(3, 4, 5, 6))
    # --- review code
    h(f"2.{idx}.2. Kết quả review code phần chức năng", 3)
    para(T["code_review"])
    cr = sheet_rows(SHEET_CODE[key])
    table(["STT", "Tiêu chí", "Kết quả", "Vị trí (file:dòng)", "Nhận xét / bằng chứng"],
          [[r[0], r[1], r[2], r[3], r[4]] for r in cr], widths=[1, 4, 2, 4, 5.5], size=9, cap=f"Checklist review code – {n}", status_cols=(2,))
    cc = Counter(r[2] for r in cr)
    rich([("Tổng hợp: ", True), (f"{len(cr)} tiêu chí – Đạt {cc['Đạt']}, Đạt một phần {cc['Đạt một phần']}, Không đạt {cc['Không đạt']}.", False)])
    # --- test
    h(f"2.{idx}.3. Kết quả xây dựng test case và thực hiện kiểm thử", 3)
    para(T["test_intro"])
    h("a) Kiểm thử giao diện", 4)
    para(T["ui"])
    urows = [[k, v["title"], short(v["expected"], 90), short(v["actual"], 130), v["status"]] for k, v in sorted(ui.items()) if v["owner"] == key]
    table(["Mã TC", "Tên test case", "Kết quả mong đợi", "Kết quả thực tế", "KQ"], urows, widths=[2, 3.6, 4, 5.4, 1.4], size=9,
          cap=f"Test case kiểm thử giao diện – {n}", status_cols=(4,))
    for nm, cap_ in T["images"]:
        image(nm, cap_, width=14.5)
    h("b) Kiểm thử đơn vị", 4)
    para(UT_DESC[key] + " " + T["unit"])
    urs = []
    for name_, (ok, msg) in sorted(unit.items()):
        if name_.startswith(f"test_UT_{key}_"):
            tid = "UT_" + key + "_" + name_.split("_")[3]
            urs.append([tid, name_.split("_", 4)[4].replace("_", " "), "Pass" if ok else "Fail", short(msg, 80) if not ok else ""])
    table(["Mã TC", "Nội dung kiểm thử (tên hàm test)", "KQ", "Ghi chú"], urs, widths=[2.3, 9, 1.4, 4], size=9.5,
          cap=f"Kết quả unit test (pytest) – {n}", status_cols=(2,))
    h("c) Kiểm thử hộp đen", 4)
    para(T["blackbox"])
    brows = [[k, v["technique"], v["title"], short(v["expected"], 80), short(v["actual"], 120), v["status"]]
             for k, v in sorted(bb.items()) if not k.startswith("_") and v["owner"] == key]
    table(["Mã TC", "Kỹ thuật", "Tên test case", "Mong đợi", "Thực tế", "KQ"], brows, widths=[1.9, 2.6, 3.1, 3.2, 4.4, 1.2], size=8.5,
          cap=f"Test case kiểm thử hộp đen (API) – {n}", status_cols=(5,))
    h("d) Nội dung lựa chọn thêm", 4)
    for b_, t_ in T["extra"]:
        bullet(t_, bold_prefix=b_)
    # --- lỗi
    h(f"2.{idx}.4. Lỗi phát hiện và đánh giá kết quả kiểm thử", 3)
    mb = [b for b in BUGS if b["owner"] == key]
    table(["Mã lỗi", "Tiêu đề", "Mức độ", "Kết quả thực tế", "Test case"],
          [[b["id"], b["title"], b["severity"], short(b["actual"], 140), ", ".join(b["tcs"])] for b in mb],
          widths=[1.6, 5, 1.8, 6, 2.4], size=9, cap=f"Danh sách lỗi phát hiện – {n}", status_cols=(2,))
    for t_ in T["evaluation"]:
        para(t_)

# ============================================================ PHẦN 3
page_break()
h("PHẦN 3 – KẾT LUẬN VÀ ĐỀ XUẤT", 1)
for title_, items in PART3["sections"]:
    h(title_, 2)
    for it in items:
        if isinstance(it, tuple):
            bullet(it[1], bold_prefix=it[0])
        else:
            para(it)
table(["Sản phẩm nộp", "Tệp / đường dẫn", "Nội dung"], PART3["deliverables"], widths=[3.5, 6, 7], size=10, cap="Danh sách sản phẩm nộp")
TCN = {}
for key in MEMBERS:
    TCN["UI_" + key] = sum(1 for v in ui.values() if v["owner"] == key)
    TCN["UT_" + key] = sum(1 for n_ in unit if n_.startswith(f"test_UT_{key}_"))
    TCN["BB_" + key] = sum(1 for k_, v in bb.items() if not k_.startswith("_") and v["owner"] == key)
contrib = [[a, b, c.format(**TCN), d] for a, b, c, d in PART3["contrib"]]
table(["Thành viên", "Công việc chung", "Công việc cá nhân", "Mức đóng góp"], contrib, widths=[3.6, 5, 5.8, 2], size=10,
      cap="Bảng phân công và đóng góp")

# di chuyển sectPr về cuối
if sectPr is not None:
    body.remove(sectPr)
    body.append(sectPr)
doc.core_properties.title = "Báo cáo bài tập dự án nhóm – Kiểm thử ứng dụng RAG – Nhóm 11"
doc.core_properties.author = "Nhóm 11 – D22VHCNPM02"
doc.save(REPORT)
print("saved", REPORT, "| tables:", TABLE_NO[0], "figures:", FIG_NO[0])
