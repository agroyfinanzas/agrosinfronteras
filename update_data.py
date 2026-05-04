import requests
import re

CIUDADES = {"Rosario": (-32.9, -60.6), "Cañuelas": (-35.0, -58.7), "Córdoba": (-31.4, -64.1), "Salta": (-24.7, -65.4), "Pehuajó": (-35.8, -61.8)}

def get_weather(lat, lon):
    try:
        r = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true", timeout=10).json()
        return r['current_weather']['temperature']
    except: return "--"

def analyze_ratio(val, tipo):
    if tipo == "urea":
        if val < 15: return "BUENA", "buena"
        if val < 19: return "REGULAR", "regular"
        return "CARA", "mala"
    return "COMPRA", "buena" if val > 12 else "VENTA", "mala"

def update():
    try:
        dolar = requests.get("https://api.bluelytics.com.ar/v2/latest").json()['oficial']['value_sell']
    except: dolar = 1420.0

    p = {
        "soja": 440000, "maiz": 270000, "trigo": 290000, "girasol": 510000, "sorgo": 240000, "cebada": 220000,
        "novillo": 3150, "ternero": 3600, "novillito": 3100, "vaquillona": 3050, "vaca": 1900, "toro": 1850
    }

    r_u_s = 105 / ((p["soja"]/10)/dolar)
    r_u_m = 105 / ((p["maiz"]/10)/dolar)
    r_c_t = p["ternero"] / (p["maiz"]/1000)

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = re.sub(r'id="val-dolar">.*?<', f'id="val-dolar">${dolar:,.2f}<', html)
    for k, v in p.items():
        html = re.sub(f'id="val-{k}">.*?<', f'id="val-{k}">${v:,.0f}<', html)

    ratios = {"u-s": (r_u_s, "urea"), "u-m": (r_u_m, "urea"), "c-t": (r_c_t, "carne")}
    for rid, (val, tipo) in ratios.items():
        txt, cls = analyze_ratio(val, tipo)
        html = re.sub(f'id="ratio-{rid}">.*?<', f'id="ratio-{rid}">{val:.1f}<', html)
        html = re.sub(f'id="badge-{rid}"[^>]*>.*?<', f'id="badge-{rid}" class="badge {cls}">{txt}<', html)

    w_html = ""
    for city, coords in CIUDADES.items():
        temp = get_weather(coords[0], coords[1])
        w_html += f'<div class="weather-card"><b style="font-size:0.7rem; color:var(--muted)">{city.upper()}</b><div style="font-size:1.5rem; font-weight:900; color:var(--accent)">{temp}°C</div></div>'
    html = re.sub(r'id="weather-container">.*?</div>', f'id="weather-container">{w_html}</div>', html, flags=re.DOTALL)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Actualización completa.")

if __name__ == "__main__":
    update()
