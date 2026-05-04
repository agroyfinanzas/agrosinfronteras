import requests
import re

def analizar_situacion(valor, tipo):
    # Umbrales históricos aproximados
    if tipo == "urea_soja":
        if valor < 15: return "Buena", "ind-buena"
        if valor < 19: return "Regular", "ind-regular"
        return "Mala", "ind-mala"
    
    if tipo == "maiz_carne":
        if valor > 12: return "Compra", "ind-buena" # Carne cara vs maíz barato
        if valor > 9: return "Equilibrio", "ind-regular"
        return "Desfavorable", "ind-mala"
    
    return "N/A", ""

def actualizar():
    try:
        res = requests.get("https://api.bluelytics.com.ar/v2/latest")
        dolar = res.json()['oficial']['value_sell']
    except:
        dolar = 1382.50

    p = {"soja": 430000, "maiz": 262675, "mag_novillo": 3050, "mag_ternero": 3450}
    
    # Cálculos
    rel_urea_soja = 100 / (p["soja"] / dolar)
    rel_maiz_ternero = p["mag_ternero"] / (p["maiz"] / 1000)

    # Análisis
    txt_urea, cls_urea = analizar_situacion(rel_urea_soja, "urea_soja")
    txt_carne, cls_carne = analizar_situacion(rel_maiz_ternero, "maiz_carne")

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Inyección de valores y clases CSS para colores
    html = re.sub(r'id="rel-urea-soja">[^<]+', f'id="rel-urea-soja">{rel_urea_soja:.1f}', html)
    html = re.sub(r'id="ind-urea-soja" class="ind">[^<]+', f'id="ind-urea-soja" class="ind {cls_urea}">{txt_urea}', html)
    
    html = re.sub(r'id="rel-maiz-ternero">[^<]+', f'id="rel-maiz-ternero">{rel_maiz_ternero:.1f}', html)
    html = re.sub(r'id="ind-maiz-ternero" class="ind">[^<]+', f'id="ind-maiz-ternero" class="ind {cls_carne}">{txt_carne}', html)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

actualizar()
