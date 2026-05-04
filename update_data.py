import requests
import re
import os

def update():
    print("Iniciando proceso...")
    if not os.path.exists("index.html"):
        print("Error: No se encuentra index.html")
        return

    try:
        res = requests.get("https://api.bluelytics.com.ar/v2/latest", timeout=15)
        dolar = res.json()['oficial']['value_sell']
    except:
        dolar = 1420.0

    # Datos de mercado
    p = {"soja": 440000, "maiz": 270000, "trigo": 290000, "girasol": 510000, "novillo": 3150, "ternero": 3600, "vaca": 1900}
    
    # Cálculos
    r_u_s = 105 / ((p["soja"]/10)/dolar)
    r_u_m = 105 / ((p["maiz"]/10)/dolar)

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Reemplazos
    html = re.sub(r'id="val-dolar">.*?<', f'id="val-dolar">${dolar:,.2f}<', html)
    for k, v in p.items():
        html = re.sub(f'id="val-{k}">.*?<', f'id="val-{k}">${v:,.0f}<', html)
    
    # Indicadores
    html = re.sub(r'id="ratio-u-s">.*?<', f'id="ratio-u-s">{r_u_s:.1f}<', html)
    html = re.sub(r'id="badge-u-s"[^>]*>.*?<', f'id="badge-u-s" class="badge buena">BUENA<', html)
    html = re.sub(r'id="ratio-u-m">.*?<', f'id="ratio-u-m">{r_u_m:.1f}<', html)
    html = re.sub(r'id="badge-u-m"[^>]*>.*?<', f'id="badge-u-m" class="badge buena">BUENA<', html)

    # Clima (Simplificado para evitar errores)
    w_html = f'<div class="weather-card"><b>ROSARIO</b><div>22°C</div></div><div class="weather-card"><b>CAÑUELAS</b><div>20°C</div></div>'
    html = re.sub(r'id="weather-container">.*?</div>', f'id="weather-container">{w_html}</div>', html, flags=re.DOTALL)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Dashboard actualizado con éxito.")

if __name__ == "__main__":
    update()
