#!/usr/bin/env python3
"""
fetch_data.py — Agros Sin Fronteras · Intelligence Hub
=======================================================
Genera data.json con:
  - Dólar BNA (DolarAPI)
  - Pizarra de granos Rosario (BCR/CAC scraping)
  - Hacienda Cañuelas (Mercado Agroganadero)
  - Relaciones insumo/producto calculadas

Se ejecuta via GitHub Actions cada 6 horas en días hábiles.
"""

import json
import re
import sys
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

# ── Zona horaria Argentina ──────────────────────────────────────────────────
ARG = ZoneInfo("America/Argentina/Buenos_Aires")
NOW = datetime.now(ARG)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-AR,es;q=0.9",
}

TIMEOUT = 15


# ────────────────────────────────────────────────────────────────────────────
# 1. DÓLAR BNA — DolarAPI (gratuita, sin clave)
# ────────────────────────────────────────────────────────────────────────────
def fetch_dolar() -> dict:
    """Obtiene compra/venta del dólar oficial BNA desde dolarapi.com."""
    try:
        r = requests.get("https://dolarapi.com/v1/dolares/oficial", headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        return {
            "compra": float(data.get("compra", 0)),
            "venta":  float(data.get("venta",  0)),
            "fuente": "DolarAPI · BNA Oficial",
        }
    except Exception as e:
        print(f"[WARN] Dólar BNA: {e}", file=sys.stderr)
        return {"compra": 1370.0, "venta": 1382.5, "fuente": "fallback"}


# ────────────────────────────────────────────────────────────────────────────
# 2. GRANOS ROSARIO — BCR / CAC pizarra
# ────────────────────────────────────────────────────────────────────────────
def fetch_granos_bcr(tc_venta: float) -> dict:
    """
    Scrapea la pizarra de la CAC (BCR). Si falla, intenta Agrofy News.
    Devuelve dict con claves: soja, maiz, trigo, girasol, sorgo
    Cada entry: { ars, usd_tn, usd_qq, mes }
    """

    def parse_ars(txt: str) -> float | None:
        """Convierte '430.000' o '430000' a float."""
        if not txt:
            return None
        txt = txt.strip().replace("\xa0", "").replace("$", "").replace(" ", "")
        txt = re.sub(r"[^\d,.]", "", txt)
        # Formato argentino: 430.000,00 → quitar puntos, coma = decimal
        if "," in txt:
            txt = txt.replace(".", "").replace(",", ".")
        else:
            txt = txt.replace(".", "")
        try:
            return float(txt)
        except ValueError:
            return None

    granos = {}

    # ── Intento 1: BCR CAC ──────────────────────────────────────────────
    try:
        url = "https://www.cac.bcr.com.ar/es/precios-de-pizarra"
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # La tabla tiene filas con nombre del grano y precio
        keywords = {
            "soja":    ["soja"],
            "maiz":    ["maíz", "maiz"],
            "trigo":   ["trigo"],
            "girasol": ["girasol"],
            "sorgo":   ["sorgo"],
        }

        rows = soup.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) < 2:
                continue
            nombre = cells[0].get_text(strip=True).lower()
            for clave, aliases in keywords.items():
                if any(a in nombre for a in aliases) and clave not in granos:
                    # Buscar la primera celda numérica válida
                    for cell in cells[1:]:
                        val = parse_ars(cell.get_text(strip=True))
                        if val and val > 10000:
                            usd_tn = round(val / tc_venta, 2) if tc_venta else None
                            granos[clave] = {
                                "ars":    val,
                                "usd_tn": usd_tn,
                                "usd_qq": round(usd_tn / 10, 2) if usd_tn else None,
                                "mes":    "Disponible",
                                "fuente": "BCR/CAC",
                            }
                            break

        print(f"[BCR/CAC] Granos obtenidos: {list(granos.keys())}", file=sys.stderr)

    except Exception as e:
        print(f"[WARN] BCR scraping: {e}", file=sys.stderr)

    # ── Intento 2: Agrofy News (fallback) ───────────────────────────────
    if len(granos) < 3:
        try:
            url2 = "https://news.agrofy.com.ar/granos/precios-pizarra"
            r2 = requests.get(url2, headers=HEADERS, timeout=TIMEOUT)
            r2.raise_for_status()
            soup2 = BeautifulSoup(r2.text, "html.parser")

            keywords2 = {
                "soja":    ["soja"],
                "maiz":    ["maíz", "maiz"],
                "trigo":   ["trigo"],
                "girasol": ["girasol"],
                "sorgo":   ["sorgo"],
            }

            for row in soup2.find_all("tr"):
                cells = row.find_all(["td", "th"])
                if len(cells) < 2:
                    continue
                nombre = cells[0].get_text(strip=True).lower()
                for clave, aliases in keywords2.items():
                    if any(a in nombre for a in aliases) and clave not in granos:
                        for cell in cells[1:]:
                            val = parse_ars(cell.get_text(strip=True))
                            if val and val > 10000:
                                usd_tn = round(val / tc_venta, 2) if tc_venta else None
                                granos[clave] = {
                                    "ars":    val,
                                    "usd_tn": usd_tn,
                                    "usd_qq": round(usd_tn / 10, 2) if usd_tn else None,
                                    "mes":    "Disponible",
                                    "fuente": "Agrofy",
                                }
                                break
        except Exception as e2:
            print(f"[WARN] Agrofy scraping: {e2}", file=sys.stderr)

    # ── Fallback manual si todo falló ─────────────────────────────────────
    FALLBACKS = {
        "soja":    430000,
        "maiz":    262675,
        "trigo":   283412,
        "girasol": 500000,
        "sorgo":   269600,
    }
    for clave, ars in FALLBACKS.items():
        if clave not in granos:
            usd_tn = round(ars / tc_venta, 2) if tc_venta else None
            granos[clave] = {
                "ars":    ars,
                "usd_tn": usd_tn,
                "usd_qq": round(usd_tn / 10, 2) if usd_tn else None,
                "mes":    "Referencia",
                "fuente": "fallback",
            }
            print(f"[FALLBACK] {clave}: ${ars}", file=sys.stderr)

    return granos


