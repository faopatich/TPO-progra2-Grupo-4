"""Scraping responsable y extracción de HTML (N09-N12)."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from time import sleep
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup, Tag

from .normalizacion import limpiar_direccion, limpiar_titulo_evento

AGENTE = "TPO-Turismo-Educativo/1.0 (uso académico; 1 solicitud por ejecución)"


class ScrapingNoPermitido(RuntimeError):
    """Indica que robots.txt no permite o no pudo autorizar la descarga."""


@dataclass(frozen=True)
class Evento:
    """Representa un evento y los atributos HTML recuperados de su tarjeta."""

    titulo: str
    fecha: str
    direccion: str
    enlace: str | None
    imagen: str | None
    clases_html: tuple[str, ...]
    identificador_html: str | None
    datos_html: dict[str, str]
    destino: str = "Buenos Aires"
    fuente: str = "web"


def _robots_permite(url: str, session: requests.Session, timeout: int) -> bool:
    """Consulta robots.txt y decide si el agente académico puede visitar la URL.

    Es una función interna (por eso empieza con ``_``) y solo la usa el módulo.
    Ante un estado HTTP de error adopta una postura conservadora: no descargar.
    """
    # urlparse separa esquema, dominio, ruta y otros componentes de la URL.
    partes = urlparse(url)
    robots_url = f"{partes.scheme}://{partes.netloc}/robots.txt"

    # El mismo User-Agent identifica tanto la consulta de reglas como el scraping.
    respuesta = session.get(robots_url, headers={"User-Agent": AGENTE}, timeout=timeout)
    if respuesta.status_code >= 400:
        return False

    # RobotFileParser interpreta las reglas User-agent, Allow y Disallow.
    analizador = RobotFileParser()
    analizador.set_url(robots_url)
    analizador.parse(respuesta.text.splitlines())
    return analizador.can_fetch(AGENTE, url)


def descargar_html(
    url: str,
    session: requests.Session | None = None,
    timeout: int = 10,
    espera_segundos: float = 1.0,
) -> str:
    """Descarga una página después de consultar robots.txt y aplicar una pausa.

    Args:
        url: Página HTML que se desea recuperar.
        session: Sesión opcional para reutilizar conexiones o realizar pruebas.
        timeout: Tiempo máximo de espera para cada solicitud.
        espera_segundos: Pausa respetuosa previa a la descarga.
    Returns:
        Contenido HTML como cadena.
    Raises:
        ScrapingNoPermitido: Si robots.txt no autoriza la operación.
        requests.RequestException: Si falla la descarga o el estado HTTP.
    """
    cliente = session or requests.Session()

    # Nunca se descarga el contenido principal sin autorización de robots.txt.
    if not _robots_permite(url, cliente, timeout):
        raise ScrapingNoPermitido(f"robots.txt no autoriza la consulta de {url}")

    # max evita que un valor negativo provoque una espera inválida.
    sleep(max(0.0, espera_segundos))
    respuesta = cliente.get(url, headers={"User-Agent": AGENTE}, timeout=timeout)
    respuesta.raise_for_status()
    return respuesta.text


def extraer_fecha(texto: str) -> str:
    """Busca una fecha dentro de texto libre usando separadores frecuentes."""
    # join/split compacta espacios, tabulaciones y saltos de línea.
    texto = " ".join(texto.split())
    separadores = ("Fecha:", "Fecha", "|")

    # Se retorna la primera porción no vacía encontrada después de un separador.
    for separador in separadores:
        if separador in texto:
            valor = texto.split(separador, 1)[1].strip(" :-|")
            if valor:
                return valor
    return "Fecha no informada"


def _valor_texto(contenedor: Tag, selectores: tuple[str, ...], defecto: str) -> str:
    """Prueba selectores CSS en orden y devuelve el primer texto encontrado."""
    for selector in selectores:
        elemento = contenedor.select_one(selector)
        if elemento:
            # El separador conserva palabras de etiquetas internas sin pegarlas.
            return elemento.get_text(" ", strip=True)
    return defecto


def extraer_eventos(
    html: str, url_base: str, destino_base: str = "Buenos Aires", fuente: str = "web"
) -> list[Evento]:
    """Convierte tarjetas HTML en una lista estructurada de eventos.

    Tolera variantes comunes de maquetado y atributos ausentes. Las URLs relativas
    se completan con ``url_base`` y los duplicados se eliminan por título + enlace.
    """
    # html.parser crea el árbol de objetos BeautifulSoup.
    soup = BeautifulSoup(html, "html.parser")

    # Se buscan article o div cuya clase sugiera que contienen un evento. La lambda
    # acepta páginas que nombren sus tarjetas "evento", "event" o "views-row".
    tarjetas = soup.find_all(["article", "div"], class_=lambda c: c and any(
        palabra in " ".join(c if isinstance(c, list) else [c]).lower()
        for palabra in ("evento", "event", "views-row")
    ))
    eventos: list[Evento] = []
    vistos: set[tuple[str, str | None]] = set()
    for tarjeta in tarjetas:
        # Los selectores se prueban de más específico a más genérico.
        titulo = _valor_texto(tarjeta, ("h2", "h3", ".titulo", ".title"), "")
        enlace_tag = tarjeta.find("a", href=True)

        # Si falta un encabezado, el texto del enlace puede servir como título.
        if not titulo and enlace_tag:
            titulo = enlace_tag.get_text(" ", strip=True)
        if not titulo:
            # Sin título no hay identidad suficiente para crear un Evento.
            continue

        # urljoin mantiene URLs absolutas y completa las relativas con el dominio.
        enlace = urljoin(url_base, enlace_tag.get("href")) if enlace_tag else None
        clave = (titulo, enlace)
        if clave in vistos:
            continue
        vistos.add(clave)

        # Cada dato se valida porque una tarjeta real puede no traerlo.
        imagen_tag = tarjeta.find("img")
        imagen = urljoin(url_base, imagen_tag.get("src")) if imagen_tag and imagen_tag.get("src") else None
        fecha = _valor_texto(tarjeta, ("time", ".fecha", ".date"), "")
        etiqueta_fecha = tarjeta.find("time")
        if etiqueta_fecha and etiqueta_fecha.get("datetime"):
            fecha = etiqueta_fecha["datetime"]
        if not fecha:
            fecha = extraer_fecha(tarjeta.get_text(" ", strip=True))
        direccion = _valor_texto(tarjeta, (".direccion", ".address"), "No informada")

        # El diccionario data_html conserva atributos personalizados data-*.
        eventos.append(
            Evento(
                destino=tarjeta.get("data-destino", destino_base),
                fuente=fuente,
                titulo=limpiar_titulo_evento(titulo),
                fecha=fecha,
                direccion=limpiar_direccion(direccion),
                enlace=enlace,
                imagen=imagen,
                clases_html=tuple(tarjeta.get("class", [])),
                identificador_html=tarjeta.get("id"),
                datos_html={k: str(v) for k, v in tarjeta.attrs.items() if k.startswith("data-")},
            )
        )
    return eventos



def extraer_agenda_caba(html: str, url_base: str) -> list[Evento]:
    """Lee el JSON público embebido en la agenda semanal oficial de CABA.

    Se considera solo la fecha de inicio informada; una actividad que empezó
    antes de la semana no se cuenta aunque continúe durante ella.
    """
    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all("script"):
        contenido = script.string or script.get_text()
        coincidencia = re.search(r"const\s+json\s*=\s*`(.*?)`", contenido, re.S)
        if not coincidencia:
            continue
        try:
            datos = json.loads(coincidencia.group(1))
        except (ValueError, TypeError) as error:
            raise ValueError("No se pudo interpretar la agenda de CABA") from error
        if not isinstance(datos, list):
            raise ValueError("Formato inesperado de agenda de CABA")
        eventos = []
        for dato in datos:
            if not isinstance(dato, dict) or dato.get("categoria_actividad_filtro", "").strip().lower() != "evento":
                continue
            titulo = dato.get("nombre_actividad", "").strip()
            fecha = dato.get("fecha_inicio", "").strip()
            if not titulo or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fecha):
                continue
            eventos.append(Evento(titulo=limpiar_titulo_evento(titulo), fecha=fecha,
                direccion=limpiar_direccion(dato.get("calle_altura", "") or "No informada"),
                enlace=urljoin(url_base, dato.get("url_boton") or url_base),
                imagen=urljoin(url_base, dato["foto"]) if dato.get("foto") else None,
                clases_html=(), identificador_html=None, datos_html={},
                destino="Buenos Aires", fuente=url_base))
        if not eventos:
            raise ValueError("La agenda de CABA no contiene eventos con fecha reconocible")
        return eventos
    raise ValueError("No se encontró el JSON de la agenda de CABA")

def demostrar_find_all(html: str) -> dict[str, int]:
    """Ejecuta las siete búsquedas de N12 y devuelve su cantidad de resultados.

    Incluye búsquedas por etiqueta, clase, id, atributo, texto, función lambda y
    combinación de criterios para que cada forma pueda demostrarse por separado.
    """
    soup = BeautifulSoup(html, "html.parser")
    return {
        "por_etiqueta": len(soup.find_all("a")),
        "por_clase": len(soup.find_all(class_="evento")),
        "por_id": len(soup.find_all(id="agenda-eventos")),
        "por_atributo": len(soup.find_all(attrs={"data-tipo": "cultural"})),
        "por_texto": len(soup.find_all(string=lambda t: t and "Festival" in t)),
        "por_lambda": len(soup.find_all(lambda tag: tag.name == "img" and tag.get("src"))),
        "combinada": len(soup.find_all("article", class_="evento", attrs={"data-tipo": "cultural"})),
    }


def inventario_html(html: str) -> dict[str, int]:
    """Cuenta las etiquetas principales solicitadas en N09."""
    soup = BeautifulSoup(html, "html.parser")
    etiquetas = ["html", "head", "body", "div", "table", "tr", "td", "a", "img", "span"]

    # La comprensión produce pares etiqueta: cantidad en un solo recorrido lógico.
    return {etiqueta: len(soup.find_all(etiqueta)) for etiqueta in etiquetas}
