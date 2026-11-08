"""Kiểm thử giao diện PrivateGPT Workbench (Playwright + Microsoft Edge, headless).

Kết quả: ../../logs/ui_results.json ; ảnh chụp: ../../screenshots/UI_*.png
Chạy: python ui_tests.py [TIEN|VINH|DUY|MANH ...]
"""

import json
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pgpt_client as c  # noqa: E402
from ui_common import BASE, new_page, shot  # noqa: E402

import os
LOG = Path(os.environ["DEMO_UI_LOG"]) if os.environ.get("DEMO_UI_LOG") else Path(__file__).resolve().parents[2] / "logs" / "ui_results.json"
DATA = c.DATA_DIR
CASES = []
VINH_ART = "vinh_ui_" + time.strftime("%H%M%S")
VINH_FILE = VINH_ART + ".txt"


def tc(tc_id, owner, title, steps, expected):
    def deco(fn):
        CASES.append(dict(id=tc_id, owner=owner, title=title, steps=steps, expected=expected, fn=fn))
        return fn
    return deco


def open_documents(page, expect=None, timeout=180000):
    """Mở Context > Documents, bấm Refresh và chờ danh sách tải xong (hoặc có file `expect`)."""
    page.click("#contextNav")
    page.wait_for_timeout(500)
    page.click("#refreshDocsButton")
    if expect:
        page.wait_for_function(
            f"document.querySelector('#documentsList').innerText.includes({expect!r})", timeout=timeout)
    else:
        page.wait_for_function(
            "document.querySelectorAll('#documentsList .source-row').length > 0 || "
            "(document.querySelector('#documentsList').innerText.includes('No documents') && "
            "![...document.querySelectorAll('.toast')].some(t => /Refreshing/.test(t.innerText)))",
            timeout=timeout)
    page.wait_for_timeout(800)


def open_auth(page):
    page.click("#settingsNav")
    page.wait_for_timeout(400)
    det = page.locator("#settingsScreen details:has(summary:has-text('Authentication'))").first
    if det.get_attribute("open") is None:
        det.locator("summary").click()
        page.wait_for_timeout(400)


def wait_models(page, timeout=180000):
    page.click("#refreshModelsButton")
    page.wait_for_function("!/No models/i.test(document.querySelector('#modelSelectLabel').innerText)", timeout=timeout)


def doc_titles(page):
    return [t.strip() for t in page.locator("#documentsList .source-title").all_inner_texts()]


def toasts(page):
    return " | ".join(page.locator(".toast").all_inner_texts())[:200]


# ------------------------------- TIẾN ---------------------------------------
@tc("UI_TIEN_01", "TIEN", "Bố cục màn hình Context > Documents",
    "1. Mở /ui  2. Bấm Context  3. Quan sát tab Documents",
    "Hiển thị tiêu đề Documents, mô tả, nút Refresh, nút Upload, vùng danh sách")
def _(page):
    page.click("#contextNav")
    page.wait_for_timeout(800)
    ok = all(page.locator(s).is_visible() for s in ["#refreshDocsButton", "#uploadDocsButton", "#documentsList"])
    return f"Refresh/Upload/List hiển thị: {ok}", ok, shot(page, "UI_TIEN_01")


@tc("UI_TIEN_02", "TIEN", "Tự tải danh sách tài liệu khi mở màn hình",
    "1. Collection nhom11 đã có tài liệu  2. Mở Context > Documents (không bấm Refresh)",
    "Danh sách tài liệu hiển thị ngay (không phải trạng thái rỗng)")
def _(page):
    page.click("#contextNav")
    page.wait_for_timeout(10000)  # chờ 10 giây, không bấm Refresh
    txt = page.inner_text("#documentsList")
    empty = "No documents loaded" in txt
    return f"Trạng thái rỗng: {empty} -> '{txt[:80]}'", not empty, shot(page, "UI_TIEN_02")


@tc("UI_TIEN_03", "TIEN", "Upload 1 file .txt qua giao diện",
    "1. Context > Documents  2. Bấm Upload, chọn ui_upload_test.txt",
    "Thông báo thành công, file xuất hiện trong danh sách với badge 'txt'")
