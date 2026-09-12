"""Operadores e indicadores turísticos (N02)."""

from __future__ import annotations

from .normalizacion import normalizar_texto


def calcular_ocupacion_estimada(
    ocupacion_base: float,
    cantidad_eventos: int,
    menciones_positivas: int,
    menciones_negativas: int,
    probabilidad_lluvia: float,
) -> float:
    """Estima ocupación combinando actividad, reputación y riesgo de lluvia.

    Cada evento suma 2 puntos, el saldo de reputación aporta 0,5 por comentario
    y la lluvia descuenta 0,15 por cada punto porcentual de probabilidad.
    El resultado queda limitado al intervalo válido de 0 a 100.
    """
    # Los operadores convierten variables distintas en un indicador común.
    estimacion = (
        ocupacion_base
        + cantidad_eventos * 2
        + (menciones_positivas - menciones_negativas) * 0.5
        - probabilidad_lluvia * 0.15
    )
    # min aplica el techo de 100 y max evita ocupaciones negativas.
    return round(max(0.0, min(100.0, estimacion)), 2)


def calcular_variacion_demanda(valor_actual: float, valor_anterior: float) -> float:
    """Calcula el cambio porcentual respecto del valor anterior.

    Devuelve cero cuando la base anterior es cero para evitar una división
    inválida. El resultado puede ser positivo o negativo.
    """
    if valor_anterior == 0:
        return 0.0
    return round(((valor_actual - valor_anterior) / valor_anterior) * 100, 2)


def contar_menciones(textos: list[str], palabras_clave: list[str]) -> int:
    """Cuenta cuántos textos contienen al menos una palabra relevante.

    Un texto con dos palabras clave cuenta una sola vez. La normalización permite
    comparar sin diferencias de mayúsculas o acentos.
    """
    # Se normalizan primero las palabras para no repetir ese trabajo por texto.
    palabras = [normalizar_texto(palabra) for palabra in palabras_clave]

    # any corta al encontrar la primera coincidencia; sum cuenta los textos True.
    return sum(
        1
        for texto in textos
        if any(palabra in normalizar_texto(texto) for palabra in palabras)
    )


def calcular_prioridad_comercial(
    ocupacion: float, variacion_demanda: float, menciones: int
) -> float:
    """Calcula un puntaje comercial ponderado entre 0 y 100.

    La ocupación pesa 55 %, la variación ajustada aporta 15 % y cada mención
    suma 1,5 puntos hasta un máximo de veinte menciones.
    """
    # Se acotan variaciones extremas para que no dominen todo el puntaje.
    demanda_normalizada = max(-100.0, min(100.0, variacion_demanda))

    # La suma ponderada prioriza la ocupación, principal señal operativa.
    puntaje = ocupacion * 0.55 + (demanda_normalizada + 100) * 0.15 + min(menciones, 20) * 1.5
    return round(max(0.0, min(100.0, puntaje)), 2)
