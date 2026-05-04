import requests
import re
import os

def update():
    # 1. Verificar si el index existe antes de empezar
    if not os.path.exists("index.html"):
        print("Error: No se encuentra el archivo index.html")
        return

    try:
        # 2. Obtener Dólar
        res_dolar = requests.get("https://api.bluelytics.com.ar/v2/latest", timeout=15)
        dolar = res_dolar.json()['oficial']['value_sell']
    except Exception as e:
        print(f"Error al obtener dólar: {e}")
        dolar = 1420.0

    # Precios de prueba
    p = {"soja": 445000, "maiz": 275000, "novillo": 3200, "ternero": 3700}

    # 3. Leer HTML
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 4. Reemplazos (con seguridad si no encuentra la etiqueta)
    html = re.sub(r'id="val-dolar">.*?<', f'id="val-dolar">${dolar:,.2f}<', html)
    for k, v in p.items():
        pattern = f'id="val-{k}">.*?<'
        html = re.sub(pattern, f'id="val-{k}">${v:,.0f}<', html)

    # 5. Escribir cambios
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Sincronización exitosa en el archivo index.html")

if __name__ == "__main__":
    update()
