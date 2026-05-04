import requests
import re
import os

def update():
    print("Iniciando actualización...")
    
    # Precios manuales por si falla la API
    dolar = 1425.0
    precios = {
        "soja": 440000, "maiz": 270000, "trigo": 290000,
        "novillo": 3150, "ternero": 3600, "vaca": 1900
    }

    try:
        res = requests.get("https://api.bluelytics.com.ar/v2/latest", timeout=10)
        dolar = res.json()['oficial']['value_sell']
    except:
        print("API Dólar falló, usando valor manual.")

    if not os.path.exists("index.html"):
        print("ERROR: No se encuentra el archivo index.html")
        return

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Reemplazo de Dólar
    html = re.sub(r'id="val-dolar">.*?<', f'id="val-dolar">${dolar:,.2f}<', html)
    
    # Reemplazo de Precios
    for k, v in precios.items():
        html = re.sub(f'id="val-{k}">.*?<', f'id="val-{k}">${v:,.0f}<', html)
    
    # Indicadores
    ratio = 105 / ((precios["soja"]/10)/dolar)
    html = re.sub(r'id="ratio-u-s">.*?<', f'id="ratio-u-s">{ratio:.1f}<', html)
    html = re.sub(r'id="badge-u-s"[^>]*>.*?<', f'id="badge-u-s" class="badge buena">BUENA<', html)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("¡Proceso terminado con éxito!")

if __name__ == "__main__":
    update()
