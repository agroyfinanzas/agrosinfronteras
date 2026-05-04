import requests
import re

def analizar(valor, tipo):
    # Umbrales para el semáforo (puedes ajustarlos a tu gusto)
    if "urea" in tipo:
        if valor < 15: return "Excelente", "ind-buena"
        if valor < 19: return "Regular", "ind-regular"
        return "Caro", "ind-mala"
    if "maiz_carne" in tipo:
        if valor > 12: return "Oportunidad", "ind-buena"
        if valor > 9: return "Equilibrio", "ind-regular"
        return "Desfavorable", "ind-mala"
    if "gasoil" in tipo:
        if valor < 12: return "Barato", "ind-buena"
        return "Elevado", "ind-mala"
    return "N/A", ""

def actualizar_todo():
    try:
        res = requests.get("https://api.bluelytics.com.ar/v2/latest")
        dolar = res.json()['oficial']['value_sell']
    except:
        dolar = 1382.50

    # Precios de referencia
    p = {
        "soja": 430000, "maiz": 262675, "trigo": 283412, "girasol": 500000, "sorgo": 269600, "cebada": 195000,
        "mag_novillo": 3050, "mag_novillito": 3360, "mag_ternero": 3450, "mag_vaca": 1920, "mag_conserva": 1380, "mag_toro": 1800
    }

    # Cálculos de Relaciones
    r_urea_s = 100 / (p["soja"] / dolar)
    r_urea_m = 100 / (p["maiz"] / dolar)
    r_gas_s = (1200 * 500) / (p["soja"] / 10)
    r_gas_m = (1200 * 500) / (p["maiz"] / 10)
    r_carne_t = p["mag_ternero"] / (p["maiz"] / 1000)
    r_carne_n = p["mag_novillo"] / (p["maiz"] / 1000)
    r_glifo_s = (10 * 100) / ((p["soja"] / 10) / dolar)

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Inyectar Dólar y Granos
    html = re.sub(r'id="valor-dolar">[^<]+', f'id="valor-dolar">${dolar:,.2f}', html)
    for g in ["soja", "maiz", "trigo", "girasol", "sorgo", "cebada"]:
        html = re.sub(f'id="precio-{g}">[^<]+', f'id="precio-{g}">${p[g]:,.0f}', html)
    for c in ["novillo", "novillito", "ternero", "vaca", "conserva", "toro"]:
        html = re.sub(f'id="mag-{c}">[^<]+', f'id="mag-{c}">${p["mag_"+c]:,.0f}', html)

    # Inyectar Relaciones e Indicadores (ESTO ES LO QUE TE FALTABA)
    def inyectar(id_val, id_ind, valor, tipo):
        nonlocal html
        txt, cls = analizar(valor, tipo)
        html = re.sub(f'id="{id_val}">[^<]+', f'id="{id_val}">{valor:.1f}', html)
        html = re.sub(f'id="{id_ind}" class="ind">[^<]+', f'id="{id_ind}" class="ind {cls}">{txt}', html)

    inyectar("rel-urea-soja", "ind-urea-soja", r_urea_s, "urea")
    inyectar("rel-urea-maiz", "ind-urea-maiz", r_urea_m, "urea")
    inyectar("rel-gasoil-soja", "ind-gasoil-soja", r_gas_s, "gasoil")
    inyectar("rel-gasoil-maiz", "ind-gasoil-maiz", r_gas_m, "gasoil")
    inyectar("rel-maiz-ternero", "ind-maiz-ternero", r_carne_t, "maiz_carne")
    inyectar("rel-maiz-novillo", "ind-maiz-novillo", r_carne_n, "maiz_carne")
    inyectar("rel-glifo-soja", "ind-glifo-soja", r_glifo_s, "glifo")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

actualizar_todo()
