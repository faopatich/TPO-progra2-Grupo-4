"""Archivos de entrada: CSV, Excel, JSON y ZIP (N19-N21).

Los ejemplos son académicos. --datos permite sustituirlos por archivos propios.
"""
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent


def cargar_archivos(carpeta: Path) -> dict:
    """Lee los cuatro formatos con Pandas; ZIP debe contener un único CSV."""
    tablas = {
        "destinos": pd.read_csv(carpeta / "destinos.csv"),
        "hoteles": pd.read_excel(carpeta / "hoteles.xlsx"),
        "comentarios": pd.read_json(carpeta / "comentarios.json"),
        "historico": (pd.read_csv(carpeta / "historico.zip", compression="zip")
                      if (carpeta / "historico.zip").is_file()
                      else pd.DataFrame(columns=["destino", "fecha", "ocupacion"])),
    }
    if "ocupacion_base" not in tablas["destinos"].columns:
        tablas["destinos"]["ocupacion_base"] = None
    columnas = {
        "destinos": ["destino", "latitud", "longitud", "zona"],
        "hoteles": ["destino", "hotel", "habitaciones"],
        "comentarios": ["destino", "comentario"],
        "historico": ["destino", "fecha", "ocupacion"],
    }
    for nombre, necesarias in columnas.items():
        faltantes = set(necesarias) - set(tablas[nombre].columns)
        if faltantes:
            raise ValueError(f"Faltan columnas en {nombre}: {', '.join(sorted(faltantes))}")
    return tablas


def cargar_fuentes_reales() -> dict:
    """Prepara el catálogo y tablas vacías sin inventar hoteles ni reseñas."""
    destinos = pd.read_csv(RAIZ / "datos" / "destinos.csv")
    destinos["ocupacion_base"] = None
    return {
        "destinos": destinos,
        "hoteles": pd.DataFrame(columns=["destino", "hotel", "habitaciones"]),
        "comentarios": pd.DataFrame(columns=["destino", "comentario"]),
        "historico": pd.DataFrame(columns=["destino", "fecha", "ocupacion"]),
    }
