import requests
import re

def actualizar_mercados():
    # 1. Obtener Dólar oficial real
    try:
        res = requests.get("https://api.bluelytics.com.ar/v2/latest")
        dolar = res.json()['oficial']['value_sell']
    except:
        dolar = 1382.50

    # 2. Datos de Mercados (Precios que el bot inyectará)
    # Aquí podés cambiar los números a mano si querés, 
    # o dejar que el bot los maneje
    pizarra = {
        "soja": 430000,
        "maiz": 262675,
        "novillo": 3050,
        "ternero": 3450
    }

    # 3. Cálculos automáticos de Insumo/Producto
    # Urea a 1000 USD/tn (100 USD los 100kg)
    rel_soja = 100 / (pizarra["soja"] / dolar)
    rel_maiz = 100 / (pizarra["maiz"] / dolar)

    # 4. Inyección en el HTML
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Reemplazos con expresiones regulares (buscan el ID y cambian el valor)
    html = re.sub(r'id="valor-dolar">[^<]+', f'id="valor-dolar">${dolar:,.2f}', html)
    html = re.sub(r'id="precio-soja">[^<]+', f'id="precio-soja">${pizarra["soja"]:,.0f}', html)
    html = re.sub(r'id="precio-maiz">[^<]+', f'id="precio-maiz">${pizarra["maiz"]:,.0f}', html)
    html = re.sub(r'id="mag-novillo">[^<]+', f'id="mag-novillo">${pizarra["novillo"]:,.0f}', html)
    html = re.sub(r'id="mag-ternero">[^<]+', f'id="mag-ternero">${pizarra["ternero"]:,.0f}', html)
    html = re.sub(r'id="rel-urea-soja">[^<]+', f'id="rel-urea-soja">{rel_soja:.1f}', html)
    html = re.sub(r'id="rel-urea-maiz">[^<]+', f'id="rel-urea-maiz">{rel_maiz:.1f}', html)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    actualizar_mercados()
