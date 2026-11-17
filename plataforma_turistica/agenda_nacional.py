"""Agenda nacional de fiestas y eventos publicada por Turismo (N10-N12)."""
from io import BytesIO
import pandas as pd
import requests
from .normalizacion import normalizar_texto

PAGINA_AGENDA = "https://www.argentina.gob.ar/jefatura/turismo-y-ambiente/turismo/fiestas-y-eventos-de-argentina"
CSV_AGENDA = "https://docs.google.com/spreadsheets/d/112JJ2hVe_lQ8xse7J8XB7TYuucBY7Rf6gQLxXYxoBL8/gviz/tq?tqx=out:csv"


def descargar_agenda_nacional(session=None):
    """Descarga una vez la planilla pública que alimenta la página nacional."""
    cliente = session or requests.Session()
    respuesta = cliente.get(CSV_AGENDA, timeout=20, headers={"User-Agent": "TPO-Turismo-Educativo/1.0"})
    respuesta.raise_for_status()
    try:
        datos = pd.read_csv(BytesIO(respuesta.content), dtype=str).fillna("")
    except (ValueError, pd.errors.ParserError, UnicodeError) as error:
        raise ValueError("No se pudo leer la agenda nacional") from error
    necesarias = {"inicio", "hasta", "titulo", "Ubicación", "Unnamed: 5", "Publicada"}
    if not necesarias.issubset(datos.columns):
        raise ValueError("La agenda nacional cambió de formato")
    datos = datos.loc[datos["Publicada"].str.strip().str.upper().eq("SI")].copy()
    datos["fecha_inicio"] = pd.to_datetime(datos["inicio"], format="%d/%m/%Y", errors="coerce")
    datos["fecha_fin"] = pd.to_datetime(datos["hasta"], format="%d/%m/%Y", errors="coerce")
    datos = datos.loc[datos["fecha_inicio"].notna() & datos["fecha_fin"].notna()
                      & datos["fecha_fin"].ge(datos["fecha_inicio"]) & datos["titulo"].str.strip().ne("")].copy()
    datos["provincia_clave"] = datos["Ubicación"].apply(normalizar_texto)
    datos["localidad_clave"] = datos["Unnamed: 5"].apply(normalizar_texto)
    return datos


def seleccionar_eventos_nacionales(datos, destino, semana):
    """Busca coincidencias geográficas exactas y eventos activos durante la semana."""
    clave = normalizar_texto(destino)
    if clave.startswith("provincia de "):
        propios = datos.loc[datos["provincia_clave"].eq(clave.removeprefix("provincia de "))]
    else:
        localidad = clave.removeprefix("ciudad de ")
        propios = datos.loc[datos["localidad_clave"].eq(localidad)]
        # Un nombre repetido en distintas provincias no identifica una ciudad.
        provincias = propios["provincia_clave"].dropna().unique()
        if len(provincias) > 1:
            return [], False
    if propios.empty:
        return [], False
    fin = semana + pd.Timedelta(days=7)
    actuales = propios.loc[propios["fecha_inicio"].lt(fin) & propios["fecha_fin"].ge(semana)]
    registros = []
    for _, fila in actuales.iterrows():
        registros.append({"destino": destino, "titulo": fila["titulo"].strip(),
                          "fecha": fila["fecha_inicio"], "fecha_fin": fila["fecha_fin"],
                          "direccion": fila["Unnamed: 5"], "enlace": fila.get("url") or PAGINA_AGENDA,
                          "imagen": fila.get("imagen") or None, "fuente": PAGINA_AGENDA})
    return registros, True
