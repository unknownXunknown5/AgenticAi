import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

from config import X_AUTH_TOKEN, X_CT0

COOKIES_FILE = Path("data/cookies.json")


def _get_playwright_cookies():
    """Load cookies from data/cookies.json or fall back to .env tokens."""
    cookies = []

    if COOKIES_FILE.exists():
        try:
            with open(COOKIES_FILE, "r", encoding="utf-8") as f:
                raw_cookies = json.load(f)

            for c in raw_cookies:
                cookie = {
                    "name": c["name"],
                    "value": c["value"],
                    "domain": c.get("domain", ".x.com"),
                    "path": c.get("path", "/"),
                    "secure": c.get("secure", True),
                    "httpOnly": c.get("httpOnly", False),
                }
                same_site = c.get("sameSite")
                if same_site in ["lax", "strict"]:
                    cookie["sameSite"] = same_site.capitalize()
                elif same_site == "no_restriction":
                    cookie["sameSite"] = "None"
                cookies.append(cookie)
            return cookies
        except Exception:
            pass

    if X_AUTH_TOKEN:
        cookies.append({
            "name": "auth_token",
            "value": X_AUTH_TOKEN,
            "domain": ".x.com",
            "path": "/",
            "secure": True,
            "httpOnly": True,
        })
        if X_CT0:
            cookies.append({
                "name": "ct0",
                "value": X_CT0,
                "domain": ".x.com",
                "path": "/",
                "secure": True,
                "httpOnly": False,
            })
        return cookies

    raise RuntimeError(
        "Twitter session cookies not found! Please provide data/cookies.json or set X_AUTH_TOKEN in .env"
    )


def publish_to_x(state):
    post = state.get("final_post") or state.get("draft")
    if not post:
        raise ValueError("No post text found in state.")

    cookies = _get_playwright_cookies()

    print("\n[Publisher] Launching browser to publish tweet via session...")

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                channel="chrome",
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
        except Exception:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )

        context.add_cookies(cookies)
        page = context.new_page()

        print("[Publisher] Opening https://x.com/home...")
        page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)

        if "login" in page.url or "i/flow" in page.url:
            browser.close()
            raise RuntimeError(
                "X session cookie is expired or invalid. Please update data/cookies.json or X_AUTH_TOKEN in .env"
            )

        # Ensure the compose button is in view and click it
        nav_button = page.locator('[data-testid="SideNav_NewTweet_Button"]').first
        # Scroll into view if needed
        try:
            nav_button.scroll_into_view_if_needed()
        except Exception:
            pass
        if nav_button.is_visible():
            nav_button.click()
            page.wait_for_timeout(1500)
        else:
            # Fallback: open compose page directly
            print("[Publisher] Side nav button not visible, opening compose URL directly")
            page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(1500)

        # Focus compose textarea (modal may have different selector in headless mode)
        textarea = page.locator('[data-testid="tweetTextarea_0"]').first
        if not textarea.is_visible():
            textarea = page.locator('div[role="textbox"]').first

        # Increase timeout for slower page loads in CI
        textarea.wait_for(state="visible", timeout=30000)
        textarea.click()

        # Type the tweet
        print("[Publisher] Typing tweet...")
        page.keyboard.type(post, delay=10)
        page.wait_for_timeout(1000)

        # Find and click Post button in modal
        print("[Publisher] Submitting tweet...")
        post_btn = page.locator('[data-testid="tweetButton"]').first
        try:
            # Try a normal click first; if it fails due to overlay, force the click.
            post_btn.click(timeout=30000)
        except Exception as e:
            print(f"[Publisher] Normal click failed ({e}), attempting force click...")
            try:
                post_btn.click(force=True, timeout=30000)
            except Exception as e2:
                print(f"[Publisher] Force click also failed ({e2}), falling back to keyboard shortcut.")
                page.keyboard.press("Control+Enter")
        
        # Wait for the tweet to publish and extract URL
        tweet_url = None
        tweet_id = None

        try:
            toast = page.locator('[data-testid="toast"]').first
            toast.wait_for(state="visible", timeout=8000)
            link = toast.locator('a[href*="/status/"]').first
            if link.count() > 0:
                href = link.get_attribute("href")
                if href:
                    tweet_url = href if href.startswith("http") else f"https://x.com{href}"
                    match = re.search(r"/status/(\d+)", tweet_url)
                    if match:
                        tweet_id = match.group(1)
        except Exception:
            pass

        page.wait_for_timeout(3000)
        browser.close()

    print(f"[Publisher] Tweet published successfully! URL: {tweet_url or 'https://x.com'}")

    return {
        "tweet_id": tweet_id or "",
        "tweet_url": tweet_url or "https://x.com"
    }