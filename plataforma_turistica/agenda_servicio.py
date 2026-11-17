"""Obtención y preparación de eventos para el tablero (N09-N12)."""
import pandas as pd
import requests
from .config import FUENTES_EVENTOS
from .eventos import descargar_html, extraer_eventos, extraer_agenda_caba, ScrapingNoPermitido
from .etl import eventos_a_registros, limpiar_eventos
from .normalizacion import normalizar_texto
from .agenda_nacional import descargar_agenda_nacional, seleccionar_eventos_nacionales, PAGINA_AGENDA


def preparar_agenda(catalogo, carpeta, usar_red, semana):
    """Devuelve eventos filtrados, cobertura, fuentes y advertencias."""
    advertencias = []
    registros = []
    cobertura = {}
    fuentes = {}
    if not usar_red and carpeta is None:
        for clave in catalogo["clave"]:
            cobertura[clave] = False
            fuentes[clave] = "sin datos"
        advertencias.append("No se consultaron fuentes de eventos: active el modo en vivo.")
    elif not usar_red:
        html = (carpeta / "eventos.html").read_text(encoding="utf-8")
        fuente = "archivo del usuario"
        # El HTML local usa data-destino; no se asigna una agenda a todas las ciudades.
        eventos = extraer_eventos(html, "https://example.org/", destino_base="", fuente=fuente)
        registros = eventos_a_registros(eventos)
        claves_archivo = {normalizar_texto(evento.destino) for evento in eventos}
        for clave in catalogo["clave"]:
            cobertura[clave] = clave in claves_archivo
            fuentes[clave] = fuente if cobertura[clave] else "sin datos"
    else:
        nacional = None
        if catalogo["clave"].ne("buenos aires").any():
            try:
                nacional = descargar_agenda_nacional()
            except (requests.RequestException, ValueError):
                advertencias.append("No se pudo consultar la agenda nacional de eventos.")
        for _, destino in catalogo.iterrows():
            clave = destino["clave"]
            cobertura[clave] = False
            fuentes[clave] = "sin datos"
            url = FUENTES_EVENTOS.get(clave)
            if not url:
                if nacional is not None:
                    propios, disponible = seleccionar_eventos_nacionales(nacional, destino["destino"], semana)
                    registros.extend(propios)
                    cobertura[clave] = disponible
                    fuentes[clave] = PAGINA_AGENDA if disponible else "sin datos"
                    if disponible:
                        advertencias.append(f"{destino['destino']}: agenda nacional parcial; no incluye necesariamente todos los eventos.")
                if not cobertura[clave]:
                    advertencias.append(f"{destino['destino']}: no hay eventos identificables en la agenda nacional.")
            else:
                try:
                    html = descargar_html(url)
                    eventos = extraer_agenda_caba(html, url) if clave == "buenos aires" else extraer_eventos(html, url, destino["destino"], "web")
                    if not eventos:
                        raise ValueError("La página no contiene tarjetas reconocidas; revisar selectores HTML.")
                    if clave == "buenos aires":
                        advertencias.append("CABA: se cuentan eventos por fecha de inicio; pueden faltar eventos ya iniciados o no publicados en la agenda.")
                    registros.extend(eventos_a_registros(eventos))
                    cobertura[clave] = True
                    fuentes[clave] = url
                except (requests.RequestException, ScrapingNoPermitido, ValueError) as error:
                    # No incluir URLs con credenciales en los avisos.
                    advertencias.append(f"{destino['destino']}: agenda no disponible ({type(error).__name__}).")
    # Un cambio de HTML que deje todas las fechas sin interpretar no equivale a cero eventos.
    for clave in catalogo["clave"]:
        propios = [registro for registro in registros if normalizar_texto(registro["destino"]) == clave]
        fechas = pd.to_datetime([registro["fecha"] for registro in propios], errors="coerce")
        if propios and fechas.isna().all():
            cobertura[clave] = False
            advertencias.append(f"{clave}: no se pudieron interpretar las fechas; revisar HTML.")
    eventos = limpiar_eventos(registros, semana)
    if registros and len(eventos) < len(registros):
        advertencias.append("Se excluyeron eventos duplicados, sin fecha ISO válida o fuera de la semana.")
    return eventos, cobertura, fuentes, advertencias
