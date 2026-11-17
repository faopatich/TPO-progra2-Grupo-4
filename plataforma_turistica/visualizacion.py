"""Gráficos básicos con DataFrame.plot y Series.plot (N23)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # Guarda PNG sin abrir ventanas, también desde la API.
import matplotlib.pyplot as plt


def generar_graficos(tablero, historico, carpeta: Path) -> list[Path]:
    """Barras comparan destinos; líneas muestran períodos comparables."""
    carpeta.mkdir(parents=True, exist_ok=True)
    archivos = []
    ocupacion = tablero.set_index("destino")["ocupacion"].dropna()
    if not ocupacion.empty:
        ax = ocupacion.plot(kind="bar", figsize=(8, 5), color="#247d88", ylim=(0, 100))
        ax.set(title="Ocupación estimada — modelo académico", xlabel="Destino", ylabel="Indicador académico (%)")
        ax.tick_params(axis="x", rotation=20)
        ruta = carpeta / "ocupacion.png"
        ax.figure.tight_layout()
        ax.figure.savefig(ruta, dpi=150)
        plt.close(ax.figure)
        archivos.append(ruta)
    if not historico.empty:
        tabla = historico.pivot_table(index="fecha", columns="destino", values="ocupacion", aggfunc="mean")
        ax = tabla.plot(kind="line", marker="o", figsize=(8, 5), ylim=(0, 100))
        ax.set(title="Referencia anterior y estimación ajustada — revisar fuentes",
               xlabel="Fecha", ylabel="Indicador académico (%)")
        ruta = carpeta / "tendencia.png"
        ax.figure.tight_layout()
        ax.figure.savefig(ruta, dpi=150)
        plt.close(ax.figure)
        archivos.append(ruta)
    if "fuente_reputacion" in tablero:
        caba = tablero.loc[tablero["fuente_reputacion"].eq("https://insideairbnb.com/get-the-data/")]
        if not caba.empty:
            import pandas as pd
            fila = caba.iloc[0]
            conteos = pd.Series({"Positivas": fila["positivas"], "Negativas": fila["negativas"],
                                 "Mixtas o sin clasificar": fila["neutras"]})
            ax = conteos.plot(kind="bar", figsize=(8, 5), color=["#247d88", "#c75d4a", "#9a9a9a"])
            ax.set(title="Reseñas CABA: clasificación por palabras", xlabel="Resultado", ylabel="Comentarios")
            ax.tick_params(axis="x", rotation=15)
            ruta = carpeta / "reputacion.png"
            ax.figure.tight_layout()
            ax.figure.savefig(ruta, dpi=150)
            plt.close(ax.figure)
            archivos.append(ruta)
    return archivos
