"""Genera notebooks/taller_torreon.ipynb a partir de presentacion.qmd.

Recorre las diapositivas y copia, en orden, cada celda de código visible junto con el
título de su diapositiva y el texto que la acompaña. Así el cuaderno que abren los
estudiantes en Google Colab contiene exactamente las celdas de la presentación.

Uso:  uv run python scripts/generar_cuaderno.py
Quarto lo ejecuta solo antes de cada render (ver `pre-render` en _quarto.yml).
"""

import re
from pathlib import Path

import nbformat as nbf

RAIZ = Path(__file__).resolve().parent.parent
QMD = RAIZ / "presentacion.qmd"
SALIDA = RAIZ / "notebooks" / "taller_torreon.ipynb"
INCLUIR_OCULTAS = False   # True: también las celdas con echo/include: false (diagramas)

RE_SECCION = re.compile(r"^# (.+?)\s*(\{.*\})?\s*$")
RE_DIAPO = re.compile(r"^## (.+?)\s*(\{.*\})?\s*$")
RE_INLINE = re.compile(r"`\{python\} [^`]*`")


def limpiar_texto(lineas):
    """Texto de la diapositiva sin marcas de Quarto (:::, fragmentos, inline python)."""
    out = []
    for l in lineas:
        if l.strip().startswith(":::") or l.strip() == ". . .":
            continue
        out.append(RE_INLINE.sub("…", l))
    return "\n".join(out).strip()


def main():
    texto = QMD.read_text(encoding="utf-8")
    cuerpo = texto.split("\n---\n", 1)[1] if texto.startswith("---") else texto
    lineas = cuerpo.split("\n")

    celdas = [
        nbf.v4.new_markdown_cell(
            "# Del dato climático al kWh\n\n"
            "Cuaderno del taller, generado a partir de `presentacion.qmd`: las mismas celdas, "
            "en el mismo orden. Ejecuta las celdas de arriba hacia abajo.\n\n"
            "6to Coloquio de Energía · IER-UNAM · Guillermo Barrios del Valle"
        ),
        nbf.v4.new_code_cell(
            "# Google Colab ya trae pandas, numpy y matplotlib; solo falta pvlib.\n"
            "try:\n"
            "    import pvlib\n"
            "except ImportError:\n"
            "    %pip install -q pvlib"
        ),
    ]

    i = 0
    titulo_diapo = None
    while i < len(lineas):
        l = lineas[i]
        m = RE_SECCION.match(l)
        if m:
            celdas.append(nbf.v4.new_markdown_cell(f"# {m.group(1)}"))
            i += 1
            continue
        m = RE_DIAPO.match(l)
        if m:
            titulo_diapo = m.group(1)
            i += 1
            continue
        if l.strip() == "```{python}":
            j = i + 1
            opciones, codigo = {}, []
            while lineas[j].strip() != "```":
                if lineas[j].startswith("#|"):
                    k, _, v = lineas[j][2:].partition(":")
                    opciones[k.strip()] = v.strip()
                else:
                    codigo.append(lineas[j])
                j += 1
            oculta = opciones.get("echo") == "false" or opciones.get("include") == "false"
            # texto que sigue al bloque, hasta la próxima diapositiva o bloque
            k = j + 1
            comentario = []
            while k < len(lineas) and not (RE_DIAPO.match(lineas[k]) or RE_SECCION.match(lineas[k])
                                           or lineas[k].strip() == "```{python}"):
                comentario.append(lineas[k])
                k += 1
            if not oculta or INCLUIR_OCULTAS:
                if titulo_diapo:
                    celdas.append(nbf.v4.new_markdown_cell(f"## {titulo_diapo}"))
                    titulo_diapo = None
                celdas.append(nbf.v4.new_code_cell("\n".join(codigo).strip("\n")))
                nota = limpiar_texto(comentario)
                if nota:
                    celdas.append(nbf.v4.new_markdown_cell(nota))
            i = j + 1
            continue
        i += 1

    nb = nbf.v4.new_notebook(cells=celdas)
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.metadata["language_info"] = {"name": "python"}
    SALIDA.parent.mkdir(exist_ok=True)
    nbf.write(nb, SALIDA)
    n_codigo = sum(c.cell_type == "code" for c in celdas)
    print(f"{SALIDA.relative_to(RAIZ)}: {n_codigo} celdas de código, {len(celdas)} en total")


if __name__ == "__main__":
    main()
