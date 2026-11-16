"""Coordina módulos; main y FastAPI reutilizan el mismo análisis."""
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import requests

from .clima import consultar_clima, ErrorClima
from .config import FUENTES_EVENTOS, PALABRAS_CLAVE
from .datos import RAIZ, cargar_archivos, preparar_demo
from .destinos import obtener_destino
from .eventos import descargar_html, extraer_eventos, ScrapingNoPermitido
from .geocodificacion import geocodificar_destino, ErrorGeocodificacion
from .indicadores import calcular_ocupacion_estimada, calcular_variacion_demanda, contar_menciones, calcular_prioridad_comercial
from .clasificacion import clasificar_destino, recomendar_accion
from .normalizacion import normalizar_texto
from .etl import limpiar_tablas, limpiar_eventos, integrar_tablas, resumir_reputacion, combinar_historico, eventos_a_registros


def inicio_semana(fecha=None) -> pd.Timestamp:
    """Agrupa por semana de lunes a domingo."""
    dia = pd.Timestamp(fecha if fecha is not None else pd.Timestamp.today()).normalize()
    if pd.isna(dia):
        raise ValueError("La fecha no es válida")
    return dia - pd.Timedelta(days=dia.dayofweek)


def construir_tablero(nombres=None, usar_red=False, fecha=None, carpeta_datos=None,
                      carpeta_demo=None, proveedor="open-meteo") -> dict:
    """Extrae fuentes, limpia datos y calcula una fila por destino.

    En vivo no reemplaza clima ni eventos fallidos por valores inventados.
    El catálogo, hoteles, comentarios e histórico demo se identifican como tales.
    """
    semana = inicio_semana(fecha)
    if usar_red and semana != inicio_semana():
        raise ValueError("El clima en vivo es actual: use la semana actual o modo demo.")
    demo = carpeta_datos is None
    if demo:
        carpeta = preparar_demo(Path(carpeta_demo or RAIZ / "salida" / "entradas_demo"), semana)
    else:
        carpeta = Path(carpeta_datos)
    tablas = limpiar_tablas(cargar_archivos(carpeta))
    catalogo = tablas["destinos"]
    if nombres:
        claves = [normalizar_texto(nombre) for nombre in nombres]
        for nombre, clave in zip(nombres, claves):
            if not clave:
                raise ValueError("El destino no puede estar vacío")
            if clave not in catalogo["clave"].values:
                destino = obtener_destino(nombre)
                coordenadas = destino["coordenadas"] or {}
                extra = pd.DataFrame([{
                    "clave": clave, "destino": destino["nombre"], "zona": destino["zona"],
                    "latitud": coordenadas.get("latitud"), "longitud": coordenadas.get("longitud"),
                    "ocupacion_base": None,
                }])
                catalogo = pd.concat([catalogo, extra], ignore_index=True)
        catalogo = catalogo.loc[catalogo["clave"].isin(claves)].copy()
    if catalogo.empty:
        raise ValueError("No hay destinos válidos para analizar")
    tablas["destinos"] = catalogo
    advertencias = []
    registros = []
    cobertura = {}
    fuentes = {}
    if not usar_red:
        html = (carpeta / "eventos.html").read_text(encoding="utf-8")
        fuente = "demo" if demo else "archivo del usuario"
        # El HTML local usa data-destino; no se asigna una agenda a todas las ciudades.
        eventos = extraer_eventos(html, "https://example.org/", destino_base="", fuente=fuente)
        registros = eventos_a_registros(eventos)
        claves_archivo = {normalizar_texto(evento.destino) for evento in eventos}
        for clave in catalogo["clave"]:
            cobertura[clave] = clave in claves_archivo
            fuentes[clave] = fuente if cobertura[clave] else "sin datos"
    else:
        for _, destino in catalogo.iterrows():
            clave = destino["clave"]
            cobertura[clave] = False
            fuentes[clave] = "sin datos"
            url = FUENTES_EVENTOS.get(clave)
            if not url:
                advertencias.append(f"{destino['destino']}: no hay fuente web de eventos configurada.")
            else:
                try:
                    html = descargar_html(url)
                    eventos = extraer_eventos(html, url, destino["destino"], "web")
                    if not eventos:
                        raise ValueError("La página no contiene tarjetas reconocidas; revisar selectores HTML.")
                    registros.extend(eventos_a_registros(eventos))
                    cobertura[clave] = True
                    fuentes[clave] = url
                except (requests.RequestException, ScrapingNoPermitido, ValueError) as error:
                    # No incluir URLs con credenciales en los avisos.
                    advertencias.append(f"{destino['destino']}: agenda no disponible ({type(error).__name__}).")
    # Un cambio de HTML que deje todas las fechas sin interpretar no equivale a cero eventos.
    for clave in catalogo["clave"]:
        propios = [registro for registro in registros if normalizar_texto(registro["destino"]) == clave]
        fechas = pd.to_datetime([registro["fecha"] for registro in propios], errors="coerce")
        if propios and fechas.isna().all():
            cobertura[clave] = False
            advertencias.append(f"{clave}: no se pudieron interpretar las fechas; revisar HTML.")
    eventos = limpiar_eventos(registros, semana)
    if registros and len(eventos) < len(registros):
        advertencias.append("Se excluyeron eventos duplicados, sin fecha ISO válida o fuera de la semana.")
    tablero = integrar_tablas(tablas, eventos, semana)
    reputacion = resumir_reputacion(tablas["comentarios"])
    filas = []
    for _, destino in tablero.iterrows():
        clave = destino["clave"]
        avisos = []
        temperatura = None
        lluvia = None
        fuente_clima = "sin datos"
        if not usar_red:
            temperatura, lluvia, fuente_clima = 20.0, 20.0, "demo"
        else:
            try:
                latitud, longitud = destino["latitud"], destino["longitud"]
                if pd.isna(latitud) or pd.isna(longitud):
                    coordenadas = geocodificar_destino(destino["destino"])
                    latitud, longitud = coordenadas.latitud, coordenadas.longitud
                if proveedor == "openweathermap":
                    from .practica_api import consultar_clima_autenticado
                    clima = consultar_clima_autenticado(latitud, longitud)
                else:
                    clima = consultar_clima(latitud, longitud)
                temperatura, lluvia, fuente_clima = clima.temperatura, clima.probabilidad_lluvia, clima.fuente
            except (ErrorClima, ErrorGeocodificacion) as error:
                avisos.append(str(error))
        textos = tablas["comentarios"].loc[tablas["comentarios"]["clave"].eq(clave), "comentario"].tolist()
        textos += eventos.loc[eventos["clave"].eq(clave), "titulo"].tolist()
        menciones = contar_menciones(textos, PALABRAS_CLAVE)
        opinion = reputacion.get(clave, {"positivas": 0, "negativas": 0, "neutras": 0})
        ocupacion = variacion = prioridad = None
        clasificacion = "datos insuficientes"
        recomendacion = "Completar fuentes del destino antes de recomendar acciones."
        if pd.notna(destino["ocupacion_base"]) and lluvia is not None and cobertura.get(clave, False):
            ocupacion = calcular_ocupacion_estimada(
                destino["ocupacion_base"], int(destino["eventos"]),
                opinion["positivas"], opinion["negativas"], lluvia,
            )
            anterior = destino["ocupacion_anterior"]
            if pd.notna(anterior) and anterior > 0:
                variacion = calcular_variacion_demanda(ocupacion, anterior)
                prioridad = calcular_prioridad_comercial(ocupacion, variacion, menciones)
                clasificacion = clasificar_destino(ocupacion, variacion, menciones, lluvia)
                recomendacion = recomendar_accion(clasificacion)
            else:
                avisos.append("Sin ocupación histórica anterior mayor que cero para comparar.")
        else:
            avisos.append("Faltan base de ocupación, clima o cobertura de eventos del destino.")
        fila = destino.to_dict()
        fila.update(
            fecha=semana, temperatura=temperatura, lluvia=lluvia, ocupacion=ocupacion,
            variacion=variacion, menciones=menciones, prioridad=prioridad,
            positivas=opinion["positivas"], negativas=opinion["negativas"],
            clasificacion=clasificacion, recomendacion=recomendacion,
            fuente_clima=fuente_clima, fuente_eventos=fuentes.get(clave, "sin datos"),
            fuente_datos="demo académico" if demo else "archivos del usuario",
            advertencias="; ".join(avisos),
        )
        filas.append(fila)
    tablero = pd.DataFrame(filas)
    for columna in ["temperatura", "lluvia", "ocupacion", "variacion", "prioridad"]:
        tablero[columna] = pd.to_numeric(tablero[columna], errors="coerce")
    tablero["fecha"] = pd.to_datetime(tablero["fecha"])
    historico = tablas["historico"].loc[tablas["historico"]["clave"].isin(tablero["clave"])]
    return {"tablero": tablero, "eventos": eventos,
            "historico": combinar_historico(historico, tablero), "advertencias": advertencias}


