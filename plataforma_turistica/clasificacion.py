"""Reglas de control para clasificar destinos (N03)."""

from __future__ import annotations

from .config import CRITERIOS_RECOMENDACION


def clasificar_destino(
    ocupacion: float,
    variacion_demanda: float,
    menciones: int,
    probabilidad_lluvia: float,
) -> str:
    """Asigna una categoría mediante reglas de negocio ordenadas por prioridad.

    Primero se controla el clima porque puede cambiar la operación incluso con
    demanda alta. Luego se evalúan alta demanda, oportunidad y baja actividad.
    """
    criterios = CRITERIOS_RECOMENDACION

    # Un riesgo meteorológico alto prevalece sobre las señales comerciales.
    if probabilidad_lluvia >= criterios["riesgo_climatico"]["probabilidad_lluvia_minima"]:
        return "riesgo climático"

    # Basta cumplir uno de los dos indicadores para detectar alta demanda.
    # Una ocupación media o varias menciones muestran potencial de crecimiento.
    if (
        ocupacion >= criterios["alta_demanda"]["ocupacion_minima"]
        or variacion_demanda >= criterios["alta_demanda"]["variacion_minima"]
    ):
        return "alta demanda"
    if (
        ocupacion >= criterios["oportunidad"]["ocupacion_minima"]
        or menciones >= criterios["oportunidad"]["menciones_minimas"]
    ):
        return "oportunidad"
    # Si no se cumple ninguna condición anterior, se usa la categoría base.
    return "baja actividad"


def recomendar_accion(clasificacion: str) -> str:
    """Traduce una clasificación conocida en una acción operativa concreta."""
    # El diccionario evita una cadena larga de if para una correspondencia exacta.
    acciones = {
        "alta demanda": "Aumentar disponibilidad y proteger tarifas.",
        "oportunidad": "Lanzar una campaña segmentada alrededor de los eventos.",
        "riesgo climático": "Preparar alternativas bajo techo y comunicar cambios.",
        "baja actividad": "Crear promociones y alianzas para estimular reservas.",
    }
    # Una clave desconocida genera KeyError y deja visible un error de integración.
    return acciones[clasificacion]
