import asyncio
from playwright.async_api import async_playwright
import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1363266175089381516/7MfPS6QMwJ8G97yIGuTuaXvoslO8zlfG0T-J5c7PHLSjOAx0THdwqX7JcjhDDA-bOGF9"
VINTED_URL = "https://www.vinted.fr/catalog?time=1745098530&disabled_personalization=true&catalog_from=0&page=1&order=newest_first"

seen_links = set()

async def scrap_and_notify():
    global seen_links
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(VINTED_URL)
        await page.wait_for_selector("div.feed-grid__item a")
        links = await page.eval_on_selector_all("div.feed-grid__item a", "els => els.map(e => e.href)")
        new_links = [link for link in links if link not in seen_links]
        for link in new_links:
            await page.goto(link)
            await page.wait_for_selector("h1", timeout=5000)
            title = await page.text_content("h1")
            price = await page.text_content("p[data-testid='item-price']")
            img = await page.get_attribute("img[itemprop='image']", "src")
            description = await page.text_content("p[data-testid='description']")
            embed = {
                "title": title.strip() if title else "Nouvelle annonce",
                "url": link,
                "description": description.strip() if description else "",
                "image": {"url": img} if img else {},
                "fields": [{"name": "Prix", "value": price.strip() if price else "?"}]
            }
            requests.post(WEBHOOK_URL, json={"embeds": [embed]})
            seen_links.add(link)
        await browser.close()

async def main():
    while True:
        try:
            await scrap_and_notify()
        except Exception as e:
            print("Erreur:", e)
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
