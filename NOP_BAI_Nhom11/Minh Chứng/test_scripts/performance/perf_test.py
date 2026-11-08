"""Kiểm thử hiệu năng đơn giản (tải đồng thời) cho PrivateGPT.

PERF_LIST   : 20 luồng x 5 request GET /v1/artifacts/list (100 request)
PERF_MODELS : 50 request tuần tự GET /v1/models
PERF_INGEST : nạp 5 văn bản nhỏ tuần tự
Kết quả ghi ../../logs/perf_results.json
"""

import json
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pgpt_client as c  # noqa: E402

LOG = Path(__file__).resolve().parents[2] / "logs" / "perf_results.json"


def pct(xs, p):
    xs = sorted(xs)
    k = max(0, min(len(xs) - 1, int(round(p / 100 * (len(xs) - 1)))))
    return xs[k]


def stats(name, lat, errors, total, wall):
    return {
        "test": name, "requests": total, "errors": errors,
        "error_rate_pct": round(errors / total * 100, 1),
        "avg_s": round(statistics.mean(lat), 3) if lat else None,
        "p50_s": round(pct(lat, 50), 3) if lat else None,
        "p95_s": round(pct(lat, 95), 3) if lat else None,
        "max_s": round(max(lat), 3) if lat else None,
        "throughput_rps": round(total / wall, 2),
    }


def one(url, params=None):
    t = time.perf_counter()
    try:
        r = httpx.get(c.BASE_URL + url, params=params, timeout=60)
        return time.perf_counter() - t, r.status_code != 200
    except Exception:
        return time.perf_counter() - t, True


out = []
# PERF_LIST
t0 = time.perf_counter()
with ThreadPoolExecutor(max_workers=20) as ex:
    res = list(ex.map(lambda _: one("/v1/artifacts/list", {"collection": c.COLLECTION}), range(100)))
out.append(stats("PERF_LIST – 100 request, 20 luồng đồng thời GET /v1/artifacts/list", [r[0] for r in res],
                 sum(r[1] for r in res), 100, time.perf_counter() - t0))
print(out[-1])

# PERF_MODELS
t0 = time.perf_counter()
res = [one("/v1/models") for _ in range(50)]
out.append(stats("PERF_MODELS – 50 request tuần tự GET /v1/models", [r[0] for r in res],
                 sum(r[1] for r in res), 50, time.perf_counter() - t0))
print(out[-1])

# PERF_INGEST
lat, err = [], 0
t0 = time.perf_counter()
for i in range(5):
    t = time.perf_counter()
    r = c.ingest_text(f"Văn bản hiệu năng số {i}: nội quy phòng họp tầng {i + 2}.", f"perf_{i}", collection="nhom11_perf",
                      file_name=f"perf_{i}.txt")
    lat.append(time.perf_counter() - t)
    err += r.status_code != 200
out.append(stats("PERF_INGEST – nạp tuần tự 5 văn bản ~60 byte", lat, err, 5, time.perf_counter() - t0))
print(out[-1])

# PERF_RAG – lấy từ kết quả hộp đen của Duy
bb = json.loads((LOG.parent / "blackbox_results.json").read_text(encoding="utf-8"))
rag = bb.get("_rag_times", [])
if rag:
    out.append(stats(f"PERF_RAG – {len(rag)} câu hỏi RAG (từ BB_DUY_*), qwen2.5:3b trên CPU", rag, 0, len(rag), sum(rag)))
    print(out[-1])

LOG.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