def _(page):
    p = DATA / "ui_upload_test.txt"
    p.write_text("Căng tin công ty mở cửa từ 11h00 đến 13h30 hằng ngày.", encoding="utf-8")
    open_documents(page)
    page.set_input_files("#fileUploadInput", str(p))
    page.wait_for_timeout(1000)
    tmsg = toasts(page)
    page.wait_for_function("document.querySelector('#documentsList').innerText.includes('ui_upload_test.txt')", timeout=120000)
    page.wait_for_timeout(500)
    titles = doc_titles(page)
    ok = "ui_upload_test.txt" in titles
    return f"Toast: {tmsg}; có trong danh sách: {ok}", ok, shot(page, "UI_TIEN_03")


@tc("UI_TIEN_04", "TIEN", "Upload nhiều file cùng lúc",
    "1. Bấm Upload, chọn 2 file ui_multi_a.txt, ui_multi_b.txt",
    "Cả 2 file xuất hiện trong danh sách")
def _(page):
    files = []
    for n, t in [("ui_multi_a.txt", "Bãi đỗ xe ở tầng hầm B2."), ("ui_multi_b.txt", "Wifi khách: SaoMai-Guest.")]:
        p = DATA / n
        p.write_text(t, encoding="utf-8")
        files.append(str(p))
    open_documents(page)
    page.set_input_files("#fileUploadInput", files)
    page.wait_for_function("(() => {const t=document.querySelector('#documentsList').innerText; return t.includes('ui_multi_a.txt') && t.includes('ui_multi_b.txt');})()", timeout=180000)
    titles = doc_titles(page)
    ok = "ui_multi_a.txt" in titles and "ui_multi_b.txt" in titles
    return f"Danh sách sau upload: {titles[:6]}", ok, shot(page, "UI_TIEN_04")


@tc("UI_TIEN_05", "TIEN", "Upload file định dạng không hỗ trợ (.zip)",
    "1. Bấm Upload, chọn archive.zip",
    "Hiển thị thông báo lỗi rõ ràng, file không xuất hiện trong danh sách")
def _(page):
    open_documents(page)
    page.set_input_files("#fileUploadInput", str(DATA / "archive.zip"))
    try:
        page.wait_for_function(
            "[...document.querySelectorAll('.toast')].some(t => /fail|error|invalid|uploaded|indexed/i.test(t.innerText))",
            timeout=120000)
    except Exception:
        pass
    tmsg = toasts(page)
    titles = doc_titles(page)
    err = bool(re.search(r"fail|error|lỗi|invalid", tmsg, re.I))
    return f"Toast: {tmsg}; zip trong danh sách: {'archive.zip' in titles}", err and "archive.zip" not in titles, shot(page, "UI_TIEN_05")


@tc("UI_TIEN_06", "TIEN", "Badge loại file hiển thị đúng phần mở rộng",
    "1. Context > Documents > Refresh  2. Quan sát badge từng dòng",
    "Badge trùng phần mở rộng file (md, txt, docx, pdf)")
def _(page):
    open_documents(page)
    rows = page.locator("#documentsList .source-row")
    bad = []
    for i in range(rows.count()):
        t = rows.nth(i).locator(".source-title").inner_text().strip()
        b = rows.nth(i).locator(".badge").inner_text().strip().lower()
        ext = t.rsplit(".", 1)[-1].lower()[:5] if "." in t else ""
        if ext and b != ext:
            bad.append(f"{t}->{b}")
    return f"{rows.count()} dòng; sai badge: {bad[:4]}", not bad, shot(page, "UI_TIEN_06")


# ------------------------------- VINH ---------------------------------------
@tc("UI_VINH_01", "VINH", "Thông tin mỗi dòng tài liệu",
    "1. Context > Documents > Refresh",
    "Mỗi dòng có tên file, 'artifact · collection', badge, nút Delete")
def _(page):
    open_documents(page)
    row = page.locator("#documentsList .source-row").first
    meta = row.locator(".source-meta").inner_text()
    has_del = row.get_by_role("button", name="Delete").count() == 1
    ok = "·" in meta and "nhom11" in meta and has_del
    return f"meta='{meta}', có Delete: {has_del}", ok, shot(page, "UI_VINH_01")


@tc("UI_VINH_02", "VINH", "Nút Refresh đồng bộ tài liệu nạp từ API",
    "1. Nạp tài liệu vinh_ui_<giờ>.txt bằng API  2. Bấm Refresh trên UI",
    "vinh_ui_<giờ>.txt xuất hiện trong danh sách")
