"""Cliente de geocodificación para destinos escritos libremente (N13)."""

from __future__ import annotations

from dataclasses import dataclass

import requests

from .config import ENDPOINTS_API


class ErrorGeocodificacion(RuntimeError):
    """Representa una falla al convertir un nombre en coordenadas."""


@dataclass(frozen=True)
class Coordenadas:
    """Coordenadas geográficas de un destino."""

    latitud: float
    longitud: float


def geocodificar_destino(
    nombre: str,
    session: requests.Session | None = None,
    timeout: int = 10,
) -> Coordenadas:
    """Busca las coordenadas del primer resultado para el nombre recibido."""
    cliente = session or requests.Session()
    parametros = {"name": nombre, "count": 1, "language": "es", "format": "json"}

    try:
        respuesta = cliente.get(
            ENDPOINTS_API["geocodificacion_publica"],
            params=parametros,
            timeout=timeout,
        )
        respuesta.raise_for_status()
        resultados = respuesta.json().get("results") or []
        primero = resultados[0]
        return Coordenadas(
            latitud=float(primero["latitude"]),
            longitud=float(primero["longitude"]),
        )
    except (
        requests.RequestException,
        AttributeError,
        KeyError,
        TypeError,
        ValueError,
        IndexError,
    ) as error:
        raise ErrorGeocodificacion(
            f"No fue posible encontrar coordenadas para '{nombre}'"
        ) from error
