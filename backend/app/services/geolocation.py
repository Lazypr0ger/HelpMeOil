import requests
from shapely.geometry import Point, Polygon
from sqlalchemy.orm import Session
from ..models.models import City
import os
from dotenv import load_dotenv

load_dotenv()
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")


# -------- Получение координат по адресу --------
def geocode_address(address: str):
    if not address:
        return None

    url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": YANDEX_API_KEY,
        "geocode": address,
        "format": "json"
    }

    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return None

    try:
        obj = resp.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        lon, lat = map(float, obj["Point"]["pos"].split())
        return lat, lon
    except:
        return None


# -------- Проверка принадлежности точки к городу --------
def detect_city_from_point(db: Session, lat: float, lon: float):
    point = Point(lon, lat)

    cities = db.query(City).all()
    for c in cities:
        if c.lat is None or c.lon is None:
            continue

        # Создаём небольшой круг вокруг центра города (7 км)
        city_zone = point.buffer(0.1)  # примерно 7-10 км радиус

        city_center = Point(c.lon, c.lat)

        if city_zone.contains(city_center):
            return c.id

    return None
