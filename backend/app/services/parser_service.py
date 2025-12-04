import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from ..models.models import District, CompetitorStation, FuelPrice

load_dotenv()

BASE_URL = "https://russiabase.ru/prices?region=46"
YANDEX_API_KEY = os.getenv("ed48b3c9-55b6-45d5-81b2-2794a0e93e09")

# Кэширование
_geocode_cache = {}
district_cache = {}

# ================================
# 1. Получить HTML (с селекторами)
# ================================
def fetch_page(page: int = 1):
    url = BASE_URL if page == 1 else f"{BASE_URL}&page={page}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Ошибка загрузки страницы {url}: {e}")
        return None

    return BeautifulSoup(response.text, "html.parser")


# ================================
# 2. Парсинг карточки АЗС
# ================================
def parse_card(card):
    # Название
    name_el = card.select_one(".ListingCard_name__O9sxw")
    name = name_el.text.strip() if name_el else "Неизвестно"

    # Бренд (логотип ALT)
    brand_logo = card.select_one(".ListingCard_logo___8VJR img")
    brand = brand_logo["alt"] if brand_logo and brand_logo.has_attr("alt") else "АЗС"

    # Адрес
    addr_el = card.select_one(".ListingCard_iconBlockText___egMo")
    address = addr_el.text.strip() if addr_el else ""

    # Цены
    prices = {}
    blocks = card.select(".PricesListNew_block__4lVEL")

    for block in blocks:
        fuel_el = block.select_one(".PricesListNew_blockLabel__FyFeq")
        price_el = block.select_one("p")

        if fuel_el and price_el:
            fuel = fuel_el.text.strip()
            price = price_el.text.replace("р.", "").replace(",", ".").strip()

            try:
                prices[fuel] = float(price)
            except:
                pass

    return {
        "station_name": name,
        "brand": brand,
        "address": address,
        "prices": prices,
    }


# ================================
# 3. Определение района → Яндекс API
# ================================
def detect_district(db: Session, address: str):
    if not address:
        return None

    # 1. Кэш
    if address in _geocode_cache:
        return _geocode_cache[address]

    # 2. Запрос к Яндекс Геокодеру
    url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": YANDEX_API_KEY,
        "geocode": f"Ульяновск, {address}",
        "format": "json",
        "results": 1,
        "lang": "ru_RU"
    }

    try:
        res = requests.get(url, params=params, timeout=7)
        data = res.json()
    except Exception as e:
        print("[ERROR] Яндекс не ответил:", e)
        return None

    # 3. Получаем компоненты адреса
    try:
        feature = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        comps = feature["metaDataProperty"]["GeocoderMetaData"]["Address"]["Components"]
    except:
        return None

    # 4. Ищем район
    found = None

    for c in comps:
        if c["kind"] in ("district", "area", "suburb", "locality"):
            found = c["name"]
            break

    if not found:
        return None

    found = found.replace("район", "").replace("г.", "").strip().lower()

    # 5. Загружаем кэш районов, если он пустой
    if not district_cache:
        for d in db.query(District).all():
            district_cache[d.name.lower()] = d.id

    # 6. Маппинг района на ID
    for name, did in district_cache.items():
        if name in found:
            _geocode_cache[address] = did
            return did

    return None


# ================================
# 4. Главная функция парсинга
# ================================
def run_full_parsing(db: Session):
    page = 1
    total_st = 0
    total_prices = 0

    while True:
        soup = fetch_page(page)
        if not soup:
            break

        cards = soup.select(".ListingCard_orgCard__xCwyi")
        if not cards:
            break

        for card in cards:
            d = parse_card(card)

            # найти или создать АЗС
            station = (
                db.query(CompetitorStation)
                .filter(CompetitorStation.station_name == d["station_name"])
                .first()
            )

            if not station:
                station = CompetitorStation(
                    station_name=d["station_name"],
                    brand=d["brand"],
                    address=d["address"],
                    district_id=detect_district(db, d["address"])
                )
                db.add(station)
                db.commit()
                db.refresh(station)
                total_st += 1

            # сохранить цены
            now = datetime.now()
            for fuel, price in d["prices"].items():
                entry = FuelPrice(
                    station_id=station.id,
                    fuel_type=fuel,
                    price=price,
                    timestamp=now,
                )
                db.add(entry)
                total_prices += 1

            db.commit()

        page += 1  # следующая страница

    return {
        "stations_added": total_st,
        "prices_added": total_prices
    }
