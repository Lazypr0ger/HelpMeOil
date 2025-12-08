from bs4 import BeautifulSoup
import requests
from typing import List, Dict, Optional
import re

BASE_URL = "https://russiabase.ru/prices"


import requests

def fetch_page(region: int, page: int) -> str | None:
    url = f"{BASE_URL}?region={region}&page={page}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "ru-RU,ru;q=0.9"
    }

    try:
        r = requests.get(url, headers=headers, timeout=12)
        if r.status_code == 200:
            return r.text
        print(f"[WARN] Bad response {r.status_code} on page {page}")
        return None

    except requests.exceptions.Timeout:
        print(f"[ERROR] Timeout while requesting {url}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return None



def parse_cards(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")

    # Каждая карточка заправки:
    cards = soup.select("div.ListingCard_orgCard__xCwyi")

    results = []

    for card in cards:
        # -------- Название станции --------
        name_tag = card.select_one("a.ListingCard_name__O9sxw")
        station_name = name_tag.get_text(strip=True) if name_tag else None

        # -------- Адрес --------
        address_tag = card.select_one("p.ListingCard_iconBlockText___egMo")
        address = address_tag.get_text(strip=True) if address_tag else None

       # -------- Город --------
        loc_tag = card.select_one("div.ListingCard_location__yrEON a:last-child")
        raw_city = loc_tag.get_text(strip=True) if loc_tag else None
        city = clean_city_name(raw_city)

        # -------- Цены --------
        prices_block = card.select("div.PricesListNew_block__4lVEL")

        prices = {}
        for pb in prices_block:
            fuel_name = pb.select_one("div.PricesListNew_blockLabel__FyFeq")
            fuel_price = pb.select_one("div.PricesListNew_pricing__m0s8Y p")

            if not fuel_name or not fuel_price:
                continue

            fname = fuel_name.get_text(strip=True)
            fprice = fuel_price.get_text(strip=True).replace("р.", "").replace(",", ".").strip()

            # Маппинг реальных названий в наши fuel_code
            if "92" in fname and "+" not in fname:
                fuel_code = "AI92"
            elif "92+" in fname:
                fuel_code = "AI92PLUS"
            elif "95" in fname:
                fuel_code = "AI95"
            elif "Газ" in fname or "ГАЗ" in fname:
                fuel_code = "GAS"
            elif "ДТ" in fname:
                fuel_code = "DIESEL"
            else:
                continue

            try:
                fprice = float(fprice)
            except:
                fprice = None

            prices[fuel_code] = fprice

        results.append({
            "station_name": station_name,
            "city": city,
            "address": address,
            "prices": prices
        })

    return results


def get_all_pages(region: int):
    page = 1
    results = []

    while True:
        html = fetch_page(region, page)

        if not html:
            print(f"[INFO] Page {page} unavailable → stop.")
            break

        parsed = parse_cards(html)

        if not parsed:
            break

        results.extend(parsed)
        page += 1

    return results

def clean_city_name(raw: str | None) -> Optional[str]:
    if not raw:
        return None
    s = raw.strip()


    s = re.sub(r'^\d+[\.,]\s*', '', s)


    if not s:
        return None

    if re.fullmatch(r'\d+([\.,]\d+)?', s):
        return None

    return s