def _(page):
    r = c.ingest_text("Kiểm tra làm mới danh sách " + VINH_ART, VINH_ART, file_name=VINH_FILE)
    open_documents(page, expect=VINH_FILE)
    ok = VINH_FILE in doc_titles(page)
    return f"Nạp API HTTP {r.status_code}; có {VINH_FILE} trên UI sau Refresh: {ok}", ok, shot(page, "UI_VINH_02")


@tc("UI_VINH_03", "VINH", "Hủy thao tác xóa tài liệu",
    "1. Bấm Delete ở dòng vinh_ui_<giờ>.txt  2. Chọn Cancel trong hộp xác nhận",
    "Tài liệu vẫn còn trong danh sách và trên server")
def _(page):
    open_documents(page, expect=VINH_FILE)
    page.once("dialog", lambda d: d.dismiss())
    page.locator("#documentsList .source-row", has_text=VINH_FILE).get_by_role("button", name="Delete").click()
    page.wait_for_timeout(1500)
    still_ui = VINH_FILE in doc_titles(page)
    still_api = VINH_ART in {d["artifact"] for d in c.list_docs().json()["data"]}
    return f"Còn trên UI: {still_ui}, còn trên server: {still_api}", still_ui and still_api, shot(page, "UI_VINH_03")


@tc("UI_VINH_04", "VINH", "Xóa tài liệu có xác nhận",
    "1. Bấm Delete ở dòng vinh_ui_<giờ>.txt  2. Bấm OK",
    "Toast 'Document deleted.', dòng biến mất, server không còn artifact")
def _(page):
    open_documents(page, expect=VINH_FILE)
    msgs = []
    page.once("dialog", lambda d: (msgs.append(d.message), d.accept()))
    page.locator("#documentsList .source-row", has_text=VINH_FILE).get_by_role("button", name="Delete").click()
    try:
        page.wait_for_function("[...document.querySelectorAll('.toast')].some(t => /deleted|failed/i.test(t.innerText))", timeout=300000)
    except Exception:
        pass
    page.wait_for_timeout(800)
    tmsg = toasts(page)
    gone_ui = VINH_FILE not in doc_titles(page)
    gone_api = VINH_ART not in {d["artifact"] for d in c.list_docs().json()["data"]}
    return f"Hộp thoại: '{msgs[:1]}'; Toast: {tmsg}; mất trên UI {gone_ui}, server {gone_api}", gone_ui and gone_api, shot(page, "UI_VINH_04")


@tc("UI_VINH_05", "VINH", "Menu thao tác theo Style Guide (Preview, Search, Delete)",
    "1. Quan sát các thao tác của một dòng tài liệu",
    "Có Preview, Search và Delete (STYLE_GUIDE.md mục Documents)")
def _(page):
    open_documents(page)
    row = page.locator("#documentsList .source-row").first
    labels = row.locator(".panel-actions button").all_inner_texts()
    ok = all(x in labels for x in ["Preview", "Search", "Delete"])
    return f"Các nút có: {labels}", ok, shot(page, "UI_VINH_05")


@tc("UI_VINH_06", "VINH", "Trạng thái lập chỉ mục phản ánh thực tế",
    "1. Upload file  2. Quan sát trạng thái trong khi đang xử lý",
    "Hiển thị 'Processing' khi đang nạp, 'Indexed' khi xong, 'Failed' khi lỗi")
def _(page):
    src = Path(c.__file__).resolve().parents[2] / "source_code" / "ui" / "index.html"
    html = src.read_text(encoding="utf-8")
    hard = 'status: "Indexed"' in html
    has_proc = "Processing" in html
    return f"index.html gán cứng status 'Indexed' cho mọi tài liệu: {hard}; có trạng thái Processing: {has_proc}", (not hard), shot(page, "UI_VINH_06")


@tc("UI_VINH_07", "VINH", "Hiển thị trạng thái rỗng khi collection không có tài liệu",
    "1. Settings: Collection = empty_col_ui, Save  2. Context > Documents > Refresh",
    "Hiển thị 'No documents loaded...'")
def _(page):
    page.click("#settingsNav")
    page.fill("#defaultCollection", "empty_col_ui")
    page.click("#saveConnectionButton")
    page.wait_for_timeout(800)
    open_documents(page)
    txt = page.inner_text("#documentsList")
    ok = "No documents" in txt
    return f"Nội dung: '{txt[:80]}'", ok, shot(page, "UI_VINH_07")


