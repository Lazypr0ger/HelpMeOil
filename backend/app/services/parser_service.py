from ..utils.geolocation import geocode_address, detect_city_from_point
from ..models.models import CompetitorStation, FuelPrice, City
from sqlalchemy.orm import Session
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import requests
from math import radians, cos, sin, asin, sqrt
import os

BASE_URL = "https://russiabase.ru/prices?region=46"
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
def geocode_address(address: str):
    if not YANDEX_API_KEY:
        print("⚠ Нет Yandex API KEY")
        return None

    url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": YANDEX_API_KEY,
        "format": "json",
        "geocode": address
    }

    resp = requests.get(url, params=params)
    data = resp.json()

    try:
        pos = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        lon, lat = map(float, pos.split(" "))
        return lat, lon
    except:
        return None
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # радиус земли в км
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c
def detect_city_by_coords(db, lat, lon):
    cities = db.query(City).all()
    closest_city = None
    min_dist = 99999

    for c in cities:
        dist = haversine(lat, lon, c.lat, c.lon)
        if dist < min_dist:
            min_dist = dist
            closest_city = c

    # если заправка дальше 7 км → считаем "трассой" и НЕ сохраняем
    if min_dist > 7:
        return None

    return closest_city.id

def fetch_page(page: int = 1):
    url = BASE_URL if page == 1 else f"{BASE_URL}&page={page}"
    response = requests.get(url, timeout=10)

    return BeautifulSoup(response.text, "html.parser") if response.status_code == 200 else None


def parse_card(card):
    name = card.select_one(".ListingCard_name__O9sxw")
    name = name.text.strip() if name else "АЗС"

    brand_logo = card.select_one(".ListingCard_logo___8VJR img")
    brand = brand_logo["alt"] if brand_logo and brand_logo.has_attr("alt") else "АЗС"

    address = card.select_one(".ListingCard_iconBlockText___egMo")
    address = address.text.strip() if address else ""

    prices = {}
    blocks = card.select(".PricesListNew_block__4lVEL")

    for b in blocks:
        t = b.select_one(".PricesListNew_blockLabel__FyFeq")
        p = b.select_one("p")

        if t and p:
            fuel = t.text.strip()
            price = p.text.replace("р.", "").replace(",", ".").strip()

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


def run_full_parsing(db: Session):
    page = 1
    added = 0
    price_count = 0

    while True:
        soup = fetch_page(page)
        if not soup:
            break

        cards = soup.select(".ListingCard_orgCard__xCwyi")
        if not cards:
            break

        for card in cards:
            data = parse_card(card)

            # 1 — получаем координаты
            coords = geocode_address(data["address"])

            if not coords:
                continue

            lat, lon = coords

            # 2 — определяем город
            city_id = detect_city_from_point(db, lat, lon)

            if not city_id:
                continue  # не сохраняем трассовые / областные станции

            # 3 — ищем или создаём станцию
            station = db.query(CompetitorStation).filter(
                CompetitorStation.station_name == data["station_name"]
            ).first()

            if not station:
                station = CompetitorStation(
                    station_name=data["station_name"],
                    brand=data["brand"],
                    address=data["address"],
                    lat=lat,
                    lon=lon,
                    city_id=city_id
                )
                db.add(station)
                db.commit()
                db.refresh(station)
                added += 1

            # 4 — сохраняем цены
            timestamp = datetime.now()

            for fuel, price in data["prices"].items():
                entry = FuelPrice(
                    station_id=station.id,
                    fuel_type=fuel,
                    price=price,
                    timestamp=timestamp,
                )
                db.add(entry)
                price_count += 1

            db.commit()

        page += 1

    return {"stations_added": added, "prices_added": price_count}
