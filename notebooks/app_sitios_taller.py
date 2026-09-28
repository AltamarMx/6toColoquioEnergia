# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.25.0",
#     "pandas>=3.0",
#     "pvlib>=0.16",
#     "matplotlib>=3.11",
# ]
# ///

import marimo

__generated_with = "0.25.0"
app = marimo.App(
    width="medium",
    app_title="Del dato climático al kWh (taller)",
)


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import matplotlib.pyplot as plt
    from pvlib import irradiance
    from pvlib.location import Location

    return Location, irradiance, mo, pd, plt


@app.cell
def _(mo):
    mo.md(r"""
    # Del dato climático al kWh · versión de taller

    Este cuaderno **ya funciona** para un solo sitio. Tu trabajo es completarlo en cuatro pasos,
    marcados como `TODO 1` a `TODO 4`. Después de cada uno, el resultado cambia solo.

    | Paso | Qué harás | Dónde |
    |---|---|---|
    | TODO 1 | Calcular para **todos** los sitios seleccionados, no solo el primero | celda "Cálculo" |
    | TODO 2 | Pasar de kWh/m² a **kWh del sistema** | celda "Cálculo" |
    | TODO 3 | Añadir los modelos de difusa **Hay-Davies** y **Perez** al menú | celda "Parámetros" |
    | TODO 4 | Agregar el **botón de descarga** de resultados | última celda |
    """)
    return


@app.cell
def _(pd):
    URL_CATALOGO = "https://raw.githubusercontent.com/AltamarMx/6toColoquioEnergia/main/data/sitios_mexico.csv"
    try:
        catalogo = pd.read_csv("data/sitios_mexico.csv")   # copia local, si existe
    except FileNotFoundError:
        catalogo = pd.read_csv(URL_CATALOGO)                # si no, desde GitHub
    return (catalogo,)


@app.cell
def _(catalogo, mo):
    tabla_sitios = mo.ui.table(
        catalogo, selection="multi", initial_selection=[0, 4, 11, 16], page_size=18,
        label="**1. Elige sitios del catálogo**",
    )
    sitios_extra = mo.ui.text_area(
        placeholder="Mi pueblo, 24.80, -104.20, 1900, America/Mexico_City",
        label="**2. Agrega sitios propios** (uno por línea: nombre, latitud, longitud, altitud m, zona horaria)",
        rows=3, full_width=True,
    )
    mo.vstack([tabla_sitios, sitios_extra])
    return sitios_extra, tabla_sitios


@app.cell
def _(mo):
    # ---- Parámetros -------------------------------------------------------
    fecha = mo.ui.date(value="2026-03-21", label="Fecha de inicio")
    periodo = mo.ui.dropdown({"Un día": 1, "Año completo": 365}, value="Un día", label="Periodo")
    inclinacion = mo.ui.slider(0, 90, step=5, value=20, label="Inclinación β (°)")
    azimut = mo.ui.slider(0, 355, step=5, value=180, label="Azimut γ (°): 0=N 90=E 180=S 270=O")
    albedo = mo.ui.slider(0.0, 0.9, step=0.05, value=0.20, label="Albedo ρ")
    turbidez = mo.ui.slider(2.0, 7.0, step=0.1, value=3.0, label="Turbidez de Linke")

    # TODO 3: agrega "Hay-Davies" -> "haydavies" y "Perez" -> "perez" al diccionario de opciones.
    modelo = mo.ui.dropdown(
        {"Isotrópico": "isotropic"},
        value="Isotrópico", label="Modelo de difusa",
    )

    area = mo.ui.number(1, 10000, value=10, label="Área del sistema (m²)")
    eficiencia = mo.ui.slider(0.10, 0.25, step=0.01, value=0.20, label="Eficiencia del sistema")
    mo.vstack([
        mo.md("**3. Parámetros**"),
        mo.hstack([fecha, periodo, modelo, turbidez]),
        mo.hstack([inclinacion, azimut, albedo]),
        mo.hstack([area, eficiencia]),
    ])
    return albedo, azimut, fecha, inclinacion, modelo, periodo, turbidez


@app.cell
def _(catalogo, pd, sitios_extra, tabla_sitios):
    def _parsear_extra(texto):
        filas = []
        for linea in texto.strip().splitlines():
            partes = [p.strip() for p in linea.split(",")]
            if len(partes) < 3:
                continue
            filas.append({
                "nombre": partes[0], "estado": "(propio)",
                "latitud": float(partes[1]), "longitud": float(partes[2]),
                "altitud_m": float(partes[3]) if len(partes) > 3 and partes[3] else 0.0,
                "zona_horaria": partes[4] if len(partes) > 4 and partes[4] else "America/Mexico_City",
            })
        return pd.DataFrame(filas, columns=catalogo.columns)

    sitios_sel = pd.concat([tabla_sitios.value, _parsear_extra(sitios_extra.value)], ignore_index=True)
    return (sitios_sel,)