# ------------------------------- DUY ----------------------------------------
PENDING_JS = "document.querySelectorAll('.thinking-text, .message.assistant.loading').length"


def wait_answer(page, timeout=300):
    """Chờ tới khi không còn chỉ báo 'Working'/loading liên tục 4 giây."""
    t0 = time.time()
    seen = False
    stable = 0
    while time.time() - t0 < timeout:
        n = page.evaluate(PENDING_JS)
        if n:
            seen = True
            stable = 0
        else:
            stable += 1
            if stable >= 4 and (seen or time.time() - t0 > 10):
                break
        page.wait_for_timeout(1000)
    return seen


def ask_in_chat(page, question, timeout=300, load_docs=True):
    if load_docs:
        open_documents(page)  # luồng thực tế: người dùng mở Documents và Refresh trước khi hỏi
    page.click("#newChatButton")
    page.wait_for_timeout(800)
    page.fill("#composerInput", question)
    t0 = time.time()
    page.click("button.send[aria-label='Send']")
    page.wait_for_timeout(700)
    loading_seen = page.evaluate(PENDING_JS) > 0
    wait_answer(page, timeout)
    page.wait_for_timeout(800)
    dt = time.time() - t0
    bubbles = page.locator(".message.assistant .message-bubble")
    ans = bubbles.last.inner_text() if bubbles.count() else ""
    return ans, dt, loading_seen


@tc("UI_DUY_01", "DUY", "Hỏi đáp có tài liệu qua giao diện chat",
    "1. New Chat (Documents bật mặc định)  2. Nhập 'Phòng máy chủ đặt ở tầng mấy?'  3. Send",
    "Câu trả lời hiển thị trong bong bóng trợ lý, nêu 'tầng 7'")
def _(page):
    ans, dt, _ = ask_in_chat(page, "Phòng máy chủ của công ty Sao Mai đặt ở tầng mấy?")
    ok = bool(re.search(r"7|bảy|seven", ans, re.I))
    return f"[{dt:.0f}s] {ans[:220]}", ok, shot(page, "UI_DUY_01")


@tc("UI_DUY_02", "DUY", "Chỉ báo đang chờ phản hồi",
    "1. Gửi câu hỏi  2. Quan sát ngay sau khi gửi",
    "Hiển thị avatar PrivateGPT với hiệu ứng 'breathing' trong lúc chờ")
def _(page):
    page.click("#newChatButton")
    page.fill("#composerInput", "Liên hệ phòng Nhân sự qua email nào?")
    page.click("button.send[aria-label='Send']")
    page.wait_for_timeout(700)
    seen = page.evaluate(PENDING_JS) > 0
    name = shot(page, "UI_DUY_02")
    wait_answer(page)
    return f"Thấy chỉ báo chờ: {seen}", seen, name


@tc("UI_DUY_03", "DUY", "Không hiển thị thẻ <citation> thô",
    "1. Quan sát câu trả lời có tài liệu",
    "Không có chuỗi '<citation' trong nội dung hiển thị; trích dẫn là nút số tròn")
def _(page):
    ans, dt, _ = ask_in_chat(page, "Dữ liệu mức Mật phải được mã hóa bằng thuật toán gì? Trích dẫn nguồn.")
    raw = "<citation" in ans
    btns = page.locator(".citation-button").count()
    return f"[{dt:.0f}s] thẻ thô: {raw}, số nút trích dẫn: {btns}; {ans[:150]}", not raw, shot(page, "UI_DUY_03")


@tc("UI_DUY_04", "DUY", "Mở popup trích dẫn",
    "1. Bấm vào nút số trích dẫn trong câu trả lời",
    "Mở popup kính mờ hiển thị metadata và đoạn trích nguồn")
def _(page):
    ans, dt, _ = ask_in_chat(page, "Hotline báo cáo sự cố bảo mật là gì? Hãy trích dẫn nguồn.")
    btn = page.locator(".citation-button")
    if btn.count() == 0:
        return f"[{dt:.0f}s] Không có nút trích dẫn nào được sinh ra -> không mở được popup. {ans[:120]}", False, shot(page, "UI_DUY_04")
    btn.first.click()
    page.wait_for_timeout(800)
    ok = page.locator(".citation-excerpt").count() > 0
    return f"Popup có đoạn trích: {ok}", ok, shot(page, "UI_DUY_04")


@tc("UI_DUY_05", "DUY", "Khối công cụ hiển thị dạng thu gọn",
    "1. Quan sát câu trả lời có gọi semantic_search",
    "Khối tool use / tool result hiển thị dạng <details> thu gọn")
