"""Client nhỏ gọi API PrivateGPT dùng chung cho các bộ test của Nhóm 11."""

import base64
import os
import time
from pathlib import Path

import httpx

BASE_URL = os.environ.get("PGPT_BASE_URL", "http://localhost:8080")
DATA_DIR = Path(__file__).resolve().parents[1] / "test_data"
COLLECTION = "nhom11"
MODEL = os.environ.get("PGPT_MODEL", "qwen2.5:3b")

client = httpx.Client(base_url=BASE_URL, timeout=600)


def b64_file(name: str) -> str:
    return base64.b64encode((DATA_DIR / name).read_bytes()).decode("ascii")


def ingest_file(name, artifact, collection=COLLECTION, file_name=None):
    body = {
        "artifact": artifact,
        "collection": collection,
        "input": {"type": "file", "value": b64_file(name)},
        "metadata": {"file_name": file_name or name},
    }
    return client.post("/v1/artifacts/ingest", json=body)


def ingest_text(text, artifact, collection=COLLECTION, file_name="note.txt"):
    body = {
        "artifact": artifact,
        "collection": collection,
        "input": {"type": "text", "value": text},
        "metadata": {"file_name": file_name},
    }
    return client.post("/v1/artifacts/ingest", json=body)


def list_docs(collection=COLLECTION):
    return client.get("/v1/artifacts/list", params={"collection": collection})


def delete_doc(artifact, collection=COLLECTION):
    return client.post(
        "/v1/artifacts/delete", json={"collection": collection, "artifact": artifact}
    )


def rag_ask(question, artifacts=None, collection=COLLECTION, history=None,
            citations=True, force_tool=True, max_tokens=512):
    messages = list(history or []) + [{"role": "user", "content": question}]
    body = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "stream": False,
        "system": {"citations": {"enabled": citations}},
        "messages": messages,
        "tools": [{"name": "semantic_search", "type": "semantic_search_v1"}],
        "tool_context": [
            {
                "type": "ingested_artifact",
                "context_filter": {
                    "collection": collection,
                    "artifacts": artifacts if artifacts is not None else [],
                },
            }
        ],
    }
    if force_tool:
        body["tool_choice"] = {"type": "tool", "name": "semantic_search"}
    t0 = time.perf_counter()
    r = client.post("/v1/messages", json=body)
    return r, time.perf_counter() - t0


def answer_text(resp_json) -> str:
    return "".join(
        b.get("text", "") for b in resp_json.get("content", []) if b.get("type") == "text"
    )


def citations_of(resp_json):
    out = []
    for b in resp_json.get("content", []):
        if b.get("type") == "text":
            out.extend(b.get("citations") or [])
    return out
