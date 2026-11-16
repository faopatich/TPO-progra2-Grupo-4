"""Plataforma modular de análisis turístico."""


def ejecutar_analisis(nombre_destino: str, usar_red: bool = False):
    """Importa el servicio cuando se necesita; permite usar ETL por separado."""
    from .servicio import ejecutar_analisis as analizar
    return analizar(nombre_destino, usar_red)


__all__ = ["ejecutar_analisis"]
