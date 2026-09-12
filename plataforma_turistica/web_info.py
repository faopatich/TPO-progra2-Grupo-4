"""Información de navegador, URL, dominio, DNS e IP (N08)."""

from __future__ import annotations

import socket
from urllib.parse import urlparse


def describir_recurso_web(url: str, navegador: str = "navegador moderno") -> dict:
    """Descompone una URL y resuelve las direcciones IP actuales del dominio.

    Args:
        url: Dirección HTTP o HTTPS inspeccionada.
        navegador: Nombre del navegador utilizado para documentar la práctica.
    Returns:
        Diccionario con navegador, URL, protocolo, dominio DNS e IPs.
    Raises:
        ValueError: Si la dirección no representa una URL web válida.
    """
    # urlparse separa la URL sin depender de posiciones de texto manuales.
    partes = urlparse(url)
    if partes.scheme not in {"http", "https"} or not partes.hostname:
        raise ValueError("La URL debe ser HTTP o HTTPS y contener un dominio")
    try:
        # DNS puede devolver varias IPs; set elimina duplicados y sorted las ordena.
        ips = sorted(set(socket.gethostbyname_ex(partes.hostname)[2]))
    except socket.gaierror:
        # Una falla temporal de DNS no impide documentar el resto de la URL.
        ips = []
    return {
        "navegador": navegador,
        "url": url,
        "protocolo": partes.scheme,
        "dominio_dns": partes.hostname,
        "ips": ips,
    }