def _(page):
    ans, dt, _ = ask_in_chat(page, "Vi phạm quy định bảo mật lần thứ hai bị xử lý thế nào?")
    n = page.locator(".message.assistant details").count()
    opened = page.locator(".message.assistant details[open]").count()
    return f"[{dt:.0f}s] số khối details: {n}, đang mở: {opened}", n > 0 and opened == 0, shot(page, "UI_DUY_05")


@tc("UI_DUY_07", "DUY", "Hỏi đáp khi trình duyệt chưa tải danh sách tài liệu",
    "1. Mở /ui trên trình duyệt mới (chưa vào Context > Documents)  2. New Chat  3. Hỏi 'Phòng máy chủ đặt ở tầng mấy?'",
    "Chat vẫn dùng tài liệu của collection đã cấu hình và trả lời 'tầng 7'")
def _(page):
    ans, dt, _ = ask_in_chat(page, "Phòng máy chủ của công ty Sao Mai đặt ở tầng mấy?", load_docs=False)
    n = page.locator(".message.assistant details").count()
    ok = bool(re.search(r"7|bảy|seven", ans, re.I))
    return f"[{dt:.0f}s] số khối công cụ: {n}; {ans[:200]}", ok, shot(page, "UI_DUY_07")


@tc("UI_DUY_06", "DUY", "Bật/tắt Documents trong menu Tools",
    "1. Mở menu Tools/Add trong composer  2. Quan sát công tắc Documents",
    "Có công tắc Documents và trạng thái được lưu theo từng chat")
def _(page):
    page.click("#newChatButton")
    page.wait_for_timeout(500)
    page.click("#composerAddMenuButton")
    page.wait_for_timeout(800)
    txt = page.locator(".menu-panel.open, #toolsMenu").first.inner_text()
    ok = "Documents" in txt
    return f"Menu: {txt[:120]!r}", ok, shot(page, "UI_DUY_06")


# ------------------------------- MẠNH ---------------------------------------
@tc("UI_MANH_01", "MANH", "Tạo hội thoại mới",
    "1. Bấm New Chat", "Xuất hiện 'New chat' được tô sáng ở đầu danh sách")
def _(page):
    before = page.locator("button.chat-row").count()
    page.click("#newChatButton")
    page.wait_for_timeout(500)
    after = page.locator("button.chat-row").count()
    active = page.locator("button.chat-row.active .chat-row-title").inner_text()
    return f"Số chat {before}->{after}, active='{active}'", after == before + 1 and active == "New chat", shot(page, "UI_MANH_01")


@tc("UI_MANH_02", "MANH", "Đổi tên hội thoại",
    "1. Hover dòng chat, bấm Rename  2. Nhập 'Hỏi về nghỉ phép'  3. Lưu",
    "Tên mới hiển thị trên sidebar và tiêu đề chat")
def _(page):
    page.click("#newChatButton")
    page.wait_for_timeout(400)
    row = page.locator(".chat-row.active").first
    row.hover()
    page.locator(".chat-row.active [data-action='rename']").first.dispatch_event("click")
    page.fill("#chatTitleInput", "Hỏi về nghỉ phép")
    page.keyboard.press("Enter")
    page.wait_for_timeout(600)
    title = page.locator("button.chat-row.active .chat-row-title").inner_text()
    return f"Tiêu đề: '{title}'", title == "Hỏi về nghỉ phép", shot(page, "UI_MANH_02")


@tc("UI_MANH_03", "MANH", "Tiêu đề dài bị cắt bằng dấu '…'",
    "1. Đổi tên chat thành chuỗi 120 ký tự", "Tiêu đề bị cắt, không có thanh cuộn ngang ở sidebar")
def _(page):
    page.click("#newChatButton")
    row = page.locator(".chat-row.active").first
    row.hover()
    page.locator(".chat-row.active [data-action='rename']").first.dispatch_event("click")
    page.fill("#chatTitleInput", "Tiêu đề rất dài " * 8)
    page.keyboard.press("Enter")
    page.wait_for_timeout(600)
    res = page.evaluate("""() => {const t=document.querySelector('button.chat-row.active .chat-row-title');
        const l=document.querySelector('#chatList');
        return {ov: getComputedStyle(t).textOverflow, trunc: t.scrollWidth > t.clientWidth, hscroll: l.scrollWidth > l.clientWidth};}""")
    return f"{res}", res["ov"] == "ellipsis" and res["trunc"] and not res["hscroll"], shot(page, "UI_MANH_03")


