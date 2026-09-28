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
app = marimo.App(width="medium", app_title="Demo: irradiancia en Torreón")


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
    # Demo: irradiancia solar en Torreón

    Es el mismo cálculo de la presentación, pero **reactivo**: mueve un control y
    todo lo que depende de él se recalcula. No hay botón de "ejecutar".

    - Cada celda es una función de Python; sus variables son globales del cuaderno.
    - Una variable solo puede definirse en **una** celda. marimo construye el grafo con eso.
    - Este archivo es Python puro: ábrelo en un editor de texto y compruébalo.
    """)
    return


@app.cell
def _(mo):
    fecha = mo.ui.date(value="2026-03-21", label="Fecha")
    turbidez = mo.ui.slider(2.0, 7.0, step=0.1, value=3.0, label="Turbidez de Linke")
    inclinacion = mo.ui.slider(0, 90, step=5, value=90, label="Inclinación β (°)")
    azimut = mo.ui.slider(0, 355, step=5, value=90, label="Azimut γ (°): 0=N 90=E 180=S 270=O")
    albedo = mo.ui.slider(0.0, 0.9, step=0.05, value=0.20, label="Albedo ρ")
    mo.vstack([mo.hstack([fecha, turbidez]), mo.hstack([inclinacion, azimut, albedo])])
    return albedo, azimut, fecha, inclinacion, turbidez


@app.cell
def _(Location, fecha, pd, turbidez):
    torreon = Location(latitude=25.54, longitude=-103.41,
                       tz="America/Mexico_City", altitude=1120, name="Torreón")
    _inicio = pd.Timestamp(fecha.value)
    horas = pd.date_range(_inicio, _inicio + pd.Timedelta(days=1), freq="10min", tz=torreon.tz)
    sol = torreon.get_solarposition(horas)
    cielo = torreon.get_clearsky(horas, model="ineichen", linke_turbidity=turbidez.value)
    return cielo, sol


@app.cell
def _(albedo, azimut, cielo, inclinacion, irradiance, sol):
    poa = irradiance.get_total_irradiance(
        surface_tilt=inclinacion.value, surface_azimuth=azimut.value,
        solar_zenith=sol["apparent_zenith"], solar_azimuth=sol["azimuth"],
        dni=cielo["dni"], ghi=cielo["ghi"], dhi=cielo["dhi"],
        albedo=albedo.value, model="isotropic")
    return (poa,)


@app.cell
def _(cielo, plt, poa):
    _fig, (_ax1, _ax2) = plt.subplots(1, 2, figsize=(11, 3.6), sharey=True)
    cielo[["ghi", "dni", "dhi"]].plot(ax=_ax1, lw=2)
    _ax1.set_title("Cielo despejado: GHI, DNI, DHI")
    _ax1.set_ylabel("W/m²"); _ax1.set_xlabel("Hora local"); _ax1.grid(alpha=.3)
    _ax1.legend(["GHI", "DNI", "DHI"], frameon=False)
    poa[["poa_global", "poa_direct", "poa_sky_diffuse", "poa_ground_diffuse"]].plot(ax=_ax2, lw=1.5)
    _ax2.lines[0].set_linewidth(2.8)
    _ax2.set_title("Sobre la superficie (β, γ)")
    _ax2.set_xlabel("Hora local"); _ax2.grid(alpha=.3)
    _ax2.legend(["Total", "Directa", "Difusa cielo", "Reflejada suelo"], frameon=False, fontsize=9)
    plt.tight_layout()
    _fig
    return


@app.cell
def _(cielo, mo, poa):
    _dt_h = 10 / 60
    _e_sup = poa["poa_global"].sum() * _dt_h / 1000
    _e_hor = cielo["ghi"].sum() * _dt_h / 1000
    mo.md(
        f"**Energía del día** · superficie: **{_e_sup:.2f} kWh/m²** · "
        f"horizontal: {_e_hor:.2f} kWh/m² · cociente: {_e_sup / _e_hor:.0%}"
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Prueba del estado oculto

    La celda de abajo define `borrar_me`. La siguiente la usa.
    **Borra la celda de abajo** y observa qué pasa con la que la usa.
    En Jupyter, la variable seguiría viva en el kernel.
    """)
    return


@app.cell
def _():
    borrar_me = 42
    return (borrar_me,)


@app.cell
def _(borrar_me, mo):
    mo.md(f"`borrar_me` vale **{borrar_me}**")
    return


if __name__ == "__main__":
    app.run()
