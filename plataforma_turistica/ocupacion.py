"""Referencias mensuales de ocupación hotelera de fuentes oficiales."""
from pathlib import Path
import pandas as pd
from .normalizacion import normalizar_texto


FUENTE_AIRBNB = "https://insideairbnb.com/get-the-data/"
CAPTURA_AIRBNB = pd.Timestamp("2026-09-23")


def calcular_referencia_airbnb(ruta: Path, semana: pd.Timestamp) -> dict:
    """Compara semanas usando una captura local, contando noches no disponibles.

    Procesa el CSV comprimido en bloques para no cargar todo el calendario en memoria.
    Una noche no disponible puede estar reservada o bloqueada por el anfitrión.
    """
    if semana < CAPTURA_AIRBNB:
        raise ValueError("La semana no puede ser anterior a la captura de Inside Airbnb")
    if not ruta.is_file():
        raise FileNotFoundError(f"Falta el calendario de Inside Airbnb: {ruta}. Ver README para descargarlo.")
    inicio = semana - pd.Timedelta(days=7)
    fin = semana + pd.Timedelta(days=7)
    resultados = {"actual": [0, 0, set()], "anterior": [0, 0, set()]}
    try:
        for bloque in pd.read_csv(ruta, compression="gzip", usecols=["date", "available"],
                                  chunksize=500000, dtype=str):
            fechas = pd.to_datetime(bloque["date"], errors="coerce")
            estado = bloque["available"].str.lower().str.strip()
            validas = fechas.ge(inicio) & fechas.lt(fin) & estado.isin(["t", "f"])
            for nombre, comienzo in (("anterior", inicio), ("actual", semana)):
                mascara = validas & fechas.ge(comienzo) & fechas.lt(comienzo + pd.Timedelta(days=7))
                seleccion = estado[mascara]
                resultados[nombre][0] += int(seleccion.eq("f").sum())
                resultados[nombre][1] += int(len(seleccion))
                resultados[nombre][2].update(fechas[mascara].dt.strftime("%Y-%m-%d").unique())
    except (OSError, ValueError, KeyError) as error:
        raise ValueError("No se pudo leer el calendario de Inside Airbnb: revise el archivo y sus columnas") from error
    salida = {}
    for nombre, (no_disponibles, total, fechas) in resultados.items():
        salida[nombre] = round(100 * no_disponibles / total, 2) if total and len(fechas) == 7 else None
        salida[nombre + "_registros"] = total
    return salida


FUENTE_EOH = "https://www.indec.gob.ar/ftp/cuadros/economia/EOH_cuadros_dic25.zip"


def cargar_eoh_localidades(ruta: Path, catalogo: pd.DataFrame, semana: pd.Timestamp) -> pd.DataFrame:
    """Lee el anexo del INDEC y calcula la tasa mensual por ciudad relevada."""
    import io
    import zipfile
    columnas = ["clave", "destino", "fecha", "ocupacion"]
    if not ruta.is_file():
        return pd.DataFrame(columns=columnas).astype({"fecha": "datetime64[ns]"})
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
             "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    # Nombre habitual o región explícita: sin asignar una localidad a otra.
    alias = {"provincia de buenos aires": "reg_ba", "cordoba": "cordoba",
             "bariloche": "bariloche", "villa carlos paz": "carlos paz",
             "villa gesell": "gesell", "puerto iguazu": "iguazu",
             "puerto madryn": "madryn", "el calafate": "calafate",
             "villa la angostura": "angostura", "san martin de los andes": "san martin de las andes",
             "san miguel de tucuman": "tucuman", "ciudad de mendoza": "mendoza"}
    try:
        with zipfile.ZipFile(ruta) as archivo:
            contenido = archivo.read("eoh_dic25_oyd_cuadros.xls")
        libro = pd.ExcelFile(io.BytesIO(contenido))
        hojas = {normalizar_texto(nombre): nombre for nombre in libro.sheet_names}
        registros = []
        for _, destino in catalogo.iterrows():
            clave = destino["clave"]
            if clave == "buenos aires":
                continue
            nombre_hoja = hojas.get(alias.get(clave, clave))
            if nombre_hoja is None:
                continue
            tabla = pd.read_excel(libro, sheet_name=nombre_hoja, header=None)
            etiquetas = tabla[0].fillna("").astype(str)
            disponibles = tabla.index[etiquetas.str.startswith("Habitaciones o unidades disponibles")]
            ocupadas = tabla.index[etiquetas.str.startswith("Habitaciones o unidades ocupadas")]
            if len(disponibles) != 1 or len(ocupadas) != 1:
                continue
            for columna in range(4, tabla.shape[1], 2):
                mes = normalizar_texto(str(tabla.iat[4, columna]))
                if mes not in meses:
                    continue
                fecha = pd.Timestamp(2025, meses.index(mes) + 1, 1)
                if fecha + pd.offsets.MonthEnd(0) >= semana:
                    continue
                total = pd.to_numeric(tabla.iat[disponibles[0] + 1, columna], errors="coerce")
                ocupadas_total = pd.to_numeric(tabla.iat[ocupadas[0] + 1, columna], errors="coerce")
                if pd.notna(total) and total > 0 and pd.notna(ocupadas_total) and 0 <= ocupadas_total <= total:
                    registros.append({"clave": clave, "destino": destino["destino"],
                                      "fecha": fecha, "ocupacion": round(100 * ocupadas_total / total, 1)})
        resultado = pd.DataFrame(registros, columns=columnas)
        resultado["fecha"] = pd.to_datetime(resultado["fecha"])
        return resultado
    except (OSError, KeyError, ValueError, zipfile.BadZipFile) as error:
        raise ValueError("No se pudo leer el anexo EOH del INDEC; revise el ZIP oficial") from error
