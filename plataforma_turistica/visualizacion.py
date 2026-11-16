"""Gráficos básicos con DataFrame.plot y Series.plot (N23)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # Guarda PNG sin abrir ventanas, también desde la API.
import matplotlib.pyplot as plt


def barra_textual(valor: float, maximo: float = 100, ancho: int = 20) -> str:
    proporcion = 0 if maximo <= 0 else max(0.0, min(1.0, valor / maximo))
    llenos = round(proporcion * ancho)
    return "#" * llenos + "-" * (ancho - llenos)


def generar_graficos(tablero, historico, carpeta: Path) -> list[Path]:
    """Barras comparan destinos; líneas muestran períodos comparables."""
    carpeta.mkdir(parents=True, exist_ok=True)
    archivos = []
    ocupacion = tablero.set_index("destino")["ocupacion"].dropna()
    if not ocupacion.empty:
        ax = ocupacion.plot(kind="bar", figsize=(8, 5), color="#247d88", ylim=(0, 100))
        ax.set(title="Ocupación estimada — modelo académico", xlabel="Destino", ylabel="Ocupación (%)")
        ax.tick_params(axis="x", rotation=20)
        ruta = carpeta / "ocupacion.png"
        ax.figure.tight_layout()
        ax.figure.savefig(ruta, dpi=150)
        plt.close(ax.figure)
        archivos.append(ruta)
    if not historico.empty:
        tabla = historico.pivot_table(index="fecha", columns="destino", values="ocupacion", aggfunc="mean")
        ax = tabla.plot(kind="line", marker="o", figsize=(8, 5), ylim=(0, 100))
        ax.set(title="Histórico y estimación actual — revisar fuentes del reporte",
               xlabel="Fecha", ylabel="Ocupación (%)")
        ruta = carpeta / "tendencia.png"
        ax.figure.tight_layout()
        ax.figure.savefig(ruta, dpi=150)
        plt.close(ax.figure)
        archivos.append(ruta)
    return archivos
