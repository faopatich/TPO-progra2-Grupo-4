"""Capa HTTP de FastAPI para consumir la plataforma desde Postman."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI, HTTPException, Query

from .destinos import listar_destinos
from .esquemas import (
    RespuestaAnalisis,
    RespuestaDestinos,
    RespuestaSalud,
    SolicitudAnalisis,
)
from .servicio import ejecutar_analisis

# FastAPI crea la aplicación ASGI y genera documentación OpenAPI automáticamente.
app = FastAPI(
    title="API de Analítica Turística",
    description="Plataforma académica modular implementada hasta N13.",
    version="1.0.0",
)


def _analizar_o_responder_error(destino: str, en_vivo: bool) -> RespuestaAnalisis:
    """Ejecuta el servicio y traduce errores de dominio a respuestas HTTP 404.

    La función evita repetir el mismo bloque try/except en los endpoints GET y
    POST. ``asdict`` transforma la dataclass del servicio en un diccionario.
    """
    try:
        resultado = ejecutar_analisis(destino, usar_red=en_vivo)
    except ValueError as error:
        # HTTPException hace que FastAPI responda JSON con status code 404.
        raise HTTPException(status_code=404, detail=str(error)) from error

    datos = asdict(resultado)
    # El contrato declara una lista; el servicio utiliza una tupla inmutable.
    datos["advertencias"] = list(resultado.advertencias)
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
        default=False,
        description="Intenta consultar Open-Meteo y la agenda oficial.",
    ),
) -> RespuestaAnalisis:
    """Analiza el destino recibido en la URL mediante una solicitud GET."""
    return _analizar_o_responder_error(destino, en_vivo)


@app.post("/analisis", response_model=RespuestaAnalisis, tags=["Análisis"])
def analizar_destino_post(solicitud: SolicitudAnalisis) -> RespuestaAnalisis:
    """Analiza los datos enviados como cuerpo JSON mediante POST."""
    return _analizar_o_responder_error(solicitud.destino, solicitud.en_vivo)
