import requests
import re

# Configuración de Ciudades para Clima
CIUDADES = {
    "Rosario": {"lat": -32.94, "lon": -60.63},
    "Cañuelas": {"lat": -35.05, "lon": -58.76},
    "Córdoba": {"lat": -31.41, "lon": -64.18},
    "Pehuajó": {"lat": -35.81, "lon": -61.89},
    "Salta": {"lat": -24.78, "lon": -65.41},
    "B. Blanca": {"lat": -38.71, "lon": -62.27}
}

def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        data = requests.get(url, timeout=10).json()
        return data['current_weather']['temperature']
    except: return "--"

def analyze_ratio(val, type):
    if type == "urea":
        if val < 15: return "BUENA", "buena"
        if val < 19: return "REGULAR", "regular"
        return "CARA", "mala"
    if type == "carne":
        if val > 12: return "COMPRA", "buena"
        if val > 10: return "EQUILIBRIO", "regular"
        return "VENTA", "mala"
    return "", ""

def update_dashboard():
    try:
        # Obtenemos el dólar real
        dolar = requests.get("https://api.bluelytics.com.ar/v2/latest").json()['oficial']['value_sell']
    except:
        dolar = 1420.0

    # PRECIOS DEL DÍA (Podés editarlos acá manualmente antes de correrlo)
    p = {
        "soja": 435000, "maiz": 268000,
        "novillo": 3150, "ternero": 3550
    }

    # Cálculos de Ratios Insumo/Producto
    r_u_s = 105 / ((p["soja"]/10)/dolar) 
    r_u_m = 105 / ((p["maiz"]/10)/dolar)
    r_c_t = p["ternero"] / (p["maiz"]/1000)
    r_c_n = p["novillo"] / (p["maiz"]/1000)

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Inyección de datos al HTML
    html = re.sub(r'id="val-dolar">.*?<', f'id="val-dolar">${dolar:,.2f}<', html)
    for k, v in p.items():
        html = re.sub(f'id="val-{k}">.*?<', f'id="val-{k}">${v:,.0f}<', html)

    ratios = {
        "u-s": (r_u_s, "urea"), "u-m": (r_u_m, "urea"),
        "c-t": (r_c_t, "carne"), "c-n": (r_c_n, "carne")
    }
    for id_r, (val, tipo) in ratios.items():
        txt, cls = analyze_ratio(val, tipo)
        html = re.sub(f'id="ratio-{id_r}">.*?<', f'id="ratio-{id_r}">{val:.1f}<', html)
        html = re.sub(f'id="badge-{id_r}"[^>]*>.*?<', f'id="badge-{id_r}" class="badge {cls}">{txt}<', html)

    # Clima Dinámico Nacional
    weather_html = ""
    for city, coord in CIUDADES.items():
        temp = get_weather(coord['lat'], coord['lon'])
        weather_html += f'''
        <div class="weather-card">
            <div style="font-size: 0.7rem; color: var(--muted); font-weight: 700;">{city.upper()}</div>
            <div class="weather-temp">{temp}°C</div>
        </div>'''
    html = re.sub(r'id="weather-container">.*?</div>', f'id="weather-container">{weather_html}</div>', html, flags=re.DOTALL)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("¡Dashboard de Agros Sin Fronteras Sincronizado!")

if __name__ == "__main__":
    update_dashboard()
