# 🌾 Agros Sin Fronteras · Intelligence Hub

Panel de mercados agropecuarios argentinos con actualización automática cada 6 horas.

## 📋 Contenido

| Archivo | Descripción |
|---|---|
| `index.html` | Frontend completo (una sola página) |
| `fetch_data.py` | Script que scrapea precios y genera `data.json` |
| `data.json` | Datos de mercado (generado automáticamente) |
| `requirements.txt` | Dependencias Python |
| `.github/workflows/update-data.yml` | GitHub Actions (actualización automática) |

## 🚀 Cómo publicar en GitHub Pages (paso a paso)

### 1. Crear repositorio en GitHub

1. Ir a [github.com/new](https://github.com/new)
2. Nombre: `agrosinfronteras` (o el que quieras)
3. Marcarlo como **público** ✅ (necesario para GitHub Pages gratis)
4. **NO** inicializar con README
5. Click en **Create repository**

### 2. Subir los archivos

```bash
# En tu computadora, en la carpeta con los archivos:
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/agrosinfronteras.git
git push -u origin main
```

> Reemplazá `TU_USUARIO` con tu usuario de GitHub.

### 3. Activar GitHub Pages

1. En el repo → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / folder: `/ (root)`
4. Click **Save**
5. En 1-2 minutos tu sitio estará en:
   `https://TU_USUARIO.github.io/agrosinfronteras/`

### 4. Verificar el workflow

1. Ir a **Actions** en tu repo
2. Verás el workflow `Actualizar datos de mercado`
3. Click en **Run workflow** para hacer la primera actualización manual
4. De ahí en adelante se actualiza solo cada 6 horas (lun-vie)

## ⚙️ Cómo funciona

```
GitHub Actions (cada 6h)
    │
    ▼
fetch_data.py
    ├── DolarAPI → dólar BNA oficial
    ├── BCR/CAC → pizarra granos Rosario
    ├── Mercado Agroganadero → hacienda Cañuelas
    └── Cálculo → relaciones insumo/producto
    │
    ▼
data.json (commit automático al repo)
    │
    ▼
index.html lee data.json al cargar
```

## 🔧 Personalización

### Cambiar frecuencia de actualización

Editar `.github/workflows/update-data.yml`, línea `cron`:
```yaml
# Cada 3 horas en días hábiles:
- cron: '0 9,12,15,18,21 * * 1-5'
```

### Agregar/quitar cultivos

En `fetch_data.py`, modificar el dict `FALLBACKS` y `keywords` en `fetch_granos_bcr()`.

### Cambiar precios de insumos de referencia

En `fetch_data.py`, función `calcular_relaciones()`, dict `INSUMOS_USD`.

## 📊 Fuentes de datos

| Dato | Fuente | API/Scraping |
|---|---|---|
| Dólar BNA | [DolarAPI](https://dolarapi.com) | API REST gratuita |
| Granos Rosario | [BCR/CAC](https://www.cac.bcr.com.ar) | HTML scraping |
| Hacienda Cañuelas | [MAG](https://www.mercadoagroganadero.com.ar) | HTML scraping |
| Clima | [Open-Meteo](https://open-meteo.com) | API REST gratuita (en JS) |

> **Nota:** Los scrapers pueden romperse si los sitios cambian su estructura HTML.
> En ese caso, el sitio usa los valores `fallback` definidos en `fetch_data.py`.

## 🛠 Correr localmente

```bash
pip install -r requirements.txt
python fetch_data.py > data.json
# Abrir index.html en el navegador (necesita un servidor local):
python -m http.server 8080
# → http://localhost:8080
```

## 📝 Licencia

Uso interno / no comercial. Datos de mercado de acceso público.
