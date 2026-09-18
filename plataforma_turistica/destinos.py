"""Acceso y validación de destinos configurados."""

from __future__ import annotations

from copy import deepcopy

from .config import DESTINOS
from .normalizacion import limpiar_nombre_destino, normalizar_texto


def listar_destinos() -> list[str]:
    """Devuelve los nombres visibles de todos los destinos configurados."""
    # La comprensión recorre los valores porque allí está el nombre presentable.
    return [datos["nombre"] for datos in DESTINOS.values()]


def obtener_destino(nombre: str) -> dict:
    """Busca un destino por nombre y entrega una copia de sus datos.

    Args:
        nombre: Nombre escrito por el usuario.
    Returns:
        Diccionario independiente con nombre, coordenadas, zona y ocupación base.
    Raises:
        Un diccionario con la configuración del destino. Si no está en el
        catálogo, devuelve una configuración básica para permitir nombres libres.
    """
    # Se normaliza la entrada para compararla con las claves de DESTINOS.
    clave = normalizar_texto(nombre)
    if clave not in DESTINOS:
        # Los datos específicos se completan con geocodificación cuando se usa
        # el modo en vivo; el modo demo no necesita coordenadas.
        return {
            "nombre": limpiar_nombre_destino(nombre),
            "coordenadas": None,
            "zona": "No informada",
            "ocupacion_base": 50.0,
        }

    # deepcopy impide que quien recibe el resultado modifique la configuración.
    return deepcopy(DESTINOS[clave])
