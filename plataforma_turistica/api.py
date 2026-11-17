"""Capa HTTP de FastAPI para consumir la plataforma desde Postman."""

from __future__ import annotations

from dataclasses import asdict
import os

from fastapi import FastAPI, HTTPException, Query
from dotenv import load_dotenv

from .destinos import listar_destinos
from .esquemas import (
    RespuestaAnalisis,
    RespuestaDestinos,
    RespuestaSalud,
    SolicitudAnalisis,
)
from .servicio import construir_tablero, ejecutar_analisis, crear_carpeta_salida
from .datos import RAIZ
from .etl import exportar_resultados
from .visualizacion import generar_graficos
from .boletines import crear_boletin, enviar_boletin

# FastAPI crea la aplicación ASGI y genera documentación OpenAPI automáticamente.
app = FastAPI(
    title="API de Analítica Turística",
    description="Plataforma académica modular con ETL, exportaciones y boletín semanal.",
    version="1.0.0",
)


def _analizar_o_responder_error(destino: str, en_vivo: bool, enviar_correo: bool = False) -> RespuestaAnalisis:
    """Ejecuta el servicio y traduce errores a respuestas HTTP.

    La función evita repetir el mismo bloque try/except en los endpoints GET y
    POST. ``asdict`` transforma la dataclass del servicio en un diccionario.
    """
    try:
        datos_analisis = construir_tablero([destino], usar_red=en_vivo)
        resultado = ejecutar_analisis(destino, usar_red=en_vivo, datos=datos_analisis)
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    datos = asdict(resultado)
    # El contrato declara una lista; el servicio utiliza una tupla inmutable.
    datos["advertencias"] = list(resultado.advertencias)
    if enviar_correo:
        load_dotenv(RAIZ / ".env")
        remitente = os.getenv("EMAIL_USER", "").strip()
        destinatarios = [direccion.strip() for direccion in os.getenv("EMAIL_RECEIVER", "").split(",") if direccion.strip()]
        try:
            carpeta = crear_carpeta_salida(RAIZ / "salida", datos_analisis["tablero"]["fecha"].iloc[0])
            archivos = exportar_resultados(datos_analisis["tablero"], datos_analisis["eventos"], datos_analisis["historico"], carpeta)
            graficos = generar_graficos(datos_analisis["tablero"], datos_analisis["historico"], carpeta)
            mensaje = crear_boletin(datos_analisis["tablero"], archivos + graficos,
                                    datos_analisis["advertencias"], remitente, destinatarios)
            enviar_boletin(mensaje)
        except (ValueError, OSError) as error:
            raise HTTPException(status_code=502, detail=f"No se pudo enviar el boletín: {error}") from error
        datos["correo_enviado"] = True
    return RespuestaAnalisis(**datos)


@app.get("/", response_model=RespuestaSalud, tags=["Sistema"])
def inicio() -> RespuestaSalud:
    """Devuelve información básica y confirma que la API responde."""
    return RespuestaSalud(
        estado="ok",
        servicio="API de Analítica Turística",
        version="1.0.0",
    )


@app.get("/destinos", response_model=RespuestaDestinos, tags=["Destinos"])
def obtener_destinos() -> RespuestaDestinos:
    """Lista los destinos que pueden utilizarse en un análisis."""
    destinos = listar_destinos()
    return RespuestaDestinos(cantidad=len(destinos), destinos=destinos)


@app.get("/analisis/{destino}", response_model=RespuestaAnalisis, tags=["Análisis"])
def analizar_destino_get(
    destino: str,
    en_vivo: bool = Query(
        default=True,
        description="Intenta consultar Open-Meteo y la agenda oficial.",
    ),
) -> RespuestaAnalisis:
    """Analiza el destino recibido en la URL mediante una solicitud GET."""
    return _analizar_o_responder_error(destino, en_vivo)


@app.post("/analisis", response_model=RespuestaAnalisis, tags=["Análisis"])
def analizar_destino_post(solicitud: SolicitudAnalisis) -> RespuestaAnalisis:
    """Analiza los datos enviados como cuerpo JSON mediante POST."""
    return _analizar_o_responder_error(solicitud.destino, solicitud.en_vivo, solicitud.enviar_correo)
