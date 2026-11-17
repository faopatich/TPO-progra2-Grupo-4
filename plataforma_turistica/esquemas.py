"""Contratos de entrada y salida de la API definidos con Pydantic."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SolicitudAnalisis(BaseModel):
    """Datos JSON que acepta POST /analisis.

    Pydantic valida automáticamente los tipos antes de llamar a la lógica.
    """

    destino: str = Field(min_length=2, examples=["Buenos Aires"])
    en_vivo: bool = Field(
        default=True,
        description="Si es verdadero intenta consultar las fuentes externas.",
    )
    enviar_correo: bool = Field(default=False, description="Genera y envía el boletín con adjuntos.")


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
    eventos: int | None
    temperatura: float | None
    lluvia: float | None
    ocupacion: float | None
    variacion: float | None
    menciones: int
    prioridad: float | None
    clasificacion: str
    recomendacion: str
    correo_enviado: bool = False
    # default_factory crea una lista nueva por respuesta y evita compartir estado.
    advertencias: list[str] = Field(default_factory=list)

    fuente_clima: str = ""
    fuente_eventos: str = ""
    fuente_datos: str = ""
    fuente_ocupacion: str = ""
    periodo_ocupacion: str = ""
    positivas: int | None = None
    negativas: int | None = None
    neutras: int | None = None
    total_resenas: int | None = None
    menciones_resenas: int | None = None
    fuente_reputacion: str = "sin datos"
    periodo_reputacion: str = "sin datos"
