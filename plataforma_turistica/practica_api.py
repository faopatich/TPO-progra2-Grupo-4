"""Prácticas de cliente GET autenticado, JSON/XML y POST local (N14-N18)."""
import argparse
import os
from pathlib import Path
from time import sleep
import xml.etree.ElementTree as ET
import requests
from dotenv import load_dotenv
from .clima import Clima, ErrorClima
from .datos import RAIZ


def interpretar_pronostico(respuesta, formato: str) -> Clima:
    """JSON usa claves y listas; XML usa elementos y atributos."""
    if formato == "json":
        datos = respuesta.json()["list"][0]
        temperatura = float(datos["main"]["temp"])
        probabilidad = float(datos["pop"]) * 100
        codigo = int(datos["weather"][0]["id"])
    elif formato == "xml":
        raiz = ET.fromstring(respuesta.text)
        intervalo = raiz.find("./forecast/time")
        temperatura = float(intervalo.find("temperature").attrib["value"])
        probabilidad = float(intervalo.find("precipitation").attrib["probability"]) * 100
        codigo = int(intervalo.find("symbol").attrib["number"])
    else:
        raise ValueError("El formato debe ser json o xml")
    if not 0 <= probabilidad <= 100:
        raise ValueError("Probabilidad meteorológica inválida")
    return Clima(temperatura, probabilidad, codigo, "OpenWeatherMap: próximo intervalo de 3 horas")


def consultar_clima_autenticado(latitud: float, longitud: float,
                               formato="json", session=None) -> Clima:
    """Lee la clave del entorno y nunca la guarda en código, reportes ni errores."""
    clave = os.getenv("OPENWEATHER_API_KEY", "").strip()
    if not clave:
        raise ErrorClima("Falta OPENWEATHER_API_KEY para la práctica autenticada.")
    if formato not in {"json", "xml"}:
        raise ErrorClima("El formato debe ser json o xml.")
    cliente = session or requests.Session()
    parametros = {"lat": latitud, "lon": longitud, "appid": clave,
                  "units": "metric", "mode": formato, "cnt": 1}
    try:
        sleep(1)  # Pausa entre consultas; no reintenta automáticamente ante 429.
        respuesta = cliente.get("https://api.openweathermap.org/data/2.5/forecast",
                                 params=parametros, timeout=10,
                                 headers={"Accept": "application/xml" if formato == "xml" else "application/json"})
        if respuesta.status_code == 429:
            raise ErrorClima("Límite de consultas alcanzado (429); esperar antes de volver a ejecutar.")
        if respuesta.status_code in {401, 403}:
            raise ErrorClima("La API rechazó la clave (401/403); revise su activación y permisos.")
        respuesta.raise_for_status()
        return interpretar_pronostico(respuesta, formato)
    except (requests.RequestException, KeyError, IndexError, TypeError,
            ValueError, AttributeError, ET.ParseError):
        raise ErrorClima("No se pudo obtener o interpretar el pronóstico autenticado.") from None


def solicitar_analisis_post(destino: str, session=None) -> dict:
    """POST como cliente de la API del TPO; no envía información a terceros."""
    cliente = session or requests.Session()
    respuesta = cliente.post(
        "http://127.0.0.1:8000/analisis",
        json={"destino": destino, "en_vivo": False},
        headers={"Accept": "application/json"}, timeout=15,
    )
    respuesta.raise_for_status()
    return respuesta.json()


def main() -> None:
    load_dotenv(RAIZ / ".env")
    parser = argparse.ArgumentParser(description="Prácticas requests de la materia")
    parser.add_argument("--formato", choices=["json", "xml"], default="json")
    parser.add_argument("--post-local", help="Nombre del destino para POST a la API local")
    opciones = parser.parse_args()
    try:
        if opciones.post_local:
            print(solicitar_analisis_post(opciones.post_local))
        else:
            print(consultar_clima_autenticado(-34.6037, -58.3816, opciones.formato))
    except (ErrorClima, requests.RequestException):
        parser.exit(1, "No se completó la práctica. Revise la clave, conexión o servidor local.\n")


if __name__ == "__main__":
    main()