@tc("UI_MANH_04", "MANH", "Xóa hội thoại có xác nhận",
    "1. Bấm Delete trên dòng chat  2. Xác nhận", "Hội thoại biến mất khỏi danh sách")
def _(page):
    page.click("#newChatButton")
    before = page.locator("button.chat-row").count()
    row = page.locator(".chat-row.active").first
    row.hover()
    page.locator(".chat-row.active [data-action='delete']").first.dispatch_event("click")
    page.wait_for_timeout(500)
    dlg = page.locator(".modal-card:visible").last
    dtxt = dlg.inner_text()[:80] if dlg.count() else ""
    page.locator(".modal-card:visible button:has-text('Delete')").last.click()
    page.wait_for_timeout(600)
    after = page.locator("button.chat-row").count()
    return f"Hộp thoại: '{dtxt}'; số chat {before}->{after}", after == before - 1, shot(page, "UI_MANH_04")


@tc("UI_MANH_05", "MANH", "Hội thoại được lưu sau khi tải lại trang",
    "1. Tạo chat, đặt tên 'Lưu trữ test'  2. Reload (F5)", "Chat 'Lưu trữ test' vẫn còn")
def _(page):
    page.click("#newChatButton")
    page.locator(".chat-row.active").first.hover()
    page.locator(".chat-row.active [data-action='rename']").first.dispatch_event("click")
    page.fill("#chatTitleInput", "Lưu trữ test")
    page.keyboard.press("Enter")
    page.wait_for_timeout(500)
    page.reload()
    page.wait_for_timeout(1500)
    titles = page.locator(".chat-row-title").all_inner_texts()
    return f"Danh sách sau reload: {titles[:5]}", "Lưu trữ test" in titles, shot(page, "UI_MANH_05")


@tc("UI_MANH_06", "MANH", "Danh sách mô hình trong dropdown",
    "1. Mở chat  2. Bấm nút chọn mô hình", "Liệt kê qwen2.5:3b và llama3.2:latest từ /v1/models")
def _(page):
    page.click("#newChatButton")
    wait_models(page)
    page.click("#modelSelectBtn")
    page.wait_for_timeout(1000)
    txt = page.inner_text("#modelOptions")
    ok = "qwen2.5:3b" in txt and "llama3.2" in txt
    return f"Dropdown: {txt[:120]!r}", ok, shot(page, "UI_MANH_06")


@tc("UI_MANH_07", "MANH", "Shift+Enter xuống dòng, không gửi",
    "1. Gõ 'dòng 1', Shift+Enter, 'dòng 2'", "Ô nhập có 2 dòng, không có tin nhắn nào được gửi")
def _(page):
    page.click("#newChatButton")
    page.click("#composerInput")
    page.keyboard.type("dòng 1")
    page.keyboard.press("Shift+Enter")
    page.keyboard.type("dòng 2")
    v = page.input_value("#composerInput")
    sent = page.locator(".message.user").count()
    return f"value={v!r}, số tin đã gửi={sent}", v == "dòng 1\ndòng 2" and sent == 0, shot(page, "UI_MANH_07")


@tc("UI_MANH_08", "MANH", "Validate Base URL không hợp lệ",
    "1. Settings  2. Base URL = 'abc xyz'  3. Save", "Báo lỗi URL không hợp lệ, không lưu")
def _(page):
    page.click("#settingsNav")
    page.fill("#privateGptBaseUrl", "abc xyz")
    page.click("#saveConnectionButton")
    page.wait_for_timeout(800)
    tmsg = toasts(page)
    stored = page.evaluate("JSON.parse(localStorage.getItem('privategpt-workbench-state-v1')).privateGptBaseUrl")
    name = shot(page, "UI_MANH_08")
    page.fill("#privateGptBaseUrl", "http://localhost:8080")
    page.click("#saveConnectionButton")
    return f"Toast: {tmsg}; giá trị đã lưu: {stored!r}", stored != "abc xyz", name


@tc("UI_MANH_09", "MANH", "Basic auth chỉ nhập username",
    "1. Settings  2. Username='admin', Password trống  3. Save", "Thông báo 'Enter both username and password...'")
