"""Formato de los resultados utilizados por la API."""
from dataclasses import dataclass
import pandas as pd

@dataclass
class ResultadoAnalisis:
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
    advertencias: tuple[str, ...] = ()
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

    def como_texto(self) -> str:
        return (f"{self.destino}: {self.clasificacion}\n"
                f"Ocupación estimada: {self.ocupacion} | variación: {self.variacion}\n"
                f"Recomendación: {self.recomendacion}\n"
                f"Fuentes: {self.fuente_clima}; {self.fuente_eventos}; {self.fuente_datos}\n"
                + "\n".join(self.advertencias))

