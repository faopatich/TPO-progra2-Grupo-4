"""Punto de entrada de la plataforma turística (alcance N01-N13)."""

from __future__ import annotations

import argparse

from plataforma_turistica.servicio import ejecutar_analisis


def crear_parser() -> argparse.ArgumentParser:
    """Configura y devuelve el lector de argumentos de la terminal.

    Returns:
        Un ``ArgumentParser`` que reconoce el modo en vivo y el destino.
    """
    # ``description`` aparece al ejecutar ``python main.py --help``.
    parser = argparse.ArgumentParser(description="Analítica turística por destino")

    # ``store_true`` produce False por defecto y True si se escribe --en-vivo.
    parser.add_argument(
        "--en-vivo",
        action="store_true",
        help="consulta Open-Meteo y la agenda oficial; sin esta opción usa datos de demostración",
    )

    # Este argumento recibe texto. Si falta, se analiza Buenos Aires.
    parser.add_argument(
        "--destino",
        default="Buenos Aires",
        help="destino configurado que se desea analizar",
    )
    return parser


def main() -> None:
    """Lee las opciones, ejecuta el análisis y muestra el informe final."""
    # parse_args convierte lo escrito en la terminal en atributos de un objeto.
    argumentos = crear_parser().parse_args()

    # El servicio contiene la lógica; main solo coordina entrada y salida.
    resultado = ejecutar_analisis(argumentos.destino, usar_red=argumentos.en_vivo)
    print(resultado.como_texto())


if __name__ == "__main__":
    # Evita ejecutar main cuando este archivo es importado desde una prueba.
    main()