def _(page):
    open_auth(page)
    page.fill("#privateGptUsername", "admin")
    page.fill("#privateGptPassword", "")
    page.click("#saveConnectionButton")
    page.wait_for_timeout(800)
    tmsg = toasts(page)
    name = shot(page, "UI_MANH_09")
    page.fill("#privateGptUsername", "")
    return f"Toast: {tmsg}", "both username and password" in tmsg, name


@tc("UI_MANH_10", "MANH", "API Debugger che thông tin xác thực",
    "1. Settings: username/password = test/test123, Save  2. Bấm Test API  3. Mở API Debugger, xem header",
    "Header Authorization hiển thị dạng che (redacted), không lộ chuỗi Basic")
def _(page):
    open_auth(page)
    page.fill("#privateGptUsername", "test")
    page.fill("#privateGptPassword", "test123")
    page.click("#saveConnectionButton")
    page.click("#testConnectionButton")
    page.wait_for_timeout(2500)
    page.click("#apiDebuggerNav")
    page.wait_for_timeout(800)
    items = page.locator("#apiDebuggerScreen button, #apiDebuggerScreen .debug-event")
    if items.count():
        items.first.click()
        page.wait_for_timeout(500)
    txt = page.inner_text("#apiDebuggerScreen")
    leaked = "dGVzdDp0ZXN0MTIz" in txt  # base64("test:test123")
    name = shot(page, "UI_MANH_10")
    open_auth(page)
    page.fill("#privateGptUsername", "")
    page.fill("#privateGptPassword", "")
    page.click("#saveConnectionButton")
    return f"Lộ chuỗi Basic trong Debugger: {leaked}; có chữ 'redacted': {'redact' in txt.lower()}", not leaked, name


@tc("UI_MANH_11", "MANH", "Mật khẩu lưu trong localStorage",
    "1. Settings: nhập password 'S3cret!'  2. Save  3. Đọc localStorage",
    "Mật khẩu không được lưu dạng rõ (plaintext) trong localStorage")
def _(page):
    open_auth(page)
    page.fill("#privateGptUsername", "u1")
    page.fill("#privateGptPassword", "S3cret!")
    page.click("#saveConnectionButton")
    page.wait_for_timeout(500)
    raw = page.evaluate("localStorage.getItem('privategpt-workbench-state-v1')")
    plain = "S3cret!" in raw
    name = shot(page, "UI_MANH_11")
    page.fill("#privateGptUsername", "")
    page.fill("#privateGptPassword", "")
    page.click("#saveConnectionButton")
    return f"Mật khẩu dạng rõ trong localStorage: {plain}", not plain, name


@tc("UI_MANH_12", "MANH", "Giao diện ở độ rộng di động 375px",
    "1. Mở /ui với viewport 375x812", "Không có thanh cuộn ngang; ô nhập chat dùng được")
def _(page):
    page.set_viewport_size({"width": 375, "height": 812})
    page.reload()
    page.wait_for_timeout(1500)
    res = page.evaluate("({sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth})")
    vis = page.locator("#composerInput").is_visible()
    return f"scrollWidth={res['sw']}, clientWidth={res['cw']}, composer hiển thị: {vis}", res["sw"] <= res["cw"] and vis, shot(page, "UI_MANH_12")


def main():
    args = [a.upper() for a in sys.argv[1:]]
    ids = {a for a in args if a.startswith("UI_")}
    owners = {a for a in args if not a.startswith("UI_")} or ({"TIEN", "VINH", "DUY", "MANH"} if not ids else set())
    results = json.loads(LOG.read_text(encoding="utf-8")) if LOG.exists() else {}
    with sync_playwright() as p:
        for case in CASES:
            if case["owner"] not in owners and case["id"] not in ids:
                continue
            b, ctx, page = new_page(p)
            t = time.time()
            try:
                actual, ok, img = case["fn"](page)
            except Exception as e:  # noqa: BLE001
                img = shot(page, case["id"] + "_error")
                actual, ok = f"EXCEPTION {type(e).__name__}: {str(e)[:200]}", False
            b.close()
            rec = {k: v for k, v in case.items() if k != "fn"}
            rec.update(actual=actual, status="Pass" if ok else "Fail", screenshot=img,
                       seconds=round(time.time() - t, 1))
            results[case["id"]] = rec
            print(f"{case['id']:11s} {rec['status']:4s} {rec['seconds']:6.1f}s {actual[:150]}", flush=True)
            LOG.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
