"""Orquestación del caso de uso sin mezclar responsabilidades."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .clasificacion import clasificar_destino, recomendar_accion
from .clima import Clima, ErrorClima, consultar_clima
from .config import PALABRAS_CLAVE, URLS_EVENTOS
from .destinos import obtener_destino
from .eventos import descargar_html, extraer_eventos
from .indicadores import (
    calcular_ocupacion_estimada,
    calcular_prioridad_comercial,
    calcular_variacion_demanda,
    contar_menciones,
)
from .reputacion import analizar_comentarios
from .visualizacion import barra_textual

# Ruta absoluta calculada desde este módulo, independiente de la carpeta desde la
# que el usuario ejecute el programa.
ARCHIVO_HTML_DEMO = Path(__file__).resolve().parent.parent / "datos" / "eventos_demo.html"

# Opiniones controladas para demostrar reputación sin depender de una plataforma.
COMENTARIOS_DEMO = [
    "Excelente ubicación y personal amable",
    "Mucho ruido durante la noche",
    "El festival fue increíble, lo recomiendo",
    "La habitación estaba limpia",
]


@dataclass(frozen=True)
class ResultadoAnalisis:
    """Agrupa todas las salidas producidas para un destino.

    La dataclass genera el constructor automáticamente. ``frozen=True`` hace que
    el resultado no pueda cambiar después de finalizar los cálculos.
    """

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
    advertencias: tuple[str, ...] = ()

    def como_texto(self) -> str:
        """Convierte el resultado en un informe multilínea para la terminal."""
        # Cada f-string controla la etiqueta y el formato decimal de un indicador.
        lineas = [
            f"Destino: {self.destino}",
            f"Eventos encontrados: {self.eventos}",
            f"Clima: {self.temperatura:.1f} °C | lluvia {self.lluvia:.0f}%",
            f"Ocupación estimada: {self.ocupacion:.1f}% {barra_textual(self.ocupacion)}",
            f"Variación de demanda: {self.variacion:+.1f}%",
            f"Menciones relevantes: {self.menciones}",
            f"Prioridad comercial: {self.prioridad:.1f}/100",
            f"Clasificación: {self.clasificacion}",
            f"Recomendación: {self.recomendacion}",
        ]

        # Las advertencias solo aparecen si falló alguna fuente externa.
        lineas.extend(f"Aviso: {aviso}" for aviso in self.advertencias)
        return "\n".join(lineas)


def ejecutar_analisis(nombre_destino: str, usar_red: bool = False) -> ResultadoAnalisis:
    """Ejecuta el flujo completo de análisis turístico hasta N13.

    Args:
        nombre_destino: Destino configurado que se desea procesar.
        usar_red: Si es True intenta agenda y clima reales; si es False usa demo.
    Returns:
        Un ``ResultadoAnalisis`` listo para mostrar o reutilizar.
    Raises:
        ValueError: Si el destino solicitado no existe.

    La función orquesta módulos especializados: no implementa internamente el
    scraping, las fórmulas ni la clasificación.
    """
    # Validar primero evita hacer trabajo de red para un destino inexistente.
    destino = obtener_destino(nombre_destino)
    advertencias: list[str] = []

    # En modo en vivo se intentan ambas fuentes por separado. Si una falla, cada
    # except conserva una alternativa local y registra el motivo para el usuario.
    if usar_red:
        try:
            html = descargar_html(URLS_EVENTOS[0])
        except Exception as error:  # el programa conserva una demostración útil ante fallas externas
            html = ARCHIVO_HTML_DEMO.read_text(encoding="utf-8")
            advertencias.append(f"agenda en vivo no disponible; se usó HTML local ({error})")
        try:
            # Las coordenadas configuradas se envían como parámetros a Open-Meteo.
            coordenadas = destino["coordenadas"]
            clima = consultar_clima(coordenadas["latitud"], coordenadas["longitud"])
        except ErrorClima as error:
            # Valores moderados de demostración mantienen operativo el análisis.
            clima = Clima(temperatura=20, probabilidad_lluvia=20, codigo=0, fuente="demo")
            advertencias.append(str(error))
    else:
        # El modo predeterminado es determinista y funciona en el aula sin red.
        html = ARCHIVO_HTML_DEMO.read_text(encoding="utf-8")
        clima = Clima(temperatura=20, probabilidad_lluvia=20, codigo=0, fuente="demo")

    # Extracción y reputación producen las entradas necesarias para las métricas.
    eventos = extraer_eventos(html, URLS_EVENTOS[0])
    reputacion = analizar_comentarios(COMENTARIOS_DEMO)

    # Se combinan títulos y comentarios para buscar menciones comerciales.
    textos = [evento.titulo for evento in eventos] + COMENTARIOS_DEMO
    menciones = contar_menciones(textos, PALABRAS_CLAVE)

    # Los cálculos se ejecutan en orden porque variación y prioridad dependen del
    # valor de ocupación que se acaba de estimar.
    ocupacion = calcular_ocupacion_estimada(
        destino["ocupacion_base"],
        len(eventos),
        reputacion["positivas"],
        reputacion["negativas"],
        clima.probabilidad_lluvia,
    )
    variacion = calcular_variacion_demanda(ocupacion, destino["ocupacion_base"])
    prioridad = calcular_prioridad_comercial(ocupacion, variacion, menciones)
    clasificacion = clasificar_destino(
        ocupacion, variacion, menciones, clima.probabilidad_lluvia
    )

    # Finalmente se empaquetan datos y alertas en un único objeto inmutable.
    return ResultadoAnalisis(
        destino=destino["nombre"],
        eventos=len(eventos),
        temperatura=clima.temperatura,
        lluvia=clima.probabilidad_lluvia,
        ocupacion=ocupacion,
        variacion=variacion,
        menciones=menciones,
        prioridad=prioridad,
        clasificacion=clasificacion,
        recomendacion=recomendar_accion(clasificacion),
        advertencias=tuple(advertencias),
    )
