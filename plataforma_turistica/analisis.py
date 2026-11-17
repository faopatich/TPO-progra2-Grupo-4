"""Clima, indicadores y recomendaciones para cada destino (N02-N04)."""
import pandas as pd
from .clima import consultar_clima, ErrorClima
from .geocodificacion import geocodificar_destino, ErrorGeocodificacion
from .config import PALABRAS_CLAVE
from .ocupacion import FUENTE_AIRBNB, CAPTURA_AIRBNB, FUENTE_EOH
from .indicadores import calcular_ocupacion_estimada, calcular_variacion_demanda, contar_menciones, calcular_prioridad_comercial
from .clasificacion import clasificar_destino, recomendar_accion
from .etl import resumir_reputacion
from .datos import RAIZ
from .reputacion import analizar_resenas_airbnb


def analizar_destinos(tablero, tablas, eventos, cobertura, fuentes, semana,
                      usar_red, proveedor):
    """Calcula el resultado de cada fila y registra sus fuentes y avisos."""
    reputacion = resumir_reputacion(tablas["comentarios"])
    resumen_airbnb = None
    error_resenas = None
    ruta_resenas = RAIZ / "datos" / "inside_airbnb" / "reviews.csv.gz"
    if tablero["clave"].eq("buenos aires").any():
        if ruta_resenas.is_file():
            try:
                resumen_airbnb = analizar_resenas_airbnb(ruta_resenas, CAPTURA_AIRBNB)
            except ValueError as error:
                error_resenas = str(error)
        else:
            error_resenas = "No se encontró el archivo local de reseñas de CABA."
    filas = []
    for _, destino in tablero.iterrows():
        clave = destino["clave"]
        avisos = []
        temperatura = None
        lluvia = None
        fuente_clima = "sin datos"
        if not usar_red:
            avisos.append("Clima no consultado: active el modo en vivo.")
        elif clave == "provincia de buenos aires":
            avisos.append("No se asigna el clima de una sola ciudad a toda la provincia.")
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
        comentarios = tablas["comentarios"].loc[tablas["comentarios"]["clave"].eq(clave), "comentario"].tolist()
        titulos_eventos = eventos.loc[eventos["clave"].eq(clave), "titulo"].tolist()
        menciones = contar_menciones(titulos_eventos, PALABRAS_CLAVE)
        opinion = reputacion.get(clave, {"positivas": 0, "negativas": 0, "neutras": 0})
        sin_opinion = clave not in reputacion
        if clave == "buenos aires" and resumen_airbnb and resumen_airbnb["total"]:
            opinion = resumen_airbnb
            sin_opinion = False
            avisos.append("Reseñas Airbnb: clasificación básica por palabras; neutras incluye opiniones mixtas y no clasificadas.")
            if resumen_airbnb["posteriores"]:
                avisos.append(f"Se excluyeron {resumen_airbnb['posteriores']} reseñas posteriores a la fecha nominal de captura.")
        elif sin_opinion:
            opinion = {"positivas": 0, "negativas": 0, "neutras": 0}
            avisos.append(error_resenas if clave == "buenos aires" and error_resenas else "Reputación no disponible: no hay comentarios de una fuente real.")
        ocupacion = variacion = prioridad = None
        clasificacion = "datos insuficientes"
        recomendacion = "Completar fuentes del destino antes de recomendar acciones."
        if pd.notna(destino["ocupacion_base"]) and lluvia is not None and cobertura.get(clave, False):
            ocupacion = calcular_ocupacion_estimada(
                destino["ocupacion_base"], int(destino["eventos"]), lluvia,
            )
            anterior = destino["ocupacion_anterior"]
            if pd.notna(anterior) and anterior > 0:
                # La variación compara referencias equivalentes, sin el ajuste académico.
                actual_comparable = destino["ocupacion_base"]
                variacion = calcular_variacion_demanda(actual_comparable, anterior)
                prioridad = calcular_prioridad_comercial(ocupacion, variacion, menciones)
                clasificacion = clasificar_destino(ocupacion, variacion, menciones, lluvia)
                recomendacion = recomendar_accion(clasificacion)
            else:
                avisos.append("Sin ocupación histórica anterior mayor que cero para comparar.")
        else:
            avisos.append("Faltan base de ocupación, clima o cobertura de eventos del destino.")
        fila = destino.to_dict()
        if clave == "buenos aires":
            fila["fuente_ocupacion"] = FUENTE_AIRBNB
            fila["periodo_ocupacion"] = semana.strftime("%Y-%m-%d") + " a " + (semana + pd.Timedelta(days=6)).strftime("%Y-%m-%d")
            fila["captura_ocupacion"] = CAPTURA_AIRBNB.strftime("%Y-%m-%d")
            avisos.append("Inside Airbnb: noches no disponibles pueden estar bloqueadas o reservadas; captura 2026-09-23, no es ocupación medida.")
            avisos.append("Variación compara no disponibilidad de dos semanas de la misma captura; no mide reservas reales.")
            if pd.isna(destino["ocupacion_base"]):
                avisos.append("Sin calendario Airbnb válido para la semana.")
        else:
            fila["fuente_ocupacion"] = FUENTE_EOH if pd.notna(destino["ocupacion_base"]) else "sin datos EOH"
            fila["periodo_ocupacion"] = destino["fecha_anterior"].strftime("%Y-%m") if pd.notna(destino["fecha_anterior"]) else "sin datos"
            fila["captura_ocupacion"] = None
            if pd.isna(destino["ocupacion_base"]):
                avisos.append("Sin tasa EOH para este destino y período; consulte cobertura y anexo local.")
            else:
                avisos.append("EOH INDEC: tasa mensual histórica de habitaciones; no es ocupación actual. La variación compara dos meses históricos EOH; no mide demanda actual.")
        fila.update(
            fecha=semana, temperatura=temperatura, lluvia=lluvia, ocupacion=ocupacion,
            variacion=variacion, menciones=menciones, prioridad=prioridad,
            positivas=opinion["positivas"], negativas=opinion["negativas"],
            clasificacion=clasificacion, recomendacion=recomendacion,
            fuente_clima=fuente_clima, fuente_eventos=fuentes.get(clave, "sin datos"),
            fuente_datos="archivos del usuario" if not tablas["comentarios"].empty else "fuentes públicas",
            advertencias="; ".join(avisos),
        )
        if clave == "buenos aires" and resumen_airbnb and resumen_airbnb["total"]:
            fila["neutras"] = resumen_airbnb["neutras"]
            fila["total_resenas"] = resumen_airbnb["total"]
            fila["menciones_resenas"] = resumen_airbnb["menciones"]
            fila["fuente_reputacion"] = FUENTE_AIRBNB
            fila["periodo_reputacion"] = f"{resumen_airbnb['desde']:%Y-%m-%d} a {resumen_airbnb['hasta']:%Y-%m-%d}"
        elif sin_opinion:
            fila["positivas"] = None
            fila["negativas"] = None
            fila["neutras"] = None
            fila["total_resenas"] = None
            fila["menciones_resenas"] = None
            fila["fuente_reputacion"] = "sin datos"
            fila["periodo_reputacion"] = "sin datos"
        else:
            fila["neutras"] = opinion["neutras"]
            fila["total_resenas"] = sum(opinion.values())
            fila["menciones_resenas"] = contar_menciones(comentarios, PALABRAS_CLAVE)
            fila["fuente_reputacion"] = "archivos del usuario"
            fila["periodo_reputacion"] = "no especificado"
        filas.append(fila)
    tablero = pd.DataFrame(filas)
    for columna in ["temperatura", "lluvia", "ocupacion", "variacion", "prioridad"]:
        tablero[columna] = pd.to_numeric(tablero[columna], errors="coerce")
    tablero["fecha"] = pd.to_datetime(tablero["fecha"])
    return tablero
