import requests
import re
import os

def update():
    print("Iniciando actualización de datos...")
    
    # 1. Intentar obtener dólar real
    try:
        res = requests.get("https://api.bluelytics.com.ar/v2/latest", timeout=15)
        dolar = res.json()['oficial']['value_sell']
    except:
        dolar = 1425.0 # Valor de respaldo

    # 2. Precios del día (Podés cambiarlos acá manualmente)
    p = {
        "soja": 440000, "maiz": 270000, "trigo": 290000, "girasol": 515000,
        "novillo": 3150, "ternero": 3600, "vaca": 1950
    }

    # 3. Cálculos de Ratios
    ratio_urea = 105 / ((p["soja"]/10)/dolar)

    # 4. Abrir el archivo index.html
    if not os.path.exists("index.html"):
        print("Error fatídico: No se encuentra index.html en la carpeta")
        return

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 5. INYECCIÓN DE DATOS (REEMPLAZO DE LOS "--")
    html = re.sub(r'id="val-dolar">.*?<', f'id="val-dolar">${dolar:,.2f}<', html)
    
    for grain, price in p.items():
        # Busca id="val-soja">--< y lo cambia por el precio
        pattern = f'id="val-{grain}">.*?<'
        replacement = f'id="val-{grain}">${price:,.0f}<'
        html = re.sub(pattern, replacement, html)

    # Reemplazo de Indicadores
    html = re.sub(r'id="ratio-u-s">.*?<', f'id="ratio-u-s">{ratio_urea:.1f}<', html)
    html = re.sub(r'id="badge-u-s"[^>]*>.*?<', f'id="badge-u-s" class="badge buena">BUENA<', html)

    # 6. Guardar cambios
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("¡Éxito! El archivo index.html ha sido actualizado.")

if __name__ == "__main__":
    update()
