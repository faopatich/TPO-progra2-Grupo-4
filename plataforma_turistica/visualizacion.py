"""Preparación de datos para visualización; DataFrame.plot corresponde a N23."""

from __future__ import annotations


def barra_textual(valor: float, maximo: float = 100, ancho: int = 20) -> str:
    """Representa un valor como una barra ASCII de ancho fijo.

    Args:
        valor: Número que se desea representar.
        maximo: Valor equivalente a una barra completa.
        ancho: Cantidad total de caracteres de la barra.
    Returns:
        Cadena formada por ``#`` llenos y ``-`` vacíos.
    """
    # Si maximo no es válido se usa cero; en otro caso se limita entre 0 y 1.
    proporcion = 0 if maximo <= 0 else max(0.0, min(1.0, valor / maximo))

    # La proporción se transforma en una cantidad entera de caracteres.
    llenos = round(proporcion * ancho)
    # Caracteres ASCII para que también funcione en terminales Windows cp1252.
    return "#" * llenos + "-" * (ancho - llenos)
