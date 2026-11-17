"""Coordina el análisis turístico y reúne los resultados."""
from pathlib import Path
from datetime import datetime
import pandas as pd

from .datos import cargar_archivos, cargar_fuentes_reales
from .destinos import seleccionar_destinos
from .etl import limpiar_tablas, combinar_historico
from .agenda_servicio import preparar_agenda
from .referencias import integrar_referencias
from .analisis import analizar_destinos
from .resultado import ResultadoAnalisis


def crear_carpeta_salida(raiz: Path, semana) -> Path:
    """Separa cada ejecución para conservar reportes y gráficos anteriores."""
    carpeta_semana = raiz / semana.strftime("%Y-%m-%d")
    carpeta_semana.mkdir(parents=True, exist_ok=True)
    while True:
        carpeta = carpeta_semana / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        try:
            carpeta.mkdir()
            return carpeta
        except FileExistsError:
            continue


def inicio_semana(fecha=None) -> pd.Timestamp:
    """Devuelve el lunes correspondiente a la fecha elegida."""
    dia = pd.Timestamp(fecha if fecha is not None else pd.Timestamp.today()).normalize()
    if pd.isna(dia):
        raise ValueError("La fecha no es válida")
    return dia - pd.Timedelta(days=dia.dayofweek)


def construir_tablero(nombres=None, usar_red=False, fecha=None, carpeta_datos=None,
                      proveedor="open-meteo") -> dict:
    """Coordina entradas, eventos, referencias e indicadores por destino."""
    semana = inicio_semana(fecha)
    if usar_red and semana != inicio_semana():
        raise ValueError("El clima en vivo es actual: use la semana actual o --sin-red.")
    carpeta = Path(carpeta_datos) if carpeta_datos else None
    tablas = limpiar_tablas(cargar_archivos(carpeta) if carpeta else cargar_fuentes_reales())
    tablas["destinos"] = seleccionar_destinos(tablas, nombres)
    eventos, cobertura, fuentes, advertencias = preparar_agenda(
        tablas["destinos"], carpeta, usar_red, semana)
    tablero = integrar_referencias(tablas, eventos, semana)
    tablero = analizar_destinos(tablero, tablas, eventos, cobertura, fuentes, semana,
                               usar_red, proveedor)
    tablero = tablero.drop(columns=["hoteles", "habitaciones"], errors="ignore")
    tablero.loc[~tablero["clave"].map(cobertura).fillna(False), "eventos"] = None
    historico = tablas["historico"].loc[tablas["historico"]["clave"].isin(tablero["clave"])]
    return {"tablero": tablero, "eventos": eventos,
            "historico": combinar_historico(historico, tablero), "advertencias": advertencias}


def ejecutar_analisis(nombre_destino: str, usar_red: bool = False, datos=None) -> ResultadoAnalisis:
    """Convierte el tablero al formato de la API, reutilizando el análisis si existe."""
    if datos is None:
        datos = construir_tablero([nombre_destino], usar_red=usar_red)
    fila = datos["tablero"].iloc[0]
    valores = {}
    for campo in ["destino", "eventos", "temperatura", "lluvia", "ocupacion",
                  "variacion", "menciones", "prioridad", "clasificacion", "recomendacion",
                  "fuente_clima", "fuente_eventos", "fuente_datos", "fuente_ocupacion", "periodo_ocupacion",
                  "positivas", "negativas", "neutras", "total_resenas", "menciones_resenas",
                  "fuente_reputacion", "periodo_reputacion"]:
        valor = fila[campo]
        valores[campo] = None if pd.isna(valor) else valor
    avisos = datos["advertencias"] + ([fila["advertencias"]] if fila["advertencias"] else [])
    return ResultadoAnalisis(**valores, advertencias=tuple(avisos))
