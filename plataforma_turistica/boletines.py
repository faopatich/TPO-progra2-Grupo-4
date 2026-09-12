"""Contenido de boletines; el envío SMTP corresponde a N24."""

from __future__ import annotations


def crear_cuerpo_boletin(destino: str, clasificacion: str, recomendacion: str) -> str:
    """Arma el texto plano de un futuro boletín semanal.

    Esta función solo compone el contenido. El envío con SMTP corresponde a N24
    y se mantiene fuera de este alcance para respetar la modularización.
    """
    # Las f-strings insertan los valores recibidos dentro de un mensaje legible.
    return (
        f"Resumen semanal de {destino}\n"
        f"Clasificación: {clasificacion}\n"
        f"Acción sugerida: {recomendacion}"
    )
