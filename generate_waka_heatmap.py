import requests
import svgwrite
import os
from datetime import datetime, timedelta, timezone

# Configuración
API_KEY = os.getenv("WAKATIME_API_KEY") or "waka_dbce4588-e9a3-4197-a14e-2fcfa355a515"
USERNAME = os.getenv("WAKATIME_USERNAME", "current")

# Paleta de colores tipo GitHub
colors = [
    "#161b22",  # Sin actividad
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
]

def get_data():
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=7)  # ✅ Solo últimos 7 días para cuentas free

    api_url = f"https://wakatime.com/api/v1/users/{USERNAME}/summaries?start={start}&end={end}"
    headers = {"Authorization": f"Basic {API_KEY}"}
    
    res = requests.get(api_url, headers=headers)
    print("Respuesta de la API:", res.text)
    if res.status_code != 200:
        raise Exception(f"Error al obtener datos: {res.status_code}")
    
    summaries = res.json()["data"]
    data = []
    for day in summaries:
        data.append({
            "date": day["range"]["date"],
            "grand_total": {
                "total_seconds": day.get("grand_total", {}).get("total_seconds", 0)
            }
        })
    
    # Debug: últimos 7 días
    for d in data:
        print(d["date"], d["grand_total"]["total_seconds"])

    return data

def intensity(duration):
    if duration == 0:
        return 0
    elif duration < 600:
        return 1
    elif duration < 1800:
        return 2
    elif duration < 3600:
        return 3
    return 4

def draw_svg(data, filename="waka-heatmap.svg"):
    square_size = 12
    padding = 2
    width = len(data) * (square_size + padding)
    height = 7 * (square_size + padding)
    dwg = svgwrite.Drawing(filename, size=(width, height), profile='tiny')

    for i, day in enumerate(data):
        date = datetime.strptime(day["date"], "%Y-%m-%d")
        x = i * (square_size + padding)
        y = date.weekday() * (square_size + padding)
        total_seconds = day.get("grand_total", {}).get("total_seconds", 0)
        level = intensity(total_seconds)
        dwg.add(dwg.rect(insert=(x, y), size=(square_size, square_size), fill=colors[level]))

    dwg.save()

if __name__ == "__main__":
    data = get_data()
    draw_svg(data)
