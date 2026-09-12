"""Limpieza de nombres, comentarios, títulos y direcciones (N04 y N07)."""

from __future__ import annotations

import re
import unicodedata


def compactar_espacios(texto: str) -> str:
    """Quita espacios exteriores y reemplaza espacios repetidos por uno solo.

    Args:
        texto: Cadena original, posiblemente con saltos o espacios duplicados.
    Returns:
        La misma información con espacios uniformes.
    """
    # La expresión \s+ incluye espacios, tabulaciones y saltos de línea.
    return re.sub(r"\s+", " ", texto).strip()


def normalizar_texto(texto: str) -> str:
    """Devuelve texto comparable: sin acentos, minúsculo y sin espacios extra.

    Se utiliza para comparar y buscar; no para mostrar contenido al usuario.
    """
    # Primero se uniforman los espacios y las mayúsculas.
    limpio = compactar_espacios(texto).lower()

    # NFD separa una letra acentuada en letra + marca. El filtro elimina las
    # marcas Unicode: por ejemplo, "í" pasa a "i".
    return "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", limpio)
        if unicodedata.category(caracter) != "Mn"
    )


def limpiar_nombre_destino(nombre: str) -> str:
    """Prepara un nombre para mostrarlo con formato de título."""
    return compactar_espacios(nombre).title()


def limpiar_titulo_evento(titulo: str) -> str:
    """Limpia espacios y separadores decorativos alrededor de un título."""
    return compactar_espacios(titulo).strip("-|•")


def limpiar_direccion(direccion: str) -> str:
    """Uniforma espacios y elimina espacios incorrectos antes de una coma."""
    return compactar_espacios(direccion).replace(" ,", ",")


def normalizar_comentario(comentario: str) -> str:
    """Normaliza una opinión antes de buscar palabras de reputación."""
    return normalizar_texto(comentario)
