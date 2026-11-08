"""Tiện ích chung cho kiểm thử giao diện (Playwright + Microsoft Edge)."""

import json
import os
from pathlib import Path

BASE = "http://localhost:8080/ui"
SHOTS = Path(os.environ["DEMO_SHOTS"]) if os.environ.get("DEMO_SHOTS") else Path(__file__).resolve().parents[2] / "screenshots"
SHOTS.mkdir(parents=True, exist_ok=True)
STORAGE_KEY = "privategpt-workbench-state-v1"

SEED_STATE = {
    "privateGptBaseUrl": "http://localhost:8080",
    "onboarding": {"completed": True, "step": 2, "appearanceSkipped": True, "lastCheck": None},
    "context": {"documents": {"defaultCollection": "nhom11"}},
    "selectedModel": "qwen2.5:3b",
}


def seed_script(state=None):
    s = json.dumps(state or SEED_STATE)
    return (
        "if (!sessionStorage.getItem('nhom11_seeded')) {"
        f"  localStorage.setItem('{STORAGE_KEY}', JSON.stringify({s}));"
        "  sessionStorage.setItem('nhom11_seeded', '1');"
        "}"
    )


def new_page(p, width=1440, height=900, state=None):
    headed = os.environ.get("DEMO_HEADED") == "1"
    browser = p.chromium.launch(channel="msedge", headless=not headed, slow_mo=350 if headed else 0)
    ctx = browser.new_context(viewport={"width": width, "height": height}, locale="vi-VN")
    ctx.add_init_script(seed_script(state))
    page = ctx.new_page()
    page.goto(BASE)
    page.wait_for_timeout(1500)
    return browser, ctx, page


def shot(page, name):
    path = SHOTS / f"{name}.png"
    page.screenshot(path=str(path))
    return path.name
