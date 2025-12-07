import os
import pandas as pd
import datetime
from typing import List, Dict

from app.services.html_parser import get_all_pages
from app.models.city import City
from app.models.station import CompetitorStation
from app.models.fuel import FuelType
from app.models.price import FuelPrice, StationType


def run_full_parsing(db):
    raw = get_all_pages(region=46)

    df = pd.DataFrame([
        {
            "station_name": item["station_name"],
            "city": item["city"],
            "AI92": item["prices"]["AI92"],
            "AI95": item["prices"]["AI95"],
            "DIESEL": item["prices"]["DIESEL"],
            "GAS": item["prices"]["GAS"],
        }
        for item in raw
    ])

    # === 1. Удаляем строки без города ===
    df = df.dropna(subset=["city"])

    fuel_cols = ["AI92", "AI95", "DIESEL", "GAS"]

    # === 2. Приводим к числам + превращаем нули в NaN ===
    for col in fuel_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")  # пустые/мусор → NaN
        # нули считаем отсутствующими данными
        df.loc[df[col] == 0, col] = pd.NA

    # === 3. Заполняем медианами по ГОРОДУ и ВИДУ ТОПЛИВА ===
    def fill_group(group):
        medians = group[fuel_cols].median()
        for col in fuel_cols:
            group[col] = group[col].fillna(medians[col])
        return group

    df = df.groupby("city", group_keys=False).apply(fill_group)

    # дальше как раньше:
    save_dataframe_to_history(df)
    write_to_database(df, db)
    return df



def save_dataframe_to_history(df: pd.DataFrame):
    """
    Сохраняет датафрейм в папку app/history/ с именем вида:
    2025-12-07_14-00.csv
    """
    folder = os.path.join(os.getcwd(), "app", "history")
    os.makedirs(folder, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"{timestamp}.csv"
    filepath = os.path.join(folder, filename)

    df.to_csv(filepath, index=False)

    print(f"[OK] Датасет сохранён в history: {filename}")


def write_to_database(df: pd.DataFrame, db):
    today = datetime.date.today()

    # Подгружаем справочник видов топлива
    fuel_map = {f.code: f.id for f in db.query(FuelType).all()}

    for _, row in df.iterrows():

        # === (1) Город ===
        city = db.query(City).filter(City.name.ilike(row.city)).first()
        if not city:
            city = City(name=row.city)
            db.add(city)
            db.commit()
            db.refresh(city)

        # === (2) Станция ===
        station = (
            db.query(CompetitorStation)
              .filter(
                  CompetitorStation.station_name.ilike(row.station_name),
                  CompetitorStation.city_id == city.id
              )
              .first()
        )

        if not station:
            station = CompetitorStation(
                station_name=row.station_name,
                brand=None,
                address=None,
                city_id=city.id
            )
            db.add(station)
            db.commit()
            db.refresh(station)

        # === (3) Пишем цены ===
        for fuel_code in ["AI92", "AI95", "DIESEL", "GAS"]:
            value = row[fuel_code]

            if pd.isna(value):
                continue

            fuel_id = fuel_map.get(fuel_code)

            # Проверяем: есть ли цена за сегодняшнюю дату?
            exists = (
                db.query(FuelPrice)
                  .filter(
                      FuelPrice.station_type == StationType.competitor,
                      FuelPrice.competitor_station_id == station.id,
                      FuelPrice.fuel_type_id == fuel_id,
                      FuelPrice.date == today
                  )
                  .first()
            )

            if exists:
                continue  # не заливаем дубли

            db.add(FuelPrice(
                station_id=station.id,
                station_type=StationType.competitor,
                competitor_station_id=station.id,
                fuel_type_id=fuel_id,
                price=float(value),
                date=today
            ))

    db.commit()
    print("[OK] Данные успешно записаны в PostgreSQL.")

