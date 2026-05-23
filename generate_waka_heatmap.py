import requests
import svgwrite
import os
import base64
from datetime import datetime, timedelta

# Cargar un archivo .env simple si existe (sin dependencia externa)
def load_dotenv(dotenv_path=".env"):
    if not os.path.exists(dotenv_path):
        return
    with open(dotenv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                os.environ.setdefault(k, v)

load_dotenv()

# Configuración
API_KEY = os.getenv("WAKATIME_API_KEY")
USERNAME = os.getenv("WAKATIME_USERNAME", "current")
THEMES = {
    "light": {
        "background": None,
        "text": "#0F172A",
        "legend_text": "#0F172A",
        "stroke": "#D7DEE8",
        "colors": [
            "#E5E7EB",  # Under 1 hr / casi sin color
            "#C8D5E6",  # 1 - 3 hrs
            "#A8C1DA",  # 4 - 8 hrs
            "#7FA4C5",  # 9 - 10 hrs
            "#44698B",  # 11 - 12 hrs
            "#0B1220",  # 13+ hrs
        ],
    },
    "dark": {
        "background": None,
        "text": "#8AA4C8",
        "legend_text": "#F2F7FF",
        "stroke": "#132033",
        "colors": [
            "#151D2B",  # Under 1 hr / casi sin color
            "#2B3A4C",  # 1 - 3 hrs
            "#3C526A",  # 4 - 8 hrs
            "#56728D",  # 9 - 10 hrs
            "#7C9AB9",  # 11 - 12 hrs
            "#F2F7FF",  # 13+ hrs
        ],
    },
}


def get_headers():
    if not API_KEY:
        raise Exception("WAKATIME_API_KEY no está configurado")

    auth_string = f"{API_KEY}:"
    b64_auth = base64.b64encode(auth_string.encode()).decode()
    return {"Authorization": f"Basic {b64_auth}"}


def get_data():
    headers = get_headers()
    
    user_res = requests.get(f"https://wakatime.com/api/v1/users/{USERNAME}", headers=headers, timeout=15)
    if user_res.status_code != 200:
        raise Exception(f"Error al obtener usuario: {user_res.status_code}")
    user_id = user_res.json()["data"]["id"]
    
    # /insights/days devuelve el heatmap anual que usa el perfil.
    api_url = f"https://wakatime.com/api/v1/users/{user_id}/insights/days?range=last_year"
    
    res = requests.get(api_url, headers=headers, timeout=15)
    print("Respuesta de la API:", res.text[:200])
    if res.status_code != 200:
        raise Exception(f"Error al obtener datos: {res.status_code}")
    
    payload = res.json()["data"]
    insights = payload.get("days", [])
    if not insights:
        raise Exception("La API no devolvió días para el heatmap")

    totals_by_date = {}
    for day in insights:
        current_date = datetime.strptime(day["date"], "%Y-%m-%d").date()
        totals_by_date[current_date] = float(day.get("total") or 0)

    first_date = min(totals_by_date)
    last_date = max(totals_by_date)

    # Alinear la grilla a columnas semanales completas: domingo -> sábado.
    grid_start = first_date - timedelta(days=(first_date.weekday() + 1) % 7)
    grid_end = last_date + timedelta(days=6 - ((last_date.weekday() + 1) % 7))

    data = []
    current_date = grid_start
    while current_date <= grid_end:
        data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "grand_total": {
                "total_seconds": totals_by_date.get(current_date, 0)
            }
        })
        current_date += timedelta(days=1)

    print("Rango API:", payload.get("human_readable_range"), first_date, last_date)
    
    # Debug: días con datos
    for d in data:
        if d["grand_total"]["total_seconds"] > 0:
            print(d["date"], d["grand_total"]["total_seconds"])

    return data

def intensity(duration):
    hours = duration / 3600
    if hours < 1:
        return 0
    if hours < 4:
        return 1
    if hours < 9:
        return 2
    if hours < 11:
        return 3
    if hours < 13:
        return 4
    return 5

def draw_svg(data, filename="waka-heatmap.svg", theme_name="light"):
    if not data:
        raise Exception("No hay datos para dibujar el heatmap")
    if theme_name not in THEMES:
        raise Exception(f"Tema no soportado: {theme_name}")

    theme = THEMES[theme_name]

    square_size = 12
    padding = 4
    radius = 2
    top_margin = 30
    left_margin = 56
    right_margin = 14
    bottom_margin = 36
    total_weeks = len(data) // 7
    chart_width = total_weeks * (square_size + padding) - padding
    chart_height = 7 * (square_size + padding) - padding
    width = left_margin + chart_width + right_margin
    height = top_margin + chart_height + bottom_margin
    dwg = svgwrite.Drawing(filename, size=(width, height), profile='tiny')
    chart_x = left_margin
    chart_y = top_margin

    if theme["background"]:
        dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill=theme["background"]))

    font_family = "Segoe UI, Arial, sans-serif"
    month_style = {
        "fill": theme["text"],
        "font_size": "12px",
        "font_family": font_family,
    }
    day_style = {
        "fill": theme["text"],
        "font_size": "12px",
        "font_family": font_family,
    }
    legend_style = {
        "fill": theme["legend_text"],
        "font_size": "12px",
        "font_family": font_family,
        "font_weight": "600",
    }

    last_month = None
    for index, day in enumerate(data):
        date = datetime.strptime(day["date"], "%Y-%m-%d")
        if date.day != 1:
            continue

        month_label = date.strftime("%b")
        if month_label == last_month:
            continue

        col = index // 7
        x = chart_x + col * (square_size + padding)
        dwg.add(dwg.text(month_label, insert=(x, 18), **month_style))
        last_month = month_label

    for label, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        y = chart_y + row * (square_size + padding) + square_size - 1
        dwg.add(dwg.text(label, insert=(10, y), **day_style))

    for index, day in enumerate(data):
        date = datetime.strptime(day["date"], "%Y-%m-%d")
        col = index // 7
        row = index % 7

        x = chart_x + col * (square_size + padding)
        y = chart_y + row * (square_size + padding)

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
            fill=theme["colors"][level],
            stroke=theme["stroke"],
            stroke_width=1,
            rx=radius,
            ry=radius,
        )
        rect.set_desc(title=label)  # 👈 Tooltip visible al pasar mouse
        dwg.add(rect)

    legend_y = chart_y + chart_height + 24
    legend_square = 10
    legend_gap = 4
    legend_width = 32 + 6 * legend_square + 5 * legend_gap + 40
    legend_x = width - right_margin - legend_width
    dwg.add(dwg.text("Less", insert=(legend_x, legend_y), **legend_style))

    legend_square_x = legend_x + 36
    for color in theme["colors"]:
        dwg.add(dwg.rect(
            insert=(legend_square_x, legend_y - legend_square + 1),
            size=(legend_square, legend_square),
            fill=color,
            stroke=theme["stroke"],
            stroke_width=1,
            rx=radius,
            ry=radius,
        ))
        legend_square_x += legend_square + legend_gap

    dwg.add(dwg.text("More", insert=(legend_square_x + 4, legend_y), **legend_style))

    dwg.save()


if __name__ == "__main__":
    data = get_data()
    draw_svg(data, "waka-heatmap.svg", "light")
    draw_svg(data, "waka-heatmap-dark.svg", "dark")
