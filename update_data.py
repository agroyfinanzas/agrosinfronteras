import requests
import re

def analizar(valor, tipo):
    if "urea" in tipo:
        if valor < 15: return "BUENA", "ind-buena"
        if valor < 18: return "EQUILIBRIO", "ind-regular"
        return "CARA", "ind-mala"
    if "carne" in tipo:
        if valor > 12: return "COMPRA", "ind-compra"
        if valor > 10: return "EQUILIBRIO", "ind-equilibrio"
        return "VENTA", "ind-mala"
    if "gasoil" in tipo:
        if valor < 14: return "BUENA", "ind-buena"
        return "ALTA", "ind-mala"
    return "--", ""

def actualizar():
    try:
        res = requests.get("https://api.bluelytics.com.ar/v2/latest")
        dolar = res.json()['oficial']['value_sell']
    except:
        dolar = 1385.00

    # Precios simulados
    p = {
        "soja": 440000, "maiz": 268000, "trigo": 290000, "girasol": 515000,
        "mag_novillo": 3150, "mag_ternero": 3600
    }

    # Cálculos
    urea_usd_100kg = 105
    gasoil_ars_500l = 1250 * 500
    
    soja_usd_tn = p["soja"] / dolar
    maiz_usd_tn = p["maiz"] / dolar

    r_u_s = urea_usd_100kg / (soja_usd_tn / 10)
    r_u_m = urea_usd_100kg / (maiz_usd_tn / 10)
    r_g_s = gasoil_ars_500l / (p["soja"] / 10)
    r_g_m = gasoil_ars_500l / (p["maiz"] / 10)
    r_c_t = p["mag_ternero"] / (p["maiz"] / 1000)
    r_c_n = p["mag_novillo"] / (p["maiz"] / 1000)

    with open("index.html", "r", encoding="utf-8") as f:
        h = f.read()

    # Inyección de Pizarra
    h = re.sub(r'id="valor-dolar"[^>]*>.*?<', f'id="valor-dolar">${dolar:,.2f}<', h)
    for g in ["soja", "maiz", "trigo", "girasol"]:
        h = re.sub(f'id="precio-{g}"[^>]*>.*?<', f'id="precio-{g}">${p[g]:,.0f}<', h)

    # Inyección de Indicadores (Con los nuevos Badges)
    def escribir(id_n, id_b, val, tipo):
        nonlocal h
        txt, cls = analizar(val, tipo)
        h = re.sub(f'id="{id_n}"[^>]*>.*?<', f'id="{id_n}" class="ip-num">{val:.1f}<', h)
        h = re.sub(f'id="{id_b}"[^>]*>.*?<', f'id="{id_b}" class="badge {cls}">{txt}<', h)

    escribir("rel-u-s", "ind-u-s", r_u_s, "urea")
    escribir("rel-u-m", "ind-u-m", r_u_m, "urea")
    escribir("rel-g-s", "ind-g-s", r_g_s, "gasoil")
    escribir("rel-g-m", "ind-g-m", r_g_m, "gasoil")
    escribir("rel-c-t", "ind-c-t", r_c_t, "carne")
    escribir("rel-c-n", "ind-c-n", r_c_n, "carne")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(h)

actualizar()
