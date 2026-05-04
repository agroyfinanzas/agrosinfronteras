import requests
import re
from bs4 import BeautifulSoup

def obtener_datos():
    # 1. Obtener Dólar oficial de Bluelytics
    try:
        response = requests.get("https://api.bluelytics.com.ar/v2/latest")
        dolar = response.json()['oficial']['value_sell']
    except:
        dolar = 1382.50 # Valor de respaldo

    # 2. Precios de Granos (BCR) y Hacienda (MAG)
    # Nota: Aquí definimos valores base. Para un scraping real y estable 
    # de estas webs, se requieren selectores que cambian frecuentemente.
    datos = {
        "soja_ars": 430000,
        "maiz_ars": 262675,
        "trigo_ars": 283412,
        "mag_novillo": 3050,
        "mag_ternero": 3450
    }

    # Lógica de cálculo Insumo/Producto (Urea a 1000 USD/tn)
    urea_usd_100kg = 100
    datos["rel_soja"] = urea_usd_100kg / (datos["soja_ars"] / dolar)
    datos["rel_maiz"] = urea_usd_100kg / (datos["maiz_ars"] / dolar)

    return dolar, datos

dolar, d = obtener_datos()

# 3. Leer y actualizar el HTML
with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Inyectar Dólar
content = re.sub(r'id="valor-dolar">[^<]+', f'id="valor-dolar">${dolar:,.2f}', content)

# Inyectar Granos Rosario
content = re.sub(r'id="precio-soja">[^<]+', f'id="precio-soja">${d["soja_ars"]:,.0f}', content)
content = re.sub(r'id="precio-maiz">[^<]+', f'id="precio-maiz">${d["maiz_ars"]:,.0f}', content)

# Inyectar Hacienda Cañuelas
content = re.sub(r'id="mag-novillo">[^<]+', f'id="mag-novillo">${d["mag_novillo"]:,.0f}', content)
content = re.sub(r'id="mag-ternero">[^<]+', f'id="mag-ternero">${d["mag_ternero"]:,.0f}', content)

# Inyectar Relaciones
content = re.sub(r'id="rel-urea-soja">[^<]+', f'id="rel-urea-soja">{d["rel_soja"]:.1f}', content)
content = re.sub(r'id="rel-urea-maiz">[^<]+', f'id="rel-urea-maiz">{d["rel_maiz"]:.1f}', content)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
