"""Cliente de la API pública Open-Meteo (N04 y N13)."""

from __future__ import annotations

from dataclasses import dataclass

import requests

from .config import ENDPOINTS_API


class ErrorClima(RuntimeError):
    """Representa una falla controlada de red, HTTP o formato meteorológico."""


@dataclass(frozen=True)
class Clima:
    """Agrupa los valores meteorológicos que necesita el análisis.

    ``frozen=True`` evita cambios accidentales después de crear el objeto.
    """

    temperatura: float
    probabilidad_lluvia: float
    codigo: int
    fuente: str = "Open-Meteo"


def consultar_clima(
    latitud: float,
    longitud: float,
    session: requests.Session | None = None,
    timeout: int = 10,
) -> Clima:
    """Consulta el pronóstico diario de Open-Meteo mediante HTTP GET.

    Args:
        latitud: Coordenada geográfica norte/sur.
        longitud: Coordenada geográfica este/oeste.
        session: Cliente HTTP opcional; permite reutilizar conexiones o probar.
        timeout: Máximo de segundos de espera para la respuesta.
    Returns:
        Un objeto ``Clima`` con temperatura, lluvia y código meteorológico.
    Raises:
        ErrorClima: Ante fallas de red, estados HTTP de error o JSON incompleto.
    """
    # Si una prueba no inyecta una sesión falsa, se crea un cliente HTTP real.
    cliente = session or requests.Session()

    # requests codifica este diccionario como parámetros de la URL. Solo se pide
    # un día y las variables utilizadas para evitar transferir datos innecesarios.
    parametros = {
        "latitude": latitud,
        "longitude": longitud,
        "current": "temperature_2m,weather_code",
        "daily": "precipitation_probability_max",
        "forecast_days": 1,
        "timezone": "auto",
    }
    try:
        # GET consulta información sin modificar el recurso del servidor.
        respuesta = cliente.get(
            ENDPOINTS_API["clima_publica"], params=parametros, timeout=timeout
        )

        # Convierte respuestas 4xx/5xx en excepciones antes de interpretar datos.
        respuesta.raise_for_status()

        # .json() transforma el cuerpo JSON en diccionarios y listas de Python.
        datos = respuesta.json()
        actual = datos["current"]
        probabilidades = datos["daily"]["precipitation_probability_max"]

        # Las conversiones garantizan tipos numéricos consistentes.
        return Clima(
            temperatura=float(actual["temperature_2m"]),
            probabilidad_lluvia=float(probabilidades[0] or 0),
            codigo=int(actual["weather_code"]),
        )
    except (requests.RequestException, KeyError, TypeError, ValueError, IndexError) as error:
        # Se unifican errores técnicos para que servicio.py maneje un solo tipo.
        raise ErrorClima(f"No fue posible obtener el clima: {error}") from error
