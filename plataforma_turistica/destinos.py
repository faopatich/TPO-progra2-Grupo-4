"""Acceso y validación de destinos configurados."""

from __future__ import annotations

from copy import deepcopy

from .config import DESTINOS
from .normalizacion import normalizar_texto


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
        ValueError: Si el destino no se encuentra en la configuración.
    """
    # Se normaliza la entrada para compararla con las claves de DESTINOS.
    clave = normalizar_texto(nombre)
    if clave not in DESTINOS:
        # Mostrar opciones válidas ayuda a corregir el dato sin mirar el código.
        disponibles = ", ".join(listar_destinos())
        raise ValueError(f"Destino desconocido. Opciones: {disponibles}")

    # deepcopy impide que quien recibe el resultado modifique la configuración.
    return deepcopy(DESTINOS[clave])
