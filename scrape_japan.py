#!/usr/bin/env python3
import asyncio
import zipfile
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

OUTPUT_DIR = Path.home() / "Downloads" / "my-site"
ZIP_PATH = Path.home() / "Downloads" / "my-site-final.zip"
URL = "https://eager-room-678856.framer.app/trips/japan"
OUT_FILE = OUTPUT_DIR / "trips" / "japan.html"


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()
        print(f"Scraping {URL} (120s timeout)...")
        await page.goto(URL, wait_until="networkidle", timeout=120_000)
        await page.wait_for_timeout(2000)
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        badge = soup.find("div", id="__framer-badge-container")
        if badge:
            badge.decompose()
            print("Removed Framer badge")
        html = str(soup)
        OUT_FILE.write_text(html, encoding="utf-8")
        print(f"Saved ({len(html):,} bytes) -> {OUT_FILE}")
        await browser.close()

    # Update zip with the new file
    print(f"Updating {ZIP_PATH}...")
    with zipfile.ZipFile(ZIP_PATH, "a", zipfile.ZIP_DEFLATED) as zf:
        arcname = OUT_FILE.relative_to(OUTPUT_DIR.parent)
        zf.write(OUT_FILE, arcname)
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
