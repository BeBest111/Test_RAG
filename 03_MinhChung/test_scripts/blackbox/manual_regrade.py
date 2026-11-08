"""Đánh giá lại thủ công (human review) một số test case RAG mà bộ chấm tự động (regex) chấm chưa chính xác.
Mỗi thay đổi đều ghi chú lý do vào trường 'actual'."""

import json
from pathlib import Path

LOG = Path(__file__).resolve().parents[2] / "logs" / "blackbox_results.json"
d = json.loads(LOG.read_text(encoding="utf-8"))

REGRADE = {
    "BB_DUY_06": ("Pass", "[Đánh giá lại thủ công] Mô hình trả lời 'does not directly identify the CEO' = từ chối đúng, không bịa tên; "
                          "regex ban đầu chưa bắt cụm này."),
    "BB_DUY_08": ("Fail", "[Đánh giá lại thủ công] Có citation nhưng trỏ SAI tài liệu: artifact_id='noi_quy' trong khi hotline SOC 1900-7777 "
                          "nằm ở 'bao_mat'; mô hình còn tự diễn giải SOC = 'Special Operations Command' (bịa)."),
    "BB_DUY_14": ("Fail", "[Đánh giá lại thủ công] Câu trả lời mở đầu bằng tiếng Anh ('The relevant information...'), chỉ chép nguyên văn đoạn "
                          "tiếng Việt từ tài liệu -> không đáp ứng 'trả lời bằng tiếng Việt'."),
}
for k, (st, note) in REGRADE.items():
    if k in d and not d[k]["actual"].startswith("[Đánh giá lại"):
        d[k]["actual"] = note + " | Kết quả gốc: " + d[k]["actual"]
        d[k]["status"] = st
LOG.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print({k: d[k]["status"] for k in REGRADE})
