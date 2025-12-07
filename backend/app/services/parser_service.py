# app/services/parser_service.py

import os
import datetime
from typing import List, Dict

import pandas as pd
from sqlalchemy.orm import Session

from app.services.html_parser import get_all_pages
from app.models.city import City
from app.models.station import CompetitorStation
from app.models.fuel import FuelType
from app.models.price import FuelPrice, StationType
from app.models.station import OurStation


HISTORY_DIR = os.path.join(os.getcwd(), "app", "history")

CITY_NORMALIZATION = {
    # --- Ульяновск ---
    "Ульяновск": "Ульяновск",
    "Городской округ Ульяновск": "Ульяновск",
    "Ульяновский район": "Ульяновск",   # по адресу – это "Большие Ключищи", но для аналитики логичнее привязывать к Ульяновску
    "Земляничный": "Барыш",             # это посёлок рядом, относится к Барышу
    "Мирный": "Чердаклы",               # п. Мирный — реальное подчинение Чердаклам

    # --- Димитровград ---
    "Димитровград": "Димитровград",
    "Мелекесский район": "Димитровград",  # Новая Майна + Мулловка — это пригород ДГ

    # --- Чердаклы ---
    "Чердаклы": "Чердаклы",
    "Чердаклинский район": "Чердаклы",    # всё корректно трактуется как Чердаклы

    # --- Барыш ---
    "Барыш": "Барыш",
    "Барышский район": "Барыш",

    # --- Новоспасское ---
    "Новоспасское": "Новоспасское",
    "Новоспасский район": "Новоспасское",

    # --- Майна / Старая Майна ---
    "Майна": "Майна",
    "Старая Майна": "Майна",
    "Старомайнский район": "Майна",

    # --- Карсун ---
    "Карсун": "Карсун",
    "Карсунский район": "Карсун",

    # --- Инза ---
    "Инза": "Инза",

    # --- Кузоватово ---
    "Кузоватовский район": "Кузоватово",

    # --- Сенгилей ---
    "Сенгилеевский район": "Сенгилей",

    # --- Цильна ---
    "Цильнинский район": "Цильна",

    # --- Тагай ---
    "Тагай": "Тагай",

    # --- Марьевка ---
    "Марьевка": "Цильна",  # административно часть Цильнинского района

    # --- Радищево ---
    "Радищевский район": "Радищево",

    # --- Новомалыклинский район ---
    "Новомалыклинский район": "Новая Малыкла",  # по твоим данным это центр

    # --- Уникальные населённые пункты ---
    "Дмитриево-Помряскино": "Дмитриево-Помряскино",
    "Ждамирово": "Ждамирово",
    "Тереньгульский район": "Тереньга",
}

def normalize_city(name: str) -> str:
    name = name.strip()

    if name in CITY_NORMALIZATION:
        return CITY_NORMALIZATION[name]

    # Если вдруг встретился "г. Ульяновск" — обрабатываем автоматически:
    if "Ульяновск" in name:
        return "Ульяновск"
    if "Димитровград" in name:
        return "Димитровград"

    # Если встретился район, но его нет в словаре — обрезаем суффикс
    if "район" in name:
        base = name.replace("район", "").strip()
        return base

    return name


def run_full_parsing(db: Session, region: int = 46) -> pd.DataFrame:
    """
    Полный цикл:
    1) парсинг russiabase.ru
    2) формирование ДЛИННОГО датасета:
       city, station_name, fuel_code, price, date
    3) очистка и заполнение медианами
    4) сохранение в history/
    5) запись в БД
    """

    raw: List[Dict] = get_all_pages(region=region)
    now = datetime.datetime.now()

    # ---------- 1. Формируем длинный датафрейм ----------
    records: List[Dict] = []

    for item in raw:
        city = item.get("city")
        station_name = item.get("station_name")
        prices = item.get("prices", {})

        for fuel_code, price in prices.items():
            records.append(
                {
                    "city": city,
                    "station_name": station_name,
                    "address": item.get("address"),
                    "fuel_code": fuel_code,
                    "price": price,
                    "date": now,
                }
            )

    df = pd.DataFrame(records)

    if df.empty:
        print("[WARN] Парсер вернул пустые данные.")
        return df

    # ---------- 2. Чистим базовые поля ----------
    # удаляем строки без города или названия станции
    df = df.dropna(subset=["city", "station_name"])

    # приводим город к строке и убираем лишние пробелы
    df["city"] = df["city"].astype(str).str.strip()
    df["city"] = df["city"].apply(normalize_city)

    # выкидываем строки, где city всё ещё выглядит как число (типа "60.3")
    mask_bad_city = df["city"].str.fullmatch(r"\d+([\.,]\d+)?")
    df = df[~mask_bad_city]

    # приводим цену к числу, нули считаем отсутствующими
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df.loc[df["price"] <= 0, "price"] = pd.NA

    # ---------- 3. Заполнение медианами по (city, fuel_code) ----------
    def fill_group(group: pd.DataFrame) -> pd.DataFrame:
        median_price = group["price"].median()
        group["price"] = group["price"].fillna(median_price)
        return group

    df = (
        df.groupby(["city", "fuel_code"], group_keys=False)
        .apply(fill_group)
        .reset_index(drop=True)
    )

    # на всякий случай выбрасываем строки, где так и не удалось получить цену
    df = df.dropna(subset=["price"])

    # ---------- 4. Сохраняем в history/ ----------
    save_dataframe_to_history(df)

    # ---------- 5. Пишем в БД ----------
    write_to_database(df, db)

    return df


