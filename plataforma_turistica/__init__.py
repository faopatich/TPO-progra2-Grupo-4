"""Plataforma modular de análisis turístico."""

# Reexportar la función principal permite usar
# ``from plataforma_turistica import ejecutar_analisis``.
from .servicio import ejecutar_analisis

# __all__ declara cuál es la interfaz pública del paquete.
__all__ = ["ejecutar_analisis"]
