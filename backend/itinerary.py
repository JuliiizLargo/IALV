from groq_client import ask_groq

def generate_itinerary(city: str, days: int, hotels, flights, places) -> str:
    def fmt_hotels(h):
        if not h or not isinstance(h, list):
            return "No disponible"
        lines = []
        for x in h[:5]:
            name = (x or {}).get("name")
            rating = (x or {}).get("rating")
            price = (x or {}).get("price")
            line = f"- {name or 'Hotel'} | ⭐ {rating or 'N/D'} | {price or 's/p'}"
            lines.append(line)
        return "\n".join(lines) or "No disponible"

    def fmt_flights(f):
        if not f or not isinstance(f, list):
            return "No disponible"
        lines = []
        for x in f[:3]:
            airline = (x or {}).get("airline")
            dep = (x or {}).get("departure_airport")
            arr = (x or {}).get("arrival_airport")
            time = (x or {}).get("departure_time")
            price = (x or {}).get("price")
            line = f"- {airline or 'Aerolínea'} {dep or ''}->{arr or ''} {time or ''} | {price or 's/p'}"
            lines.append(line)
        return "\n".join(lines) or "No disponible"

    def fmt_places(p):
        if not p or not isinstance(p, list):
            return "No disponible"
        lines = []
        for x in p[:6]:
            name = (x or {}).get("name")
            rating = (x or {}).get("rating")
            line = f"- {name or 'Lugar'} | ⭐ {rating or 'N/D'}"
            lines.append(line)
        return "\n".join(lines) or "No disponible"

    prompt = f"""
    Eres un agente de viajes profesional. Genera un itinerario optimizado de {days} días en {city}.
    Resume y usa los siguientes insumos reales. Si algún insumo no está disponible, asume alternativas razonables.

    Hoteles sugeridos (top):
    {fmt_hotels(hotels)}

    Vuelos sugeridos (top):
    {fmt_flights(flights)}

    Actividades recomendadas (top):
    {fmt_places(places)}

    Requisitos del itinerario:
    - Proporciona actividades por mañana/tarde/noche cada día.
    - Indica tiempos aproximados de traslado cuando sea útil.
    - Alterna actividades intensas con otras ligeras.
    - Incluye opciones de comida típicas de la ciudad.
    - Formatea en secciones claras por día con encabezado "Día N".
    """
    return ask_groq(prompt)
