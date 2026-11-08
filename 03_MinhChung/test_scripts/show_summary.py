"""In bảng tổng kết kết quả kiểm thử chính thức của Nhóm 11 ra terminal."""

import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOGS = HERE.parent / "logs"
sys.path.insert(0, str(HERE / "report_gen"))
from bugs import BUGS, ENV_BUGS  # noqa: E402

MEMBERS = [("TIEN", "Nguyễn Minh Tiến", "Nạp tài liệu"), ("VINH", "Nguyễn Bá Quang Vinh", "Quản lý tài liệu"),
           ("DUY", "Vũ Đức Duy", "Hỏi đáp RAG"), ("MANH", "Bùi Văn Mạnh", "Hội thoại & cấu hình")]

bb = json.loads((LOGS / "blackbox_results.json").read_text(encoding="utf-8"))
ui = json.loads((LOGS / "ui_results.json").read_text(encoding="utf-8"))
ut = {t.get("name"): t.find("failure") is None for t in ET.parse(LOGS / "unit_nhom11.xml").getroot().iter("testcase")}

print()
print("=" * 86)
print("  TỔNG KẾT KẾT QUẢ KIỂM THỬ CHÍNH THỨC – NHÓM 11 – PrivateGPT".center(86))
print("=" * 86)
print(f"  {'Thành viên':<24}{'Chức năng':<22}{'Giao diện':>10}{'Đơn vị':>9}{'Hộp đen':>10}{'Đạt':>9}")
print("  " + "-" * 82)
TP = TT = 0
for k, n, f in MEMBERS:
    u = [v["status"] for v in ui.values() if v["owner"] == k]
    t = [ok for name, ok in ut.items() if name.startswith(f"test_UT_{k}_")]
    b = [v["status"] for kk, v in bb.items() if not kk.startswith("_") and v["owner"] == k]
    p = u.count("Pass") + sum(t) + b.count("Pass")
    tot = len(u) + len(t) + len(b)
    TP += p
    TT += tot
    print(f"  {n:<24}{f:<22}{u.count('Pass'):>5}/{len(u):<4}{sum(t):>4}/{len(t):<4}{b.count('Pass'):>5}/{len(b):<4}{p / tot * 100:>7.0f}%")
print("  " + "-" * 82)
print(f"  TỔNG CỘNG: {TP}/{TT} test case đạt = {TP / TT * 100:.0f}%")
sev = Counter(b["severity"] for b in BUGS)
print()
print(f"  Lỗi phát hiện: {len(BUGS)} lỗi chức năng/bảo mật/hiệu năng (Cao {sev['Cao']} · Trung bình {sev['Trung bình']} · Thấp {sev['Thấp']})")
print(f"                 + {len(ENV_BUGS)} lỗi cài đặt trên Windows + 16 lỗi tài liệu")
print()
print("  5 LỖI NGHIÊM TRỌNG NHẤT:")
for bid in ["BUG-01", "BUG-02", "BUG-09", "BUG-16", "BUG-17"]:
    b = next(x for x in BUGS if x["id"] == bid)
    print(f"   [{b['severity']}] {b['id']}: {b['title']}")
print("=" * 86)
