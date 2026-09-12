"""Contratos de entrada y salida de la API definidos con Pydantic."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SolicitudAnalisis(BaseModel):
    """Datos JSON que acepta POST /analisis.

    Pydantic valida automáticamente los tipos antes de llamar a la lógica.
    """

    destino: str = Field(min_length=2, examples=["Buenos Aires"])
    en_vivo: bool = Field(
        default=False,
        description="Si es verdadero intenta consultar las fuentes externas.",
    )


class RespuestaSalud(BaseModel):
    """Contrato del endpoint usado para comprobar que la API está disponible."""

    estado: str
    servicio: str
    version: str


class RespuestaDestinos(BaseModel):
    """Contrato de la colección de destinos habilitados."""

    cantidad: int
    destinos: list[str]


class RespuestaAnalisis(BaseModel):
    """Contrato JSON completo de un análisis turístico."""

    destino: str
    eventos: int
    temperatura: float
    lluvia: float
    ocupacion: float
    variacion: float
    menciones: int
    prioridad: float
    clasificacion: str
    recomendacion: str
    # default_factory crea una lista nueva por respuesta y evita compartir estado.
    advertencias: list[str] = Field(default_factory=list)