@dataclass
class ResultadoAnalisis:
    destino: str
    eventos: int
    temperatura: float | None
    lluvia: float | None
    ocupacion: float | None
    variacion: float | None
    menciones: int
    prioridad: float | None
    clasificacion: str
    recomendacion: str
    advertencias: tuple[str, ...] = ()
    fuente_clima: str = ""
    fuente_eventos: str = ""
    fuente_datos: str = ""

    def como_texto(self) -> str:
        return (f"{self.destino}: {self.clasificacion}\n"
                f"Ocupación estimada: {self.ocupacion} | variación: {self.variacion}\n"
                f"Recomendación: {self.recomendacion}\n"
                f"Fuentes: {self.fuente_clima}; {self.fuente_eventos}; {self.fuente_datos}\n"
                + "\n".join(self.advertencias))


def ejecutar_analisis(nombre_destino: str, usar_red: bool = False) -> ResultadoAnalisis:
    """Mantiene el contrato usado por GET y POST; no envía correos desde la API."""
    datos = construir_tablero([nombre_destino], usar_red=usar_red)
    fila = datos["tablero"].iloc[0]
    valores = {}
    for campo in ["destino", "eventos", "temperatura", "lluvia", "ocupacion",
                  "variacion", "menciones", "prioridad", "clasificacion", "recomendacion",
                  "fuente_clima", "fuente_eventos", "fuente_datos"]:
        valor = fila[campo]
        valores[campo] = None if pd.isna(valor) else valor
    avisos = datos["advertencias"] + ([fila["advertencias"]] if fila["advertencias"] else [])
    return ResultadoAnalisis(**valores, advertencias=tuple(avisos))
