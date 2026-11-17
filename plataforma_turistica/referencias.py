"""Integra Airbnb para CABA y EOH para las demás localidades."""
import pandas as pd
from .datos import RAIZ
from .etl import integrar_tablas
from .ocupacion import calcular_referencia_airbnb, cargar_eoh_localidades


def integrar_referencias(tablas, eventos, semana):
    catalogo = tablas["destinos"]
    tiene_caba = catalogo["clave"].eq("buenos aires").any()
    referencia = (calcular_referencia_airbnb(RAIZ / "datos" / "inside_airbnb" / "calendar.csv.gz", semana)
                  if tiene_caba else {"actual": None, "anterior": None})
    otras = catalogo.loc[catalogo["clave"].ne("buenos aires")]
    historico = cargar_eoh_localidades(RAIZ / "datos" / "eoh_cuadros_2025.zip", otras, semana)
    if referencia["anterior"] is not None:
        anterior = pd.DataFrame([{"clave": "buenos aires", "destino": "Buenos Aires",
                                  "fecha": semana - pd.Timedelta(days=7), "ocupacion": referencia["anterior"]}])
        historico = pd.concat([historico, anterior], ignore_index=True)
    tablas["historico"] = historico
    tablero = integrar_tablas(tablas, eventos, semana)
    tablero["ocupacion_base"] = tablero["ocupacion_anterior"]
    tablero.loc[tablero["clave"].eq("buenos aires"), "ocupacion_base"] = referencia["actual"]
    datos_eoh = historico.loc[historico["clave"].ne("buenos aires")]
    penultimo = datos_eoh.sort_values("fecha").groupby("clave").nth(-2).set_index("clave")["ocupacion"]
    otras_filas = tablero["clave"].ne("buenos aires")
    tablero.loc[otras_filas, "ocupacion_anterior"] = tablero.loc[otras_filas, "clave"].map(penultimo)
    return tablero
