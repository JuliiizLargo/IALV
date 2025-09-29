import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from backend.serp_client import search_hotels, search_flights, search_places
from backend.itinerary import generate_itinerary
from backend.utils import itinerary_to_ics_content
from backend.serp_client import SerpApiError
from backend.groq_client import GroqClientError
from datetime import datetime, timedelta
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)
# Habilitar CORS para endpoints /api/*
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.after_request
def add_cors_headers(response):
    # Asegura cabeceras CORS en todas las respuestas /api/*
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

@app.route("/api/itinerary", methods=["POST", "OPTIONS"])
def api_itinerary():
    # Preflight
    if request.method == "OPTIONS":
        return ("", 204)
    data = (request.get_json(silent=True) or {})
    city = (data.get("city") or "").strip()
    days_raw = data.get("days")
    start_date = (data.get("start_date") or "").strip()

    if not city:
        return jsonify({"error": "'city' es requerido"}), 400

    try:
        days = int(days_raw) if days_raw is not None else 3
    except ValueError:
        return jsonify({"error": "'days' debe ser un número"}), 400
    if days < 1 or days > 30:
        return jsonify({"error": "'days' debe estar entre 1 y 30"}), 400

    # Fecha por defecto dinámica: hoy + 14 días
    if not start_date:
        start_date = (datetime.utcnow() + timedelta(days=14)).strftime("%Y-%m-%d")
    else:
        try:
            # validar formato
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "'start_date' debe tener formato YYYY-MM-DD"}), 400

    hotels = flights = places = None
    errors = {}
    try:
        hotels = search_hotels(city)
    except SerpApiError as e:
        errors["hotels"] = str(e)
    try:
        flights = search_flights("BOG", city, start_date)
    except SerpApiError as e:
        errors["flights"] = str(e)
    try:
        places = search_places(city)
    except SerpApiError as e:
        errors["places"] = str(e)

    try:
        itinerary_text = generate_itinerary(city, days, hotels, flights, places)
    except GroqClientError as e:
        return jsonify({"error": f"Fallo al generar el itinerario: {e}", "details": errors}), 502
    except Exception as e:
        return jsonify({"error": f"Error inesperado generando itinerario: {e}", "details": errors}), 500

    ics_content = None
    ics_filename = None
    try:
        ics_content = itinerary_to_ics_content(city, start_date, days, itinerary_text)
        ics_filename = f"itinerary_{city}.ics"
    except Exception as e:
        # No romper la respuesta si el ICS falla; devolvemos el itinerario y un warning
        errors["ics"] = f"No se pudo generar ICS: {e}"

    return jsonify({
        "itinerary": itinerary_text,
        "ics_content": ics_content,
        "ics_filename": ics_filename,
        "warnings": errors or None,
    })

@app.route("/api/ask", methods=["POST", "OPTIONS"])
def api_ask():
    # Preflight
    if request.method == "OPTIONS":
        return ("", 204)
    from backend.groq_client import ask_groq
    data = (request.get_json(silent=True) or {})
    question = (data.get("question") or "").strip()
    if len(question) < 3:
        return jsonify({"error": "La pregunta es demasiado corta."}), 400
    try:
        answer = ask_groq(question)
        return jsonify({"answer": answer})
    except GroqClientError as e:
        return jsonify({"error": f"Fallo al consultar Groq: {e}"}), 502
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)

