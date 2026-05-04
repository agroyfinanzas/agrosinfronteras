import requests
import re

def analizar(valor, tipo):
    if "tn" in tipo: # Urea/Soja tn/tn
        if valor < 2.1: return "Barata", "ind-buena"
        if valor < 2.5: return "Normal", "ind-regular"
        return "Cara", "ind-mala"
    if "unit" in tipo: # Gasoil lt / Maíz kg
        if valor < 6.0: return "Favorable", "ind-buena"
        return "Caro", "ind-mala"
    if "urea" in tipo:
        if valor < 15: return "Buena", "ind-buena"
        return "Cara", "ind-mala"
    if "carne" in tipo:
        if valor > 12: return "Favorable", "ind-buena"
        return "Mala", "ind-mala"
    if "gas" in tipo:
        if valor < 14: return "Barata", "ind-buena"
        return "Elevada", "ind-mala"
    return "N/A", ""

def actualizar():
    try:
        res = requests.get("https://api.bluelytics.com.ar/v2/latest")
        dolar = res.json()['oficial']['value_sell']
    except:
        dolar = 1385.00

    p = {
        "soja": 435000, "maiz": 265000, "trigo": 285000, "girasol": 510000, "sorgo": 270000, "cebada": 198000,
        "mag_novillo": 3100, "mag_novillito": 3400, "mag_vaquillona": 3250, "mag_ternero": 3500, "mag_ternera": 3400, "mag_vaca": 1950, "mag_conserva": 1400, "mag_toro": 1850
    }

    # --- MATEMÁTICA DE INTERCAMBIO ---
    
    # Precios Insumos
    urea_usd_tn = 1000
    gasoil_ars_lt = 1250
    gasoil_usd_lt = gasoil_ars_lt / dolar
    
    # Precios Granos
    soja_usd_tn = p["soja"] / dolar
    maiz_usd_tn = p["maiz"] / dolar
    maiz_usd_kg = maiz_usd_tn / 1000

    # Relaciones solicitadas
    rel_u_s_tn = urea_usd_tn / soja_usd_tn      # (Urea usd/tn) / (Soja usd/tn)
    rel_g_m_unit = gasoil_usd_lt / maiz_usd_kg  # (Gasoil usd/lt) / (Maiz usd/kg)

    # Relaciones de Poder de Compra (qq y kg)
    r_u_s = 100 / (soja_usd_tn / 10)            # qq Soja para 100kg Urea
    r_g_m = (gasoil_ars_lt * 500) / (p["maiz"] / 10) # qq Maíz para 500L Gasoil
    r_c_t = p["mag_ternero"] / (p["maiz"] / 1000)    # kg Maíz por 1kg Ternero
    r_c_n = p["mag_novillo"] / (p["maiz"] / 1000)    # kg Maíz por 1kg Novillo

    with open("index.html", "r", encoding="utf-8") as f:
        h = f.read()

    # Inyección de Dólar y Pizarra
    h = re.sub(r'id="valor-dolar"[^>]*>.*?<', f'id="valor-dolar">${dolar:,.2f}<', h)
    for g in ["soja", "maiz", "trigo", "girasol", "sorgo", "cebada"]:
        h = re.sub(f'id="precio-{g}"[^>]*>.*?<', f'id="precio-{g}">${p[g]:,.0f}<', h)
    for c in ["novillo", "novillito", "vaquillona", "ternero", "ternera", "vaca", "conserva", "toro"]:
        h = re.sub(f'id="mag-{c}"[^>]*>.*?<', f'id="mag-{c}">${p["mag_"+c]:,.0f}<', h)

    # Función para inyectar indicadores
    def escribir(id_n, id_b, val, tipo):
        nonlocal h
        txt, cls = analizar(val, tipo)
        h = re.sub(f'id="{id_n}"[^>]*>.*?<', f'id="{id_n}" class="ip-qty">{val:.2f}<', h)
        h = re.sub(f'id="{id_b}"[^>]*>.*?<', f'id="{id_b}" class="ind {cls}">{txt}<', h)

    # Inyectar todos los indicadores
    escribir("rel-u-s-tn", "ind-u-s-tn", rel_u_s_tn, "tn")
    escribir("rel-u-s", "ind-u-s", r_u_s, "urea")
    escribir("rel-g-m-unit", "ind-g-m-unit", rel_g_m_unit, "unit")
    escribir("rel-g-m", "ind-g-m", r_g_m, "gas")
    escribir("rel-c-t", "ind-c-t", r_c_t, "carne")
    escribir("rel-c-n", "ind-c-n", r_c_n, "carne")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(h)

if __name__ == "__main__":
    actualizar()
