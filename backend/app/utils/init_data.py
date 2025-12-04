from backend.app.db.database import SessionLocal
from backend.app.models.models import District, OurStation

def init_data():
    db = SessionLocal()

    districts = [
        "Засвияжский",
        "Ленинский",
        "Железнодорожный",
        "Заволжский"
    ]

    # --- Добавляем районы ---
    district_objs = {}
    for name in districts:
        d = db.query(District).filter_by(name=name).first()
        if not d:
            d = District(name=name)
            db.add(d)
            db.commit()
            db.refresh(d)
        district_objs[name] = d

    # --- Добавляем наши АЗС HelpMeOil ---
    stations = [
        ("HelpMeOil №1", "Засвияжский", 54.30877, 48.33497),
        ("HelpMeOil №2", "Ленинский", 54.32200, 48.39700),
        ("HelpMeOil №3", "Железнодорожный", 54.27340, 48.26150),
        ("HelpMeOil №4", "Заволжский", 54.36850, 48.54010)
    ]

    for name, district_name, lat, lon in stations:
        exists = db.query(OurStation).filter_by(
            name=name,
            district_id=district_objs[district_name].id
        ).first()
        if not exists:
            s = OurStation(
                name=name,
                district_id=district_objs[district_name].id,
                lat=lat,
                lon=lon
            )
            db.add(s)
            db.commit()

    db.close()
    print("✔ Данные успешно добавлены!")


if __name__ == "__main__":
    init_data()
