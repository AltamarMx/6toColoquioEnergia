"""Comprueba que cada bloque `.celda` de presentacion.qmd exista, línea por línea, en notebooks/app_sitios.py.

Uso:  uv run python scripts/verificar_celdas.py
"""
import re, sys, pathlib

raiz = pathlib.Path(__file__).resolve().parent.parent
qmd = (raiz / "presentacion.qmd").read_text()
src = {l.strip() for l in (raiz / "notebooks" / "app_sitios.py").read_text().splitlines()}
bloques = re.findall(r"```\{\.python \.celda[^\n]*\}\n(.*?)```", qmd, flags=re.S)
faltan = [l for b in bloques for l in b.splitlines() if l.strip() and l.strip() not in src]
print(f"{len(bloques)} celdas en las diapositivas; líneas que no están en app_sitios.py: {len(faltan)}")
for l in faltan:
    print("   ", l)
sys.exit(1 if faltan else 0)
