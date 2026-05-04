import requests
import re

def analizar(valor, tipo):
    if "urea" in tipo:
        if valor < 15: return "Buena", "ind-buena"
        if valor < 19: return "Regular", "ind-regular"
        return "Caro", "ind-mala"
    if "carne" in tipo:
        # Favorable para el ganadero si 1kg de carne compra mucho maíz
        if valor > 12: return "Favorable", "ind-buena"
        if valor > 10: return "Equilibrio", "ind-regular"
        return "Desfavorable", "ind-mala"
    if "gas" in tipo:
        if valor < 14: return "Barato", "ind-buena"
        return "Elevado", "ind-mala"
    return "N/A", ""

def actualizar():
    try:
        res = requests.get("https://api.bluelytics.com.ar/v2/latest")
        dolar = res.json()['oficial']['value_sell']
    except:
        dolar = 1382.50

    # Precios pizarra y MAG
    p = {
        "soja": 430000, "maiz": 262675, "trigo": 283412, "girasol": 500000, "sorgo": 269600, "cebada": 195000,
        "mag_novillo": 3050, "mag_novillito": 3360, "mag_vaquillona": 3200, "mag_ternero": 3450, "mag_ternera": 3350, "mag_vaca": 1920, "mag_conserva": 1380, "mag_toro": 1800
    }

    # --- CÁLCULOS ---
    
    # 1. Urea (USD/USD): qq de grano para 100kg Urea (Base USD 1000/tn)
    costo_100kg_urea_usd = 100
    r_u_s = costo_100kg_urea_usd / ((p["soja"] / 10) / dolar)
    r_u_m = costo_100kg_urea_usd / ((p["maiz"] / 10) / dolar)

    # 2. Gasoil ($/$ ARS): qq de grano para 500L (Base $1200/litro)
    costo_500l_gasoil_ars = 1200 * 500
    r_g_s = costo_500l_gasoil_ars / (p["soja"] / 10)
    r_g_m = costo_500l_gasoil_ars / (p["maiz"] / 10)

    # 3. Carne/Maíz (kg/kg): kg de Maíz que compras con 1kg de Carne
    # $/kg Carne / $/kg Maíz
    r_c_t = p["mag_ternero"] / (p["maiz"] / 1000)
    r_c_n = p["mag_novillo"] / (p["maiz"] / 1000)

    with open("index.html", "r", encoding="utf-8") as f:
        h = f.read()

    # Reemplazos de Precios
    h = re.sub(r'id="valor-dolar"[^>]*>.*?<', f'id="valor-dolar">${dolar:,.2f}<', h)
    for g in ["soja", "maiz", "trigo", "girasol", "sorgo", "cebada"]:
        h = re.sub(f'id="precio-{g}"[^>]*>.*?<', f'id="precio-{g}">${p[g]:,.0f}<', h)
    for c in ["novillo", "novillito", "vaquillona", "ternero", "ternera", "vaca", "conserva", "toro"]:
        h = re.sub(f'id="mag-{c}"[^>]*>.*?<', f'id="mag-{c}">${p["mag_"+c]:,.0f}<', h)

    # Reemplazos de Indicadores
    def escribir(id_n, id_b, val, tipo):
        nonlocal h
        txt, cls = analizar(val, tipo)
        h = re.sub(f'id="{id_n}"[^>]*>.*?<', f'id="{id_n}" class="ip-qty">{val:.1f}<', h)
        h = re.sub(f'id="{id_b}"[^>]*>.*?<', f'id="{id_b}" class="ind {cls}">{txt}<', h)

    escribir("rel-u-s", "ind-u-s", r_u_s, "urea")
    escribir("rel-u-m", "ind-u-m", r_u_m, "urea")
    escribir("rel-g-s", "ind-g-s", r_g_s, "gas")
    escribir("rel-g-m", "ind-g-m", r_g_m, "gas")
    escribir("rel-c-t", "ind-c-t", r_c_t, "carne")
    escribir("rel-c-n", "ind-c-n", r_c_n, "carne")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(h)

if __name__ == "__main__":
    actualizar()
