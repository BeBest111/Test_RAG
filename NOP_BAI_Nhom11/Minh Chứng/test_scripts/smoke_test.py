"""Smoke test: nạp 5 tài liệu mẫu và hỏi 1 câu RAG."""
import json
import time

import pgpt_client as c

for f, a in [
    ("chinh_sach_nghi_phep.md", "nghi_phep"),
    ("quy_dinh_bao_mat.txt", "bao_mat"),
    ("quy_trinh_hoan_tien.docx", "hoan_tien"),
    ("bang_gia.pdf", "bang_gia"),
    ("product_faq_en.md", "faq"),
]:
    t = time.time()
    r = c.ingest_file(f, a)
    print(f, r.status_code, round(time.time() - t, 1), r.text[:160])

print(c.list_docs().text[:600])
r, dt = c.rag_ask("Nhân viên dưới 5 năm thâm niên được bao nhiêu ngày phép năm?")
print(r.status_code, round(dt, 1))
j = r.json()
print(c.answer_text(j)[:600])
print(json.dumps(c.citations_of(j)[:2], ensure_ascii=False))
print([b.get("type") for b in j.get("content", [])], j.get("stop_reason"), j.get("usage"))
