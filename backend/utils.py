from ics import Calendar, Event
from datetime import datetime, timedelta

def itinerary_to_ics_content(city, start_date, days, plan_text) -> str:
    """Genera un archivo ICS en memoria y devuelve su contenido como string."""
    cal = Calendar()
    base_date = datetime.strptime(start_date, "%Y-%m-%d")

    for i in range(days):
        e = Event()
        e.name = f"Viaje a {city} - Día {i+1}"
        # Asumimos evento de día completo; ics acepta date o datetime. Usamos begin como fecha.
        e.begin = base_date + timedelta(days=i)
        e.make_all_day()
        e.description = plan_text
        cal.events.add(e)

    return cal.serialize()
