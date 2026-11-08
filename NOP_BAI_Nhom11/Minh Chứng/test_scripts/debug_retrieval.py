import json
import sys

import pgpt_client as c

q = sys.argv[1] if len(sys.argv) > 1 else "Nhân viên dưới 5 năm thâm niên được bao nhiêu ngày phép năm?"
arts = sys.argv[2].split(",") if len(sys.argv) > 2 and sys.argv[2] else None
force = (sys.argv[3] != "auto") if len(sys.argv) > 3 else True
r, dt = c.rag_ask(q, artifacts=arts, force_tool=force)
j = r.json()
print("status", r.status_code, "time", round(dt, 1))
if r.status_code != 200:
    print(r.text[:800])
for b in j.get("content", []):
    t = b.get("type")
    if t == "server_tool_use":
        print("TOOL_USE input:", json.dumps(b.get("input"), ensure_ascii=False))
    elif t == "server_tool_result":
        s = json.dumps(b.get("content"), ensure_ascii=False)
        print("TOOL_RESULT:", s[:700])
    elif t == "text":
        print("TEXT:", b.get("text", "")[:400])
        print("CITATIONS:", json.dumps(b.get("citations"), ensure_ascii=False)[:300])
