import requests
import re

# Configuración de Ciudades
CIUDADES = {
    "Rosario": (-32.9, -60.6), "Cañuelas": (-35.0, -58.7), 
    "Córdoba": (-31.4, -64.1), "Pehuajó": (-35.8, -61.8),
    "Salta": (-24.7, -65.4), "Bahía Blanca": (-38.7, -62.2)
}

def get_weather(lat, lon):
    try:
        r = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true", timeout=5).json()
        return r['current_weather']['temperature']
    except: return "--"

def analyze_ratio(val, tipo):
    if tipo == "urea":
        if val < 15: return "BUENA", "buena"
        if val < 19: return "REGULAR", "regular"
        return "CARA", "mala"
    if tipo == "carne":
        if val > 12: return "COMPRA", "buena"
        if val > 10: return "EQUILIBRIO", "regular"
        return "VENTA", "mala"
    return "ESTABLE", "buena"

def update():
    try:
        dolar = requests.get("https://api.bluelytics.com.ar/v2/latest").json()['oficial']['value_sell']
    except: dolar = 1425.0

    # DATOS DE MERCADO (Precios referenciales)
    p = {
        "soja": 435000, "maiz": 268000, "trigo": 290000, "girasol": 510000, "sorgo": 240000, "cebada": 220000,
        "novillo": 3150, "ternero": 3550, "vaca": 1900, "vaquillona": 3000, "novillito": 3100, "toro": 1800
    }

    # RATIOS TÉCNICOS
    r_u_s = 105 / ((p["soja"]/10)/dolar) # Urea USD 105 vs 10qq Soja
    r_u_m = 105 / ((p["maiz"]/10)/dolar)
    r_u_t = 105 / ((p["trigo"]/10)/dolar)
    r_c_t = p["ternero"] / (p["maiz"]/1000) # kg maiz por kg carne
    r_c_n = p["novillo"] / (p["maiz"]/1000)
    r_g_m = 13.2 # Referencia Gasoil/Maíz

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Reemplazo de Dólar y Granos
    html = re.sub(r'id="val-dolar">.*?<', f'id="val-dolar">${dolar:,.2f}<', html)
    for k, v in p.items():
        html = re.sub(f'id="val-{k}">.*?<', f'id="val-{k}">${v:,.0f}<', html)

    # Reemplazo de Indicadores
    ratios = {
        "u-s": (r_u_s, "urea"), "u-m": (r_u_m, "urea"), "u-t": (r_u_t, "urea"),
        "c-t": (r_c_t, "carne"), "c-n": (r_c_n, "carne"), "g-m": (r_g_m, "urea")
    }
    for rid, (val, tipo) in ratios.items():
        txt, cls = analyze_ratio(val, tipo)
        html = re.sub(f'id="ratio-{rid}">.*?<', f'id="ratio-{rid}">{val:.1f}<', html)
        html = re.sub(f'id="badge-{rid}"[^>]*>.*?<', f'id="badge-{rid}" class="badge {cls}">{txt}<', html)

    # Reemplazo de Clima
    w_html = ""
    for city, coords in CIUDADES.items():
        t = get_weather(coords[0], coords[1])
        w_html += f'<div class="weather-card"><div style="font-size:0.7rem; color:var(--muted);">{city.upper()}</div><div style="font-size:1.8rem; font-weight:900; color:var(--accent);">{t}°C</div></div>'
    html = re.sub(r'id="weather-container">.*?</div>', f'id="weather-container">{w_html}</div>', html, flags=re.DOTALL)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    update()
