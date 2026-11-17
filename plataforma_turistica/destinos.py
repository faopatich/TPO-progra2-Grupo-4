"""Acceso y validación de destinos configurados."""

from __future__ import annotations

from copy import deepcopy

from .config import DESTINOS
from .normalizacion import limpiar_nombre_destino, normalizar_texto


def listar_destinos() -> list[str]:
    """Devuelve los nombres visibles de todos los destinos configurados."""
    # La comprensión recorre los valores porque allí está el nombre presentable.
    return [datos["nombre"] for datos in DESTINOS.values()]


def obtener_destino(nombre: str) -> dict:
    """Busca un destino por nombre y entrega una copia de sus datos.

    Args:
        nombre: Nombre escrito por el usuario.
    Returns:
        Diccionario con nombre, coordenadas y zona; si no está en el catálogo,
        devuelve una configuración básica para permitir nombres libres.
    """
    # Se normaliza la entrada para compararla con las claves de DESTINOS.
    clave = normalizar_texto(nombre)
    if clave not in DESTINOS:
        # Los datos específicos se completan con geocodificación cuando se usa
        # el modo en vivo.
        return {
            "nombre": limpiar_nombre_destino(nombre),
            "coordenadas": None,
            "zona": "No informada",
        }

    # deepcopy impide que quien recibe el resultado modifique la configuración.
    return deepcopy(DESTINOS[clave])


def seleccionar_destinos(tablas, nombres):
    """Selecciona destinos y resuelve nombres alternativos (N04-N06)."""
    import pandas as pd
    catalogo = tablas["destinos"]
    if nombres:
        # CABA y Ciudad de Buenos Aires nombran el mismo destino; la provincia
        # es una unidad diferente y nunca se sustituye por la ciudad.
        alias = {"caba": "Buenos Aires", "ciudad de buenos aires": "Buenos Aires",
                 "provincia de buenos aires": "Provincia de Buenos Aires"}
        nombres = [alias.get(normalizar_texto(nombre), nombre) for nombre in nombres]
        claves = [normalizar_texto(nombre) for nombre in nombres]
        for nombre, clave in zip(nombres, claves):
            if not clave:
                raise ValueError("El destino no puede estar vacío")
            if clave not in catalogo["clave"].values:
                destino = obtener_destino(nombre)
                if clave == "provincia de buenos aires":
                    destino["zona"] = "Provincia de Buenos Aires"
                coordenadas = destino["coordenadas"] or {}
                extra = pd.DataFrame([{
                    "clave": clave, "destino": destino["nombre"], "zona": destino["zona"],
                    "latitud": coordenadas.get("latitud"), "longitud": coordenadas.get("longitud"),
                    "ocupacion_base": None,
                }])
                catalogo = pd.concat([catalogo, extra], ignore_index=True)
        catalogo = catalogo.loc[catalogo["clave"].isin(claves)].copy()
    if catalogo.empty:
        raise ValueError("No hay destinos válidos para analizar")
    return catalogo
