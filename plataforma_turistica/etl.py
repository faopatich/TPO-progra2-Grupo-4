"""Limpieza, agregación, fechas y uniones con Pandas (N19-N22)."""
from dataclasses import asdict
from pathlib import Path
import pandas as pd
from .normalizacion import normalizar_texto, normalizar_comentario
from .reputacion import analizar_comentarios


def eventos_a_registros(eventos: list) -> list[dict]:
    return [asdict(evento) for evento in eventos]


def limpiar_tablas(tablas: dict) -> dict:
    """Normaliza claves, elimina duplicados y trata nulos según su significado."""
    limpias = {}
    for nombre, original in tablas.items():
        df = original.copy()
        df = df.dropna(subset=["destino"])
        df["clave"] = df["destino"].astype(str).apply(normalizar_texto)
        df = df.loc[df["clave"].ne("")].drop_duplicates()
        limpias[nombre] = df
    destinos = limpias["destinos"]
    destinos["destino"] = destinos["destino"].astype(str).str.strip()
    destinos["zona"] = destinos["zona"].fillna("No informada")
    for columna in ["latitud", "longitud", "ocupacion_base"]:
        destinos[columna] = pd.to_numeric(destinos[columna], errors="coerce")
    # Una ocupación imposible no se reemplaza por cero: se marca como faltante.
    destinos["ocupacion_base"] = destinos["ocupacion_base"].where(
        destinos["ocupacion_base"].between(0, 100)
    )
    limpias["destinos"] = destinos.drop_duplicates("clave")
    hoteles = limpias["hoteles"]
    hoteles["habitaciones"] = pd.to_numeric(hoteles["habitaciones"], errors="coerce")
    hoteles = hoteles.loc[hoteles["habitaciones"].ge(0)].copy()
    limpias["hoteles"] = hoteles.drop_duplicates(["clave", "hotel"])
    comentarios = limpias["comentarios"]
    comentarios["comentario"] = comentarios["comentario"].fillna("").apply(normalizar_comentario)
    limpias["comentarios"] = comentarios.loc[comentarios["comentario"].ne("")].drop_duplicates(
        ["clave", "comentario"]
    )
    historico = limpias["historico"]
    historico["fecha"] = pd.to_datetime(historico["fecha"], errors="coerce")
    historico["ocupacion"] = pd.to_numeric(historico["ocupacion"], errors="coerce")
    historico = historico.dropna(subset=["fecha", "ocupacion"])
    limpias["historico"] = historico.loc[historico["ocupacion"].between(0, 100)].drop_duplicates(
        ["clave", "fecha"], keep="last"
    )
    return limpias


def limpiar_eventos(registros: list[dict], inicio: pd.Timestamp) -> pd.DataFrame:
    """Convierte fechas ISO y conserva solo los eventos de la semana del informe."""
    columnas = ["destino", "titulo", "fecha", "fecha_fin", "direccion", "enlace", "imagen", "fuente"]
    df = pd.DataFrame(registros).reindex(columns=columnas)
    df = df.dropna(subset=["destino", "titulo"])
    df["clave"] = df["destino"].astype(str).apply(normalizar_texto)
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["fecha_fin"] = pd.to_datetime(df["fecha_fin"], errors="coerce").fillna(df["fecha"])
    fin = inicio + pd.Timedelta(days=7)
    df = df.loc[df["fecha"].lt(fin) & df["fecha_fin"].ge(inicio)]
    return df.drop_duplicates(["clave", "titulo", "fecha", "enlace"]).reset_index(drop=True)


def integrar_tablas(tablas: dict, eventos: pd.DataFrame, fecha: pd.Timestamp) -> pd.DataFrame:
    """merge une por clave; join agrega capacidad; concat se usa para el histórico."""
    destinos = tablas["destinos"].copy()
    cantidad = eventos.groupby("clave").size().rename("eventos").reset_index()
    tablero = destinos.merge(cantidad, on="clave", how="left", validate="one_to_one")
    tablero["eventos"] = tablero["eventos"].fillna(0).astype(int)
    capacidad = tablas["hoteles"].groupby("clave").agg(
        hoteles=("hotel", "nunique"), habitaciones=("habitaciones", "sum")
    )
    tablero = tablero.set_index("clave").join(capacidad, how="left").reset_index()
    tablero[["hoteles", "habitaciones"]] = tablero[["hoteles", "habitaciones"]].fillna(0)
    # Solo se compara con una observación anterior; sin base no se inventa variación.
    anteriores = tablas["historico"].loc[tablas["historico"]["fecha"].lt(fecha)]
    anteriores = anteriores.sort_values("fecha").groupby("clave").tail(1)
    anteriores = anteriores[["clave", "fecha", "ocupacion"]].rename(
        columns={"fecha": "fecha_anterior", "ocupacion": "ocupacion_anterior"}
    )
    return tablero.merge(anteriores, on="clave", how="left", validate="one_to_one")


def resumir_reputacion(comentarios: pd.DataFrame) -> dict:
    resultado = {}
    for clave, grupo in comentarios.groupby("clave"):
        resultado[clave] = analizar_comentarios(grupo["comentario"].tolist())
    return resultado


def combinar_historico(historico: pd.DataFrame, tablero: pd.DataFrame) -> pd.DataFrame:
    """Concatena períodos y reemplaza la misma fecha al repetir una ejecución."""
    actual = tablero[["clave", "destino", "fecha", "ocupacion"]]
    columnas = ["clave", "destino", "fecha", "ocupacion"]
    serie = pd.concat([historico.reindex(columns=columnas), actual], ignore_index=True)
    serie = serie.dropna(subset=["fecha", "ocupacion"])
    serie = serie.drop_duplicates(["clave", "fecha"], keep="last").sort_values(["clave", "fecha"])
    serie["anio"] = serie["fecha"].dt.year
    serie["mes"] = serie["fecha"].dt.month
    serie["dia"] = serie["fecha"].dt.day
    return serie.reset_index(drop=True)


def exportar_resultados(tablero, eventos, historico, carpeta: Path) -> list[Path]:
    """Exporta tablas limpias; Excel reúne tablero, detalle e histórico."""
    carpeta.mkdir(parents=True, exist_ok=True)
    csv = carpeta / "tablero.csv"
    excel = carpeta / "reporte.xlsx"
    json = carpeta / "tablero.json"
    detalle = carpeta / "eventos.csv"
    serie = carpeta / "historico.csv"
    tablero.to_csv(csv, index=False, encoding="utf-8-sig")
    tablero.to_json(json, orient="records", force_ascii=False, date_format="iso", indent=2)
    eventos.to_csv(detalle, index=False, encoding="utf-8-sig")
    historico.to_csv(serie, index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(excel, engine="openpyxl") as escritor:
        tablero.to_excel(escritor, sheet_name="Tablero", index=False)
        eventos.to_excel(escritor, sheet_name="Eventos", index=False)
        historico.to_excel(escritor, sheet_name="Historico", index=False)
    return [csv, excel, json, detalle, serie]