def save_dataframe_to_history(df: pd.DataFrame) -> None:
    """
    Сохраняет датасет в app/history/YYYY-MM-DD_HH-MM.csv
    Формат колонок: city, station_name, fuel_code, price, date
    """
    os.makedirs(HISTORY_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"{ts}.csv"
    path = os.path.join(HISTORY_DIR, filename)
    df.to_csv(path, index=False)
    print(f"[OK] Датасет сохранён: {path}")


def write_to_database(df: pd.DataFrame, db: Session) -> None:
    """
    Простая версия: создаём все города, станции и ЦЕНЫ БЕЗ проверок дубликатов.
    Потом уже будем умнеть.
    """

    # кэш видов топлива
    fuel_map = {f.code: f.id for f in db.query(FuelType).all()}
    print("[DEBUG] fuel_map:", fuel_map)

    created_cities = {}
    created_stations = {}

    for idx, row in df.iterrows():
        city_name = str(row["city"]).strip()
        station_name = str(row["station_name"]).strip()
        address = str(row["address"]).strip() if row.get("address") is not None else None
        fuel_code = row["fuel_code"]
        price = float(row["price"])
        date = row["date"]   # тут у тебя уже datetime, это ок

        print(f"[ROW {idx}] {city_name} | {station_name} | {fuel_code} | {price}")

        # --- город ---
        city = created_cities.get(city_name)
        if not city:
            city = (
                db.query(City)
                .filter(City.name.ilike(city_name))
                .first()
            )
            if not city:
                city = City(name=city_name)
                db.add(city)
                db.commit()
                db.refresh(city)
                print(f"[DB] Создан город: {city_name} (id={city.id})")
            created_cities[city_name] = city

            # создаём нашу АЗС в этом городе
            ensure_our_station_exists(db, city)

        # --- станция конкурента ---
        st_key = (city.id, station_name)
        station = created_stations.get(st_key)
        if not station:
            station = (
                db.query(CompetitorStation)
                .filter(
                    CompetitorStation.station_name.ilike(station_name),
                    CompetitorStation.city_id == city.id,
                )
                .first()
            )
            if not station:
                station = CompetitorStation(
                    station_name=station_name,
                    address=address,
                    city_id=city.id,
                )
                db.add(station)
                db.commit()
                db.refresh(station)
                print(f"[DB] Создана станция: {station_name} в {city_name} (id={station.id})")
            created_stations[st_key] = station

        # --- вид топлива ---
        fuel_id = fuel_map.get(fuel_code)
        if not fuel_id:
            print(f"[WARN] Неизвестный вид топлива: {fuel_code}, строка {idx} — пропускаем")
            continue

        # --- просто добавляем цену БЕЗ проверок существования ---
        db_price = FuelPrice(
            station_type=StationType.competitor,
            competitor_station_id=station.id,
            fuel_type_id=fuel_id,
            price=price,
            date=date,
        )
        db.add(db_price)
        print(f"[DB] Добавлена цена: station_id={station.id}, fuel={fuel_code}, price={price}, date={date}")

    db.commit()
    print("[OK] Все данные записаны в БД.")


def ensure_our_station_exists(db: Session, city: City):
    """
    Создаёт нашу АЗС, если её ещё нет в городе.
    """
    existing = (
        db.query(OurStation)
        .filter(OurStation.city_id == city.id)
        .first()
    )

    if existing:
        return existing

    station = OurStation(
        name=f"HelpMeOil – {city.name}",
        address=f"{city.name}",
        city_id=city.id
    )
    db.add(station)
    db.commit()
    db.refresh(station)

    print(f"[OK] Добавлена наша АЗС в городе: {city.name}")

    return station
