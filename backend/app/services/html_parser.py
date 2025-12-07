import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

BASE_URL = "https://russiabase.ru/prices"


def fetch_page(region: int, page: int) -> Optional[str]:
    """
    Загружает HTML страницу по региону и номеру страницы.
    """
    url = f"{BASE_URL}?region={region}&page={page}"
    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        return None

    return response.text


def parse_table(html: str) -> List[Dict]:
    """
    Парсит таблицу со страницы russiabase.ru
    Возвращает список словарей:
    {
        "station_name": "...",
        "city": "...",
        "prices": {
            "AI92": ...,
            "AI95": ...,
            "DIESEL": ...,
            "GAS": ...
        }
    }
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")

    if table is None:
        return []

    rows = table.find_all("tr")[1:]  # пропускаем заголовок

    result = []

    for row in rows:
        cols = [c.text.strip() for c in row.find_all("td")]

        if len(cols) < 6:
            continue

        station_name = cols[0]
        city = cols[1]

        ai92 = cols[2] or None
        ai95 = cols[3] or None
        diesel = cols[4] or None
        gas = cols[5] or None

        result.append({
            "station_name": station_name,
            "city": city,
            "prices": {
                "AI92": ai92,
                "AI95": ai95,
                "DIESEL": diesel,
                "GAS": gas
            }
        })

    return result


def get_all_pages(region: int) -> List[Dict]:
    """
    Загружает и парсит все страницы подряд, 
    пока таблица не пропадёт или не будет пустой.
    """
    page = 1
    result = []

    while True:
        html = fetch_page(region, page)
        if html is None:
            break

        rows = parse_table(html)
        if not rows:
            break

        result.extend(rows)

        page += 1

    return result
