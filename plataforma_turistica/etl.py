"""Preparación de registros; el ETL con Pandas se incorporará desde N19."""

from __future__ import annotations

from dataclasses import asdict

from .eventos import Evento


def eventos_a_registros(eventos: list[Evento]) -> list[dict]:
    """Convierte objetos Evento en diccionarios listos para una tabla o archivo.

    ``asdict`` también convierte de forma segura los campos de la dataclass. La
    carga con Pandas y la exportación completa se incorporarán desde N19.
    """
    return [asdict(evento) for evento in eventos]
