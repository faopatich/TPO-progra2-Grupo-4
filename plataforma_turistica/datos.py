"""Archivos de entrada: CSV, Excel, JSON y ZIP (N19-N21).

Los ejemplos son académicos. --datos permite sustituirlos por archivos propios.
"""
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent


def preparar_demo(carpeta: Path, fecha: pd.Timestamp) -> Path:
    """Construye Excel y ZIP de ejemplo desde plantillas de texto versionadas."""
    carpeta.mkdir(parents=True, exist_ok=True)
    origen = RAIZ / "datos"
    # CSV conserva el catálogo; Excel aporta capacidad de hoteles por destino.
    destinos = pd.read_csv(origen / "destinos.csv")
    destinos.to_csv(carpeta / "destinos.csv", index=False)
    hoteles = pd.read_csv(origen / "hoteles_demo.csv")
    hoteles.to_excel(carpeta / "hoteles.xlsx", index=False)
    comentarios = pd.read_json(origen / "comentarios_demo.json")
    comentarios.to_json(carpeta / "comentarios.json", orient="records", force_ascii=False)
    # Las fechas relativas mantienen reproducible la demostración cualquier semana.
    historico = pd.read_csv(origen / "historico_demo.csv")
    historico["fecha"] = fecha - pd.to_timedelta(historico.pop("dias_antes"), unit="D")
    historico.to_csv(
        carpeta / "historico.zip", index=False,
        compression={"method": "zip", "archive_name": "historico.csv"},
    )
    html = (origen / "eventos_demo.html").read_text(encoding="utf-8")
    for dia in range(1, 7):
        html = html.replace(f"FECHA_{dia}", (fecha + pd.Timedelta(days=dia - 1)).strftime("%Y-%m-%d"))
    (carpeta / "eventos.html").write_text(html, encoding="utf-8")
    return carpeta


def cargar_archivos(carpeta: Path) -> dict:
    """Lee los cuatro formatos con Pandas; ZIP debe contener un único CSV."""
    tablas = {
        "destinos": pd.read_csv(carpeta / "destinos.csv"),
        "hoteles": pd.read_excel(carpeta / "hoteles.xlsx"),
        "comentarios": pd.read_json(carpeta / "comentarios.json"),
        "historico": pd.read_csv(carpeta / "historico.zip", compression="zip"),
    }
    columnas = {
        "destinos": ["destino", "latitud", "longitud", "zona", "ocupacion_base"],
        "hoteles": ["destino", "hotel", "habitaciones"],
        "comentarios": ["destino", "comentario"],
        "historico": ["destino", "fecha", "ocupacion"],
    }
    for nombre, necesarias in columnas.items():
        faltantes = set(necesarias) - set(tablas[nombre].columns)
        if faltantes:
            raise ValueError(f"Faltan columnas en {nombre}: {', '.join(sorted(faltantes))}")
    return tablas
