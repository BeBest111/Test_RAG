from playwright.sync_api import sync_playwright

from ui_common import new_page, shot

with sync_playwright() as p:
    b, ctx, page = new_page(p)
    print("title:", page.title())
    print(shot(page, "explore_home"))
    page.click("#contextNav")
    page.wait_for_timeout(1500)
    print(shot(page, "explore_context"))
    print(page.inner_text("#contextScreen")[:800])
    b.close()
