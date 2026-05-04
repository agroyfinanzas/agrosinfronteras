import requests
import re

def actualizar_plataforma():
    # 1. Obtener Dólar oficial real (vía API)
    try:
        res = requests.get("https://api.bluelytics.com.ar/v2/latest")
        dolar = res.json()['oficial']['value_sell']
    except:
        dolar = 1382.50 # Valor de respaldo si la API falla

    # 2. Base de datos de precios (Valores que el bot inyectará)
    # Podes editar estos números manualmente en GitHub y el bot hará los cálculos
    p = {
        # GRANOS ROSARIO ($/tn)
        "soja": 430000,
        "maiz": 262675,
        "trigo": 283412,
        "girasol": 500000,
        "sorgo": 269600,
        "cebada": 195000,
        
        # GANADERÍA CAÑUELAS ($/kg)
        "mag_novillo": 3050,
        "mag_novillito": 3360,
        "mag_ternero": 3450,
        "mag_vaca": 1920,
        "mag_conserva": 1380,
        "mag_toro": 1800
    }

    # 3. Cálculos automáticos de Insumo/Producto
    # Basado en Urea a USD 1.000 la tonelada (USD 100 los 100kg)
    # La fórmula convierte el precio ARS a USD usando el dólar obtenido arriba
    rel_soja = 100 / (p["soja"] / dolar)
    rel_maiz = 100 / (p["maiz"] / dolar)

    # 4. Leer el archivo HTML
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 5. Inyectar Dólar
    html = re.sub(r'id="valor-dolar">[^<]+', f'id="valor-dolar">${dolar:,.2f}', html)

    # 6. Inyectar Granos (recorre la lista y busca los IDs en el HTML)
    for grano in ["soja", "maiz", "trigo", "girasol", "sorgo", "cebada"]:
        html = re.sub(f'id="precio-{grano}">[^<]+', f'id="precio-{grano}">${p[grano]:,.0f}', html)

    # 7. Inyectar Ganadería
    for cat in ["novillo", "novillito", "ternero", "vaca", "conserva", "toro"]:
        html = re.sub(f'id="mag-{cat}">[^<]+', f'id="mag-{cat}">${p["mag_"+cat]:,.0f}', html)

    # 8. Inyectar Relaciones Insumo/Producto
    html = re.sub(r'id="rel-urea-soja">[^<]+', f'id="rel-urea-soja">{rel_soja:.1f}', html)
    html = re.sub(r'id="rel-urea-maiz">[^<]+', f'id="rel-urea-maiz">{rel_maiz:.1f}', html)

    # 9. Guardar los cambios en el archivo
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    actualizar_plataforma()
