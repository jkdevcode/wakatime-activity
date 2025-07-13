import requests
import svgwrite
import os
import base64
from datetime import datetime, timedelta, timezone

# Configuración
API_KEY = os.getenv("WAKATIME_API_KEY")
USERNAME = os.getenv("WAKATIME_USERNAME", "current")

# Paleta de colores tipo GitHub
colors = [
  "#1C1F26",  # Negro azulado oscuro
  "#2B3A4C",  # Azul oscuro
  "#3C526A",  # Azul grisáceo oscuro
  "#56728D",  # Azul medio
  "#7C9AB9",  # Azul claro
  "#D3D7DC"   # Gris muy claro
]


def get_data():
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=7)  # ✅ Solo últimos 7 días para cuentas free

    api_url = f"https://wakatime.com/api/v1/users/{USERNAME}/summaries?start={start}&end={end}"
    # Codifica la API Key en base64, agregando ":" al final
    auth_string = f"{API_KEY}:"
    b64_auth = base64.b64encode(auth_string.encode()).decode()
    headers = {"Authorization": f"Basic {b64_auth}"}
    
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
    horas = duration / 3600
    if horas < 1:
        return 0  # Negro azulado oscuro
    elif 1 <= horas < 4:
        return 1  # Azul oscuro
    elif 4 <= horas < 9:
        return 2  # Azul grisáceo oscuro
    elif 9 <= horas < 11:
        return 3  # Azul medio
    elif 11 <= horas < 13:
        return 4  # Azul claro
    else:
        return 5  # Gris muy claro

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

        # Calcular horas y minutos
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)

        # Formato de texto hover
        label = f"{date.strftime('%b %d, %Y')} — {hours}h {minutes}m"

        rect = dwg.rect(
            insert=(x, y),
            size=(square_size, square_size),
            fill=colors[level]
        )
        rect.set_desc(title=label)  # 👈 Tooltip visible al pasar mouse
        dwg.add(rect)

    dwg.save()


if __name__ == "__main__":
    data = get_data()
    draw_svg(data)
