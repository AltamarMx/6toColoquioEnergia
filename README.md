# Del dato climático al kWh: ciencia de datos con Python

6to Coloquio de Energía · IER-UNAM

Taller en dos sesiones. La primera es una charla sobre por qué aprender Python para
ciencia de datos, cómo trabajar de forma reproducible con narrativa computacional y
Jupyter vs marimo, con la irradiancia solar en Torreón, Coahuila, como hilo conductor.
La segunda construye, celda por celda, una app en marimo que calcula la energía solar
para una lista de sitios de México definida por el usuario.

El taller se realiza en [molab](https://molab.marimo.io), sin instalación local.

## Contenido

| Archivo | Propósito |
|---|---|
| `presentacion.qmd` | Las dos sesiones en una sola presentación (Quarto + reveal.js): la charla con celdas Python ejecutables y la app celda por celda, con botón de copiar en cada bloque |
| `notebooks/demo_irradiancia.py` | Demo de marimo para la sesión 1 (Torreón, controles reactivos) |
| `notebooks/app_sitios.py` | La app completa de la sesión 2 (lo que se construye en las diapositivas) |
| `notebooks/app_sitios_taller.py` | Punto de control: funciona para un sitio y tiene 4 TODOs |
| `data/sitios_mexico.csv` | Catálogo de 18 ciudades con latitud, longitud, altitud y zona horaria |
| `scripts/verificar_celdas.py` | Comprueba que el código de las diapositivas coincide con `app_sitios.py` |
| `docs/` | Salida renderizada que sirve GitHub Pages |
| `custom.scss`, `_quarto.yml` | Tema y configuración de Quarto |

Presentación publicada: <https://altamarmx.github.io/6toColoquioEnergia/>

## Regenerar las presentaciones (para el autor)

Requiere [uv](https://docs.astral.sh/uv/) y [Quarto](https://quarto.org) ≥ 1.4.

```bash
uv sync                                   # instala dependencias (incluye jupyter para Quarto)
uv run quarto render                      # genera docs/index.html
git add docs && git commit -m "Publica" && git push   # GitHub Pages sirve la carpeta docs/ de main
uv run python scripts/verificar_celdas.py # el código de las diapositivas == app_sitios.py
uv run quarto preview presentacion.qmd    # vista previa con recarga automática
```

## Correr los cuadernos en tu máquina

```bash
uv run marimo edit notebooks/app_sitios.py    # como cuaderno
uv run marimo run notebooks/app_sitios.py     # como app
uv run python notebooks/app_sitios.py         # como script
uv run marimo check notebooks/                # revisa el grafo de dependencias
```

Cada cuaderno declara sus dependencias en un encabezado `# /// script`, así que también
corre fuera del repositorio con `uv run notebooks/app_sitios.py` o `marimo edit --sandbox`.

## Atajos en las presentaciones

- `f` pantalla completa · `s` notas del ponente · `o` vista general
- `b` pizarrón · `c` puntero · `?` lista completa de atajos
