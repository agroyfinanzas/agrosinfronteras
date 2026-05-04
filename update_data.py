import requests
import re
import os

CIUDADES = {"Rosario": (-32.9, -60.6), "Cañuelas": (-35.0, -58.7), "Córdoba": (-31.4, -64.1)}

def update():
    try:
        # Buscamos el Oficial de BNA
        res = requests.get("https://api.bluelytics.com.ar/v2/latest", timeout=15).json()
        dolar = res['oficial']['value_sell']
    except: dolar = 1435.0

    p = {
        "soja": 445000, "maiz": 275000, "trigo": 298000, 
        "sorgo": 238000, "cebada": 225000, "novillo": 3190
    }

    # Relaciones
    r_maiz_novillo = p["novillo"] / (p["maiz"] / 1000)
    r_urea_maiz = 550 / ((p["maiz"]/10)/dolar) # Urea USD 550 ref.
    r_soja_maiz = p["soja"] / p["maiz"]

    if not os.path.exists("index.html"): return

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Inyección
    html = re.sub(r'id="val-dolar">.*?<', f'id="val-dolar">${dolar:,.2f}<', html)
    for k, v in p.items():
        html = re.sub(f'id="val-{k}">.*?<', f'id="val-{k}">${v:,.0f}<', html)

    html = re.sub(r'id="ratio-c-n">.*?<', f'id="ratio-c-n">{r_maiz_novillo:.1f}<', html)
    html = re.sub(r'id="ratio-u-m">.*?<', f'id="ratio-u-m">{r_urea_maiz:.1f}<', html)
    html = re.sub(r'id="ratio-s-m">.*?<', f'id="ratio-s-m">{r_soja_maiz:.2f}<', html)

    # Clima
    w_html = ""
    for c, coord in CIUDADES.items():
        try:
            t = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={coord[0]}&longitude={coord[1]}&current_weather=true").json()['current_weather']['temperature']
            w_html += f'<div class="weather-card"><b>{c}</b><div style="font-size:1.5rem;color:var(--accent);font-weight:900;">{t}°C</div></div>'
        except: pass
    html = re.sub(r'id="weather-container">.*?</div>', f'id="weather-container">{w_html}</div>', html, flags=re.DOTALL)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    update()