@app.cell
def _(Location, irradiance, pd):
    def calcular_sitio(nombre, lat, lon, alt, tz, inicio, dias, tilt, az, albedo, modelo, tl):
        """Energía de cielo despejado sobre una superficie (β=tilt, γ=az) para un sitio.

        Es exactamente la cadena de la sesión 1:
        Location -> posición solar -> cielo despejado -> proyección a la superficie -> integral.
        Devuelve (resumen: dict, serie: Series con la irradiancia total sobre la superficie).
        """
        paso = "10min" if dias == 1 else "1h"
        loc = Location(lat, lon, tz=tz, altitude=alt, name=nombre)
        t0 = pd.Timestamp(inicio)
        tiempos = pd.date_range(t0, t0 + pd.Timedelta(days=dias), freq=paso, tz=tz, inclusive="left")

        sol = loc.get_solarposition(tiempos)
        cielo = loc.get_clearsky(tiempos, model="ineichen", linke_turbidity=tl)
        poa = irradiance.get_total_irradiance(
            surface_tilt=tilt, surface_azimuth=az,
            solar_zenith=sol["apparent_zenith"], solar_azimuth=sol["azimuth"],
            dni=cielo["dni"], ghi=cielo["ghi"], dhi=cielo["dhi"],
            dni_extra=irradiance.get_extra_radiation(tiempos),
            airmass=loc.get_airmass(tiempos, solar_position=sol)["airmass_relative"],
            albedo=albedo, model=modelo,
        )
        dt_h = pd.Timedelta(paso) / pd.Timedelta(hours=1)
        resumen = {
            "sitio": nombre,
            "kWh/m² horizontal": cielo["ghi"].sum() * dt_h / 1000,
            "kWh/m² superficie": poa["poa_global"].sum() * dt_h / 1000,
        }
        return resumen, poa["poa_global"]

    return (calcular_sitio,)


@app.cell
def _(
    albedo,
    azimut,
    calcular_sitio,
    fecha,
    inclinacion,
    mo,
    modelo,
    pd,
    periodo,
    sitios_sel,
    turbidez,
):
    # ---- Cálculo ------------------------------------------------------------
    mo.stop(sitios_sel.empty, mo.md("⚠️ Selecciona al menos un sitio."))

    _filas, series = [], {}

    # TODO 1: ahora solo se calcula el PRIMER sitio (fila 0). Conviértelo en un ciclo sobre
    # todas las filas de `sitios_sel`. Pista:
    #     for _, _s in sitios_sel.iterrows():
    #         ...
    _s = sitios_sel.iloc[0]
    _resumen, _serie = calcular_sitio(
        _s["nombre"], _s["latitud"], _s["longitud"], _s["altitud_m"], _s["zona_horaria"],
        fecha.value, periodo.value, inclinacion.value, azimut.value,
        albedo.value, modelo.value, turbidez.value,
    )
    _filas.append(_resumen)
    series[_s["nombre"]] = _serie

    resultados = pd.DataFrame(_filas)
    resultados["ganancia vs horizontal"] = resultados["kWh/m² superficie"] / resultados["kWh/m² horizontal"] - 1

    # TODO 2: energía del sistema = kWh/m² sobre la superficie × área (m²) × eficiencia.
    # Los controles se leen con `area.value` y `eficiencia.value`.
    resultados["kWh sistema"] = 0.0

    resultados = resultados.sort_values("kWh/m² superficie", ascending=False).reset_index(drop=True)
    return resultados, series


@app.cell
def _(mo, periodo, resultados):
    _unidad = "kWh/m² en el día" if periodo.value == 1 else "kWh/m² en el año"
    mo.vstack([
        mo.md(f"**4. Resultados** ({_unidad}, cielo despejado)"),
        mo.ui.table(resultados.round(2), selection=None),
    ])
    return


@app.cell
def _(periodo, plt, resultados, series):
    _fig, (_ax1, _ax2) = plt.subplots(1, 2, figsize=(12, 4), width_ratios=[1, 1.4])

    _ax1.barh(resultados["sitio"], resultados["kWh/m² superficie"], color="#f4a300")
    _ax1.invert_yaxis()
    _ax1.set_xlabel("kWh/m² sobre la superficie")
    _ax1.grid(alpha=.3, axis="x")

    if periodo.value == 1:
        for _nombre, _serie in series.items():
            _hora = _serie.index.hour + _serie.index.minute / 60
            _ax2.plot(_hora, _serie.values, lw=1.5, label=_nombre)
        _ax2.set_xlabel("Hora local"); _ax2.set_ylabel("W/m²")
        _ax2.set_title("Irradiancia sobre la superficie")
    else:
        for _nombre, _serie in series.items():
            _mensual = _serie.groupby(_serie.index.month).sum() / 1000
            _ax2.plot(_mensual.index, _mensual.values, marker="o", lw=1.5, label=_nombre)
        _ax2.set_xticks(range(1, 13)); _ax2.set_xticklabels(list("EFMAMJJASOND"))
        _ax2.set_ylabel("kWh/m² por mes"); _ax2.set_title("Energía mensual sobre la superficie")
    _ax2.grid(alpha=.3); _ax2.legend(frameon=False, fontsize=8, ncol=2)
    plt.tight_layout()
    _fig
    return


@app.cell
def _(mo, resultados):
    # TODO 4: sustituye este mensaje por un botón de descarga:
    #     mo.download(data=resultados.to_csv(index=False).encode("utf-8"),
    #                 filename="resultados_sitios.csv", mimetype="text/csv",
    #                 label="Descargar resultados (CSV)")
    mo.md(f"TODO 4: aquí va el botón de descarga. La tabla tiene {len(resultados)} fila(s).")
    return


if __name__ == "__main__":
    app.run()
