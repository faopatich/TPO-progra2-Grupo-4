"""Entrada del proyecto: llama a los módulos y presenta sus resultados."""
import argparse
import os
from pathlib import Path
from dotenv import load_dotenv
from plataforma_turistica.datos import RAIZ
from plataforma_turistica.servicio import construir_tablero, inicio_semana, crear_carpeta_salida
from plataforma_turistica.etl import exportar_resultados
from plataforma_turistica.visualizacion import generar_graficos
from plataforma_turistica.boletines import crear_boletin, guardar_boletin, enviar_boletin


def crear_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Análisis turístico modular — Taller de Programación II")
    parser.add_argument("--destino", help="Un destino; si se omite se analizan todos los del CSV")
    parser.add_argument("--fecha", help="Fecha ISO de la semana del informe, por ejemplo 2026-11-16")
    parser.add_argument("--sin-red", dest="en_vivo", action="store_false", help="No consultar fuentes en línea; se indicará falta de datos")
    parser.add_argument("--proveedor", choices=["open-meteo", "openweathermap"], default="open-meteo")
    parser.add_argument("--datos", type=Path, help="Carpeta con CSV, Excel, JSON, ZIP y eventos.html propios")
    parser.add_argument("--salida", type=Path, default=RAIZ / "salida", help="Carpeta para reportes")
    parser.add_argument("--sin-enviar", dest="enviar", action="store_false",
                       help="Generar los reportes sin enviar correos")
    parser.add_argument("--para", help="Destinatarios separados por coma; reemplaza EMAIL_RECEIVER")
    return parser


def main() -> None:
    load_dotenv(RAIZ / ".env")
    parser = crear_parser()
    opciones = parser.parse_args()
    try:
        remitente = os.getenv("EMAIL_USER", "").strip()
        texto_destinatarios = opciones.para or os.getenv("EMAIL_RECEIVER", "")
        destinatarios = [email.strip() for email in texto_destinatarios.split(",") if email.strip()]
        if opciones.enviar and not remitente:
            raise ValueError("Para enviar, configure EMAIL_USER en .env")
        if opciones.enviar and not destinatarios:
            raise ValueError("Para enviar, configure EMAIL_RECEIVER en .env o use --para")
        semana = inicio_semana(opciones.fecha)
        nombres = [opciones.destino] if opciones.destino else None
        # Cada módulo tiene una responsabilidad: analizar, exportar, graficar y correo.
        datos = construir_tablero(
            nombres, usar_red=opciones.en_vivo, fecha=semana, carpeta_datos=opciones.datos,
            proveedor=opciones.proveedor,
        )
        carpeta = crear_carpeta_salida(opciones.salida, semana)
        archivos = exportar_resultados(datos["tablero"], datos["eventos"], datos["historico"], carpeta)
        graficos = generar_graficos(datos["tablero"], datos["historico"], carpeta)
        mensaje = None
        if remitente and destinatarios:
            mensaje = crear_boletin(datos["tablero"], archivos + graficos, datos["advertencias"],
                                    remitente, destinatarios)
            guardar_boletin(mensaje, carpeta / "boletin.eml")
        print(datos["tablero"][["destino", "ocupacion_base", "periodo_ocupacion", "eventos", "ocupacion", "variacion", "clasificacion"]].to_string(index=False))
        for _, fila in datos["tablero"].iterrows():
            if fila.get("fuente_reputacion") == "https://insideairbnb.com/get-the-data/":
                print(f"Reseñas de {fila['destino']} ({fila['periodo_reputacion']}): "
                      f"{int(fila['total_resenas'])} analizadas; positivas {int(fila['positivas'])}, "
                      f"negativas {int(fila['negativas'])}, mixtas o sin clasificar {int(fila['neutras'])}; "
                      f"menciones turísticas {int(fila['menciones_resenas'])}.")
            if fila["advertencias"]:
                print(f"Aviso {fila['destino']}: {fila['advertencias']}")
        for aviso in datos["advertencias"]:
            print(f"Aviso: {aviso}")
        print(f"Reportes y gráficos: {carpeta}")
        if opciones.enviar:
            enviar_boletin(mensaje)
            print("Boletín enviado.")
        elif mensaje:
            print("Boletín guardado para revisión; no se envió.")
        else:
            print("Para generar el boletín, configure EMAIL_USER y EMAIL_RECEIVER o --para.")
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
