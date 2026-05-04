import requests
import re

def analizar(valor, tipo):
    if "urea" in tipo:
        if valor < 15: return "Buena", "ind-buena"
        if valor < 19: return "Regular", "ind-regular"
        return "Caro", "ind-mala"
    if "carne" in tipo:
        if valor > 12: return "Compra", "ind-buena"
        if valor > 9: return "Equilibrio", "ind-regular"
        return "Desfavorable", "ind-mala"
    if "gasoil" in tipo:
        if valor < 12: return "Barato", "ind-buena"
        return "Elevado", "ind-mala"
    return "N/A", ""

def actualizar():
    try:
        res = requests.get("https://api.bluelytics.com.ar/v2/latest")
        dolar = res.json()['oficial']['value_sell']
    except:
        dolar = 1382.50

    # Datos de mercado base
    p = {
        "soja": 430000, "maiz": 262675, "trigo": 283412, "girasol": 500000, "sorgo": 269600, "cebada": 195000,
        "mag_novillo": 3050, "mag_novillito": 3360, "mag_ternero": 3450, "mag_vaca": 1920, "mag_conserva": 1380, "mag_toro": 1800
    }

    # Cálculos
    r_u_s = 100 / (p["soja"] / dolar)
    r_u_m = 100 / (p["maiz"] / dolar)
    r_g_s = (1200 * 500) / (p["soja"] / 10)
    r_g_m = (1200 * 500) / (p["maiz"] / 10)
    r_c_t = p["mag_ternero"] / (p["maiz"] / 1000)
    r_c_n = p["mag_novillo"] / (p["maiz"] / 1000)
    r_gl_s = (10 * 100) / ((p["soja"] / 10) / dolar)

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Inyectar Dólar y Granos
    html = re.sub(r'id="valor-dolar">[^<]+', f'id="valor-dolar">${dolar:,.2f}', html)
    for g in ["soja", "maiz", "trigo", "girasol", "sorgo", "cebada"]:
        html = re.sub(f'id="precio-{g}">[^<]+', f'id="precio-{g}">${p[g]:,.0f}', html)
    for c in ["novillo", "novillito", "ternero", "vaca", "conserva", "toro"]:
        html = re.sub(f'id="mag-{c}">[^<]+', f'id="mag-{c}">${p["mag_"+c]:,.0f}', html)

    # Inyectar Relaciones y Botones (Aseguramos que coincidan con el HTML)
    def escribir(id_n, id_b, val, tipo):
        nonlocal html
        txt, cls = analizar(val, tipo)
        html = re.sub(f'id="{id_n}">[^<]+', f'id="{id_n}">{val:.1f}', html)
        html = re.sub(f'id="{id_b}" class="ind">[^<]+', f'id="{id_b}" class="ind {cls}">{txt}', html)

    escribir("rel-u-s", "ind-u-s", r_u_s, "urea")
    escribir("rel-u-m", "ind-u-m", r_u_m, "urea")
    escribir("rel-g-s", "ind-g-s", r_g_s, "gasoil")
    escribir("rel-g-m", "ind-g-m", r_g_m, "gasoil")
    escribir("rel-c-t", "ind-c-t", r_c_t, "carne")
    escribir("rel-c-n", "ind-c-n", r_c_n, "carne")
    escribir("rel-gl-s", "ind-gl-s", r_gl_s, "urea")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

actualizar()
