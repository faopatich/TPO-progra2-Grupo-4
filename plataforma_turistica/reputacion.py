"""Análisis básico y explicable de reputación web."""

from __future__ import annotations

from .normalizacion import normalizar_comentario

# Léxicos simples y explicables. No pretenden reemplazar un modelo de lenguaje;
# permiten practicar listas, cadenas y control con un resultado reproducible.
POSITIVAS = ["excelente", "bueno", "limpio", "amable", "recomiendo", "increible"]
NEGATIVAS = ["malo", "sucio", "demora", "ruido", "caro", "problema"]


def analizar_comentarios(comentarios: list[str]) -> dict[str, int]:
    """Clasifica comentarios como positivos, negativos o neutros.

    Un comentario con vocabulario de ambos grupos se considera neutro porque la
    regla no puede decidir un sentimiento dominante con suficiente claridad.
    """
    # El diccionario funciona como acumulador de las tres categorías.
    resultado = {"positivas": 0, "negativas": 0, "neutras": 0}
    for comentario in comentarios:
        # La normalización permite coincidir sin acentos ni mayúsculas.
        texto = normalizar_comentario(comentario)
        tiene_positiva = any(palabra in texto for palabra in POSITIVAS)
        tiene_negativa = any(palabra in texto for palabra in NEGATIVAS)

        # if/elif/else garantiza que cada comentario se cuente una sola vez.
        if tiene_positiva and not tiene_negativa:
            resultado["positivas"] += 1
        elif tiene_negativa and not tiene_positiva:
            resultado["negativas"] += 1
        else:
            resultado["neutras"] += 1
    return resultado