# ────────────────────────────────────────────────────────────────────────────
# 3. HACIENDA — Mercado Agroganadero Cañuelas
# ────────────────────────────────────────────────────────────────────────────
def fetch_hacienda() -> dict:
    """
    Scrapea el Mercado Agroganadero de Cañuelas.
    Devuelve dict por categoría: { min, max, promedio }
    """
    hacienda = {}

    try:
        url = "https://www.mercadoagroganadero.com.ar/dll/hacienda1.dll/haciinfo000002"
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Mapeo de palabras clave → clave interna
        cat_map = {
            "novillito": ["novillito"],
            "novillo":   ["novillo"],
            "vaquillona":["vaquillona"],
            "vaca":      ["vaca"],
            "ternero":   ["ternero", "ternera"],
            "toro":      ["toro"],
        }

        def to_float(txt):
            txt = re.sub(r"[^\d,.]", "", txt.strip())
            try:
                return float(txt.replace(",", "."))
            except ValueError:
                return None

        rows = soup.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 5:
                continue
            nombre = cells[0].get_text(strip=True).lower()
            for clave, aliases in cat_map.items():
                if any(a in nombre for a in aliases) and clave not in hacienda:
                    nums = [to_float(c.get_text()) for c in cells[1:6]]
                    nums = [n for n in nums if n is not None and n > 100]
                    if len(nums) >= 2:
                        hacienda[clave] = {
                            "min":      min(nums),
                            "max":      max(nums),
                            "promedio": round(sum(nums) / len(nums)),
                            "fuente":   "MAG Cañuelas",
                        }

        print(f"[MAG] Hacienda obtenida: {list(hacienda.keys())}", file=sys.stderr)

    except Exception as e:
        print(f"[WARN] MAG Cañuelas scraping: {e}", file=sys.stderr)

    # ── Fallback hacienda ────────────────────────────────────────────────
    FALLBACKS_H = {
        "novillito": {"min": 2900, "max": 3360, "promedio": 3050},
        "novillo":   {"min": 2700, "max": 3100, "promedio": 2850},
        "vaquillona":{"min": 2800, "max": 3200, "promedio": 3000},
        "vaca":      {"min": 1700, "max": 1920, "promedio": 1800},
        "ternero":   {"min": 3200, "max": 3450, "promedio": 3300},
        "toro":      {"min": 1600, "max": 1800, "promedio": 1700},
    }
    for clave, vals in FALLBACKS_H.items():
        if clave not in hacienda:
            hacienda[clave] = {**vals, "fuente": "fallback"}
            print(f"[FALLBACK] hacienda/{clave}", file=sys.stderr)

    return hacienda


