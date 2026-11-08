"""Bổ sung vào blackbox_results.json các test case đã thực thi bằng script riêng:
- BB_TIEN_23: performance/concurrency_ingest_test.py
- BB_DUY_15 : debug_retrieval.py với PGPT_MODEL=llama3.2 (lượt chạy smoke ngày 26/10)
- BB_MANH_17: quan sát khi pull qwen2.5:3b lúc server đang chạy
"""

import json
from pathlib import Path

LOGS = Path(__file__).resolve().parents[2] / "logs"
LOG = LOGS / "blackbox_results.json"
d = json.loads(LOG.read_text(encoding="utf-8"))
conc = json.loads((LOGS / "concurrency_results.json").read_text(encoding="utf-8"))[-1]
codes = [s for _, s, _ in conc["ingest_status"]]

d["BB_TIEN_23"] = dict(
    id="BB_TIEN_23", owner="TIEN", technique="Kiểm thử đồng thời (concurrency)", title="Nạp đồng thời 6 tài liệu nhỏ",
    data="6 luồng song song POST /v1/artifacts/ingest vào collection mới " + conc["collection"],
    expected="6/6 HTTP 200 và cả 6 có trong danh sách",
    actual=f"Mã trả về: {codes}; trong danh sách chỉ có {conc['listed']}; thiếu {conc['missing_from_list']}; "
           f"xem nội dung: {conc['content_status']}",
    status="Pass" if not conc["missing_from_list"] and all(c == 200 for c in codes) else "Fail", seconds=20.0)

d["BB_DUY_15"] = dict(
    id="BB_DUY_15", owner="DUY", technique="Kiểm thử cấu hình (so sánh mô hình)", title="Hỏi đáp RAG với model llama3.2:3b",
    data="model=llama3.2:latest, 'Nhân viên dưới 5 năm thâm niên được bao nhiêu ngày phép năm?'",
    expected="Truy xuất được tài liệu nghỉ phép, trả lời 12 ngày",
    actual="[41s] LLM gọi semantic_search với artifacts=[null, null] -> tool trả 'artifacts rejected, nothing was searched'; "
           "câu trả lời bịa: 'nhân viên dưới 5 năm thâm niên được phép nghỉ phép tối đa 10 ngày' / '20 ngày'. "
           "Lần thử với artifacts=['nghi_phep']: LLM truyền tên 'LĐLĐ' -> tiếp tục bị từ chối.",
    status="Fail", seconds=41.2)

d["BB_MANH_17"] = dict(
    id="BB_MANH_17", owner="MANH", technique="Đoán lỗi (cập nhật cấu hình nóng)", title="Phát hiện model mới thêm vào Ollama khi server đang chạy",
    data="ollama pull qwen2.5:3b khi server đang chạy; GET /v1/models; POST /v1/messages model=qwen2.5:3b",
    expected="Model mới xuất hiện (hoặc có cơ chế làm mới)",
    actual="GET /v1/models chỉ trả ['llama3.2:latest']; /v1/messages trả 400 \"Model 'qwen2.5:3b' not found. Available: {'llama3.2:latest', 'default'}\"; "
           "chỉ xuất hiện sau khi khởi động lại server",
    status="Fail", seconds=2.1)

LOG.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print("ok", d["BB_TIEN_23"]["status"])
