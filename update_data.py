import requests
import re

# Ciudades Clima
CIUDADES = {"Rosario": (-32.9, -60.6), "Cañuelas": (-35.0, -58.7), "Córdoba": (-31.4, -64.1), "Salta": (-24.7, -65.4)}

def get_weather(lat, lon):
    try:
        r = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()
        return r['current_weather']['temperature']
    except: return "--"

def update():
    # 1. Obtener Dólar
    try:
        dolar = requests.get("https://api.bluelytics.com.ar/v2/latest").json()['oficial']['value_sell']
    except: dolar = 1420.0

    # 2. Precios (Editá estos números y corré el script)
    p = {"soja": 435000, "maiz": 268000, "novillo": 3150, "ternero": 3650}

    # 3. Leer HTML
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 4. Reemplazar Precios y Dólar
    html = re.sub(r'id="val-dolar">.*?<', f'id="val-dolar">${dolar:,.2f}<', html)
    for k, v in p.items():
        html = re.sub(f'id="val-{k}">.*?<', f'id="val-{k}">${v:,.0f}<', html)

    # 5. Reemplazar Clima
    weather_html = ""
    for city, coords in CIUDADES.items():
        temp = get_weather(coords[0], coords[1])
        weather_html += f'<div class="weather-card"><b>{city}</b><div>{temp}°C</div></div>'
    html = re.sub(r'id="weather-container">.*?</div>', f'id="weather-container">{weather_html}</div>', html, flags=re.DOTALL)

    # 6. Guardar cambios
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Sincronización completa.")

if __name__ == "__main__":
    update()
