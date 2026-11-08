"""Tiện ích định dạng openpyxl dùng chung cho các file Excel nộp."""

from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

NAVY = "1F3864"
BLUE = "2E75B6"
LIGHT = "DDEBF7"
GREY = "F2F2F2"
PASS_FILL = PatternFill("solid", fgColor="C6EFCE")
FAIL_FILL = PatternFill("solid", fgColor="FFC7CE")
PART_FILL = PatternFill("solid", fgColor="FFEB9C")
NA_FILL = PatternFill("solid", fgColor="EDEDED")
thin = Side(style="thin", color="A6A6A6")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
FONT = "Times New Roman"

MEMBERS = {
    "TIEN": ("Nguyễn Minh Tiến", "B22DVCN308", "Nạp tài liệu (Ingest) – upload & lập chỉ mục"),
    "VINH": ("Nguyễn Bá Quang Vinh", "B22DVCN348", "Quản lý tài liệu – liệt kê, xem nội dung, xóa"),
    "DUY": ("Vũ Đức Duy", "B22DVCN397", "Hỏi đáp RAG có trích dẫn nguồn"),
    "MANH": ("Bùi Văn Mạnh", "B22DVCN212", "Quản lý hội thoại, mô hình & cấu hình (Settings)"),
}


def title_block(ws, title, subtitle, ncols):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
    c = ws.cell(1, 1, title)
    c.font = Font(name=FONT, bold=True, size=15, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=NAVY)
    c.alignment = CENTER
    ws.row_dimensions[1].height = 30
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ncols)
    s = ws.cell(2, 1, subtitle)
    s.font = Font(name=FONT, italic=True, size=11, color="404040")
    s.alignment = CENTER
    ws.row_dimensions[2].height = 20


def header_row(ws, row, headers, widths=None):
    for i, h in enumerate(headers, 1):
        c = ws.cell(row, i, h)
        c.font = Font(name=FONT, bold=True, color="FFFFFF", size=11)
        c.fill = PatternFill("solid", fgColor=BLUE)
        c.alignment = CENTER
        c.border = BORDER
    ws.row_dimensions[row].height = 32
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = ws.cell(row + 1, 1)


def data_rows(ws, start_row, rows, status_col=None, center_cols=()):
    r = start_row
    for row in rows:
        for i, v in enumerate(row, 1):
            c = ws.cell(r, i, v)
            c.font = Font(name=FONT, size=11)
            c.border = BORDER
            c.alignment = CENTER if i in center_cols else WRAP
        if status_col:
            v = str(ws.cell(r, status_col).value or "")
            fill = {"Pass": PASS_FILL, "Đạt": PASS_FILL, "Fail": FAIL_FILL, "Không đạt": FAIL_FILL,
                    "Partial": PART_FILL, "Đạt một phần": PART_FILL, "N/A": NA_FILL}.get(v)
            if fill:
                ws.cell(r, status_col).fill = fill
        r += 1
    return r


def section(ws, row, text, ncols):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
    c = ws.cell(row, 1, text)
    c.font = Font(name=FONT, bold=True, size=12, color=NAVY)
    c.fill = PatternFill("solid", fgColor=LIGHT)
    c.alignment = Alignment(vertical="center")
    ws.row_dimensions[row].height = 22
    return row + 1


def kv_table(ws, start_row, pairs, w1=28, w2=90):
    ws.column_dimensions["A"].width = w1
    ws.column_dimensions["B"].width = w2
    r = start_row
    for k, v in pairs:
        a = ws.cell(r, 1, k)
        a.font = Font(name=FONT, bold=True)
        a.fill = PatternFill("solid", fgColor=GREY)
        a.border = BORDER
        a.alignment = WRAP
        b = ws.cell(r, 2, v)
        b.font = Font(name=FONT)
        b.border = BORDER
        b.alignment = WRAP
        r += 1
    return r
