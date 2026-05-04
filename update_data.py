import requests
import re
import os

def update():
    print("Iniciando actualización forzada...")
    
    # 1. Obtener Dólar (Si falla la web, usa uno manual para que no quede vacío)
    try:
        res = requests.get("https://api.bluelytics.com.ar/v2/latest", timeout=15)
        dolar_val = res.json()['oficial']['value_sell']
    except:
        dolar_val = 1419.0

    # 2. Precios del día (Cámbialos aquí si necesitas)
    precios = {
        "soja": 435000, "maiz": 265000, "trigo": 285000, "girasol": 510000,
        "sorgo": 240000, "cebada": 220000, "novillo": 3100, "ternero": 3550,
        "vaca": 1900, "vaquillona": 3000, "novillito": 3150, "toro": 1850
    }

    if not os.path.exists("index.html"):
        print("ERROR: No se encontró index.html")
        return

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Reemplazo de Dólar
    html = re.sub(r'id="val-dolar">.*?<', f'id="val-dolar">${dolar_val:,.2f}<', html)
    
    # Reemplazo de todos los precios de granos y carne
    for k, v in precios.items():
        pattern = f'id="val-{k}">.*?<'
        replacement = f'id="val-{k}">${v:,.0f}<'
        html = re.sub(pattern, replacement, html)

    # Cálculo e inyección de Indicadores (Urea)
    ratio_urea = 105 / ((precios["soja"]/10)/dolar_val)
    html = re.sub(r'id="ratio-u-s">.*?<', f'id="ratio-u-s">{ratio_urea:.1f}<', html)
    html = re.sub(r'id="badge-u-s"[^>]*>.*?<', f'id="badge-u-s" class="badge buena">BUENA<', html)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("Sincronización finalizada con éxito.")

if __name__ == "__main__":
    update()
