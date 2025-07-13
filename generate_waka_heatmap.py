import requests
import datetime
import svgwrite
import os

# Configuración
API_KEY = os.getenv("WAKATIME_API_KEY")
USERNAME = os.getenv("WAKATIME_USERNAME", "current")
API_URL = f"https://wakatime.com/api/v1/users/{USERNAME}/insights/days/last_year"

# Paleta de colores tipo GitHub
colors = [
    "#161b22",  # Sin actividad
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
]

def get_data():
    headers = {"Authorization": f"Basic {API_KEY}"}
    res = requests.get(API_URL, headers=headers)
    if res.status_code != 200:
        raise Exception(f"Error al obtener datos: {res.status_code}")
    return res.json()["data"]["days"]

def intensity(duration):
    if duration == 0:
        return 0
    elif duration < 30 * 60:
        return 1
    elif duration < 2 * 60 * 60:
        return 2
    elif duration < 4 * 60 * 60:
        return 3
    return 4

def draw_svg(data, filename="waka-heatmap.svg"):
    square_size = 12
    padding = 2
    width = 53 * (square_size + padding)
    height = 7 * (square_size + padding)
    dwg = svgwrite.Drawing(filename, size=(width, height), profile='tiny')

    start_date = datetime.datetime.strptime(data[0]["date"], "%Y-%m-%d")
    week = 0

    for i, day in enumerate(data):
        date = datetime.datetime.strptime(day["date"], "%Y-%m-%d")
        x = week * (square_size + padding)
        y = date.weekday() * (square_size + padding)
        total_seconds = day.get("grand_total", {}).get("total_seconds", 0)
        level = intensity(total_seconds)
        dwg.add(dwg.rect(insert=(x, y), size=(square_size, square_size), fill=colors[level]))
        if date.weekday() == 6:
            week += 1


    dwg.save()

if __name__ == "__main__":
    data = get_data()
    draw_svg(data)
