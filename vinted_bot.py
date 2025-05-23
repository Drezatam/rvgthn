import json
import time
import asyncio
import requests
from playwright.async_api import async_playwright

WEBHOOK_URL = "https://discord.com/api/webhooks/1363273647405535367/4wsu0gD9w3MH8k6CepFeKf4R7iPinkUi8CtZrnVXU9TwHzuYOPPM5QDyiKevK1QrPXkv"
VINTED_URL = "https://www.vinted.fr/catalog?time=1745141217&disabled_personalization=true&page=1&order=newest_first&search_text=birkenstock&price_to=20.00&currency=EUR&status_ids[]=2&status_ids[]=3&status_ids[]=4&brand_ids[]=3203&size_ids[]=776&size_ids[]=777&size_ids[]=778&size_ids[]=780&size_ids[]=781&size_ids[]=782&size_ids[]=783&size_ids[]=784&size_ids[]=785&size_ids[]=786&size_ids[]=787&size_ids[]=788&size_ids[]=56&size_ids[]=57&size_ids[]=1196&size_ids[]=1197&size_ids[]=58&size_ids[]=1198&size_ids[]=59&size_ids[]=1199&size_ids[]=60&size_ids[]=1200&size_ids[]=61&size_ids[]=1201&size_ids[]=62&size_ids[]=63"
SEEN_FILE = "seen_annonces.json"

async def fetch_annonces():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(VINTED_URL)
        await page.wait_for_selector("div.feed-grid__item")
        await page.wait_for_timeout(1500)

        annonces = await page.query_selector_all("div.feed-grid__item a")
        results = []

        for annonce in annonces:
            href = await annonce.get_attribute("href")
            if href and "vinted.fr" in href:
                link = "https://www.vinted.fr" + href if href.startswith("/items") else href
                image_el = await annonce.query_selector("img")
                image = await image_el.get_attribute("src") if image_el else None

                results.append({"url": link, "image": image})

        await browser.close()
        return results

def send_to_discord(annonce):
    data = {
        "embeds": [
            {
                "title": "📢 Nouvelle annonce Vinted",
                "url": annonce["url"],
                "image": {"url": annonce["image"]} if annonce["image"] else {},
                "color": 5814783,
                "footer": {"text": "Vinted Bot"},
            }
        ]
    }
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print(f"❌ Erreur d'envoi : {response.status_code} - {response.text}")
    else:
        print(f"✅ Nouvelle annonce envoyée : {annonce['url']}")

def load_seen():
    try:
        with open(SEEN_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_seen(links):
    with open(SEEN_FILE, "w") as f:
        json.dump(links, f)

async def main_loop():
    seen = load_seen()
    while True:
        print("🔍 Vérification des nouvelles annonces...")
        annonces = await fetch_annonces()
        new_annonces = [a for a in annonces if a["url"] not in seen]

        for annonce in new_annonces:
            send_to_discord(annonce)
            seen.append(annonce["url"])

        if new_annonces:
            save_seen(seen)

        print(f"🕒 Pause de 60 secondes...")
        time.sleep(60)

if __name__ == "__main__":
    asyncio.run(main_loop())

