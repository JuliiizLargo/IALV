from ics import Calendar, Event
from datetime import datetime, timedelta

def itinerary_to_ics_content(city, start_date, days, plan_text) -> str:
    """Genera un archivo ICS en memoria y devuelve su contenido como string."""
    cal = Calendar()
    base_date = datetime.strptime(start_date, "%Y-%m-%d")

    for i in range(days):
        e = Event()
        e.name = f"Viaje a {city} - Día {i+1}"
        # Definir una duración razonable (por ejemplo 9:00 a 18:00)
        day_start = base_date + timedelta(days=i, hours=9)
        e.begin = day_start
        e.end = day_start + timedelta(hours=9)
        e.description = plan_text
        cal.events.add(e)

    return cal.serialize()
