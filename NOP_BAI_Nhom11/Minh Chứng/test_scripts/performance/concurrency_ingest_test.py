"""Kiểm thử nạp đồng thời: 6 tài liệu nhỏ nạp song song vào collection mới,
sau đó kiểm tra tất cả có trong danh sách và xem được nội dung không.
Kết quả ghi ../../logs/concurrency_results.json
"""

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pgpt_client as c  # noqa: E402

COL = "nhom11_conc_" + time.strftime("%H%M%S")
N = 6


def ingest(i):
    t = time.time()
    r = c.ingest_text(f"Tài liệu đồng thời số {i}: phòng họp số {i} ở tầng {i + 1}.", f"conc_{i}", collection=COL,
                      file_name=f"conc_{i}.txt")
    return i, r.status_code, round(time.time() - t, 1)


with ThreadPoolExecutor(max_workers=N) as ex:
    res = list(ex.map(ingest, range(N)))
print("ingest:", res)
time.sleep(3)
listed = {d["artifact"] for d in c.list_docs(COL).json()["data"]}
content = {}
for i in range(N):
    r = c.client.post("/v1/artifacts/content", json={"context_filter": {"collection": COL, "artifacts": [f"conc_{i}"]}})
    content[f"conc_{i}"] = r.status_code
out = {
    "collection": COL,
    "ingest_status": res,
    "listed": sorted(listed),
    "missing_from_list": [f"conc_{i}" for i in range(N) if f"conc_{i}" not in listed],
    "content_status": content,
}
print(json.dumps(out, ensure_ascii=False, indent=1))
log = Path(__file__).resolve().parents[2] / "logs" / "concurrency_results.json"
runs = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
runs.append(out)
log.write_text(json.dumps(runs, ensure_ascii=False, indent=1), encoding="utf-8")
