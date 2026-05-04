import requests
import re

# 1. Obtener Dólar oficial de Bluelytics (API Gratuita)
try:
    response = requests.get("https://api.bluelytics.com.ar/v2/latest")
    dolar = response.json()['oficial']['value_sell']
except:
    dolar = 1382.50 # Valor por defecto si falla la red

# 2. Precios base (Simulados para el ejemplo)
precio_soja_ars = 430000 
precio_maiz_ars = 262675
urea_usd_tn = 1000

# 3. Cálculos de Insumo/Producto (Quintales necesarios)
rel_soja = (urea_usd_tn / 10) / (precio_soja_ars / dolar)
rel_maiz = (urea_usd_tn / 10) / (precio_maiz_ars / dolar)

# 4. Inyectar datos en el HTML usando los IDs
with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(r'id="valor-dolar">[^<]+', f'id="valor-dolar">${dolar:,.2f}', content)
content = re.sub(r'id="rel-urea-soja">[^<]+', f'id="rel-urea-soja">{rel_soja:.1f}', content)
content = re.sub(r'id="rel-urea-maiz">[^<]+', f'id="rel-urea-maiz">{rel_maiz:.1f}', content)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