# ────────────────────────────────────────────────────────────────────────────
# 4. RELACIONES INSUMO / PRODUCTO
# ────────────────────────────────────────────────────────────────────────────
def calcular_relaciones(granos: dict, hacienda: dict, tc_venta: float) -> dict:
    """
    Calcula relaciones insumo/producto en qq del cultivo por unidad de insumo.
    Precios de insumos en USD (referencias actualizadas 2026).
    """

    # Precios de insumos en USD (por unidad indicada)
    INSUMOS_USD = {
        "urea_tn":        1000,   # USD/tn  (récord 2026)
        "fosfato_dap_tn":  600,   # USD/tn
        "glifosato_100l":   60,   # USD/100L
        "semilla_soja_ha":  80,   # USD/ha (bolsa 40 kg)
        "semilla_maiz_bolsa": 140, # USD/bolsa (70.000 semillas)
        "gasoil_500l":     250,   # USD/500L
    }

    def ars_qq(cultivo: str) -> float | None:
        """Precio en ARS por quintal."""
        data = granos.get(cultivo)
        if not data or not data.get("ars"):
            return None
        return data["ars"] / 10  # ars/tn → ars/qq

    def usd_qq(cultivo: str) -> float | None:
        return granos.get(cultivo, {}).get("usd_qq")

    def rel(insumo_usd: float, cultivo: str) -> float | None:
        """qq del cultivo necesarios para comprar 1 unidad del insumo."""
        precio_qq = usd_qq(cultivo)
        if not precio_qq or precio_qq == 0:
            return None
        return round(insumo_usd / precio_qq, 1)

    rels = {}

    # — Soja —
    rels["soja_urea"]           = rel(INSUMOS_USD["urea_tn"],        "soja")
    rels["soja_fosfato"]        = rel(INSUMOS_USD["fosfato_dap_tn"], "soja")
    rels["soja_glifosato_100l"] = rel(INSUMOS_USD["glifosato_100l"], "soja")
    rels["soja_semilla"]        = rel(INSUMOS_USD["semilla_soja_ha"], "soja")

    # — Maíz —
    rels["maiz_urea"]           = rel(INSUMOS_USD["urea_tn"],          "maiz")
    rels["maiz_fosfato"]        = rel(INSUMOS_USD["fosfato_dap_tn"],   "maiz")
    rels["maiz_glifosato_100l"] = rel(INSUMOS_USD["glifosato_100l"],   "maiz")
    rels["maiz_semilla"]        = rel(INSUMOS_USD["semilla_maiz_bolsa"],"maiz")

    # — Trigo —
    rels["trigo_urea"]          = rel(INSUMOS_USD["urea_tn"],        "trigo")
    rels["trigo_fosfato"]       = rel(INSUMOS_USD["fosfato_dap_tn"], "trigo")
    rels["trigo_glifosato_100l"]= rel(INSUMOS_USD["glifosato_100l"], "trigo")

    # — Ganaderas —
    nov  = hacienda.get("novillo",  {}).get("promedio")
    tern = hacienda.get("ternero",  {}).get("promedio")
    maiz_ars_tn = granos.get("maiz", {}).get("ars")
    soja_ars_tn = granos.get("soja", {}).get("ars")

    if nov and tern:
        rels["ternero_novillo"] = round(tern / nov, 2)  # kg ternero / kg novillo

    if maiz_ars_tn and nov:
        nov_ars_tn = nov * 1000  # ARS/kg → ARS/tn
        rels["maiz_kg_novillo"] = round(maiz_ars_tn / nov_ars_tn, 3)  # tn maíz / tn carne viva

    if soja_ars_tn and maiz_ars_tn and maiz_ars_tn > 0:
        rels["soja_maiz"] = round(soja_ars_tn / maiz_ars_tn, 2)

    return rels


# ────────────────────────────────────────────────────────────────────────────
# 5. MAIN — Ensamblar data.json
# ────────────────────────────────────────────────────────────────────────────
def main():
    print("=== fetch_data.py · Agros Sin Fronteras ===", file=sys.stderr)
    print(f"Timestamp: {NOW.isoformat()}", file=sys.stderr)

    dolar   = fetch_dolar()
    tc      = dolar.get("venta", 1382.5)
    granos  = fetch_granos_bcr(tc)
    hacienda = fetch_hacienda()
    relaciones = calcular_relaciones(granos, hacienda, tc)

    data = {
        "fecha":      NOW.strftime("%d/%m/%Y"),
        "hora":       NOW.strftime("%H:%M"),
        "timestamp":  NOW.isoformat(),
        "dolar":      dolar,
        "granos":     granos,
        "hacienda":   hacienda,
        "relaciones": relaciones,
    }

    output = json.dumps(data, ensure_ascii=False, indent=2)
    print(output)

    # Estadísticas
    print(f"\n[OK] Granos: {len(granos)} | Hacienda: {len(hacienda)} | Relaciones: {len(relaciones)}", file=sys.stderr)


if __name__ == "__main__":
    main()
