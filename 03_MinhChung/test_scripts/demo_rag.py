"""DEMO trực tiếp luồng RAG qua API: nạp 1 tài liệu mới -> liệt kê -> hỏi đáp có trích dẫn."""

import json
import time

import pgpt_client as c

COL = "nhom11_demo"
ART = "demo_" + time.strftime("%H%M%S")
DOC = ("QUY ĐỊNH GIỜ GIẤC – CÔNG TY SAO MAI (tài liệu demo)\n"
       "1. Giờ làm việc buổi sáng bắt đầu lúc 8 giờ 00.\n"
       "2. Nhân viên đi muộn quá 15 phút bị trừ 50.000 đồng vào lương tháng.\n"
       "3. Nhân viên được nghỉ trưa từ 12 giờ 00 đến 13 giờ 15.\n")


def line(t=""):
    print(t, flush=True)


line("=" * 70)
line(" DEMO LUỒNG RAG – PrivateGPT (Nhóm 11)")
line("=" * 70)
line(f"[1] Nạp tài liệu '{ART}.txt' vào collection '{COL}' ...")
t = time.time()
r = c.ingest_text(DOC, ART, collection=COL, file_name=f"{ART}.txt")
line(f"    -> HTTP {r.status_code} sau {time.time() - t:.1f} giây")

line(f"\n[2] Liệt kê tài liệu trong collection '{COL}':")
for d in c.list_docs(COL).json().get("data", []):
    line(f"    - {d['artifact']}  ({d['doc_metadata'].get('file_name')})")

q = "Nhân viên đi muộn quá 15 phút bị phạt bao nhiêu tiền?"
line(f"\n[3] Hỏi: {q}")
line("    (mô hình qwen2.5:3b chạy trên CPU – chờ khoảng 30-90 giây...)")
r, dt = c.rag_ask(q, artifacts=[ART], collection=COL)
j = r.json()
for b in j.get("content", []):
    if b.get("type") == "server_tool_use":
        line(f"    LLM gọi công cụ semantic_search, truy vấn: {json.dumps(b.get('input'), ensure_ascii=False)}")
ans = c.answer_text(j)
line(f"\n[4] Trả lời (sau {dt:.0f} giây):")
line("    " + ans.replace("\n", "\n    "))
cits = c.citations_of(j)
line(f"\n[5] Trích dẫn: {json.dumps(cits, ensure_ascii=False) if cits else 'không có'}")
line("\nĐáp án đúng theo tài liệu: 50.000 đồng.")
line("=" * 70)
