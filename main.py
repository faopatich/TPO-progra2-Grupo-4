"""Entrada del proyecto: llama a los módulos y presenta sus resultados."""
import argparse
import os
from pathlib import Path
from dotenv import load_dotenv
from plataforma_turistica.datos import RAIZ
from plataforma_turistica.servicio import construir_tablero, inicio_semana
from plataforma_turistica.etl import exportar_resultados
from plataforma_turistica.visualizacion import generar_graficos
from plataforma_turistica.boletines import crear_boletin, guardar_boletin, enviar_boletin


def crear_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Análisis turístico modular — Taller de Programación II")
    parser.add_argument("--destino", help="Un destino; si se omite se analizan todos los del CSV")
    parser.add_argument("--fecha", help="Fecha ISO de la semana del informe, por ejemplo 2026-11-16")
    parser.add_argument("--en-vivo", action="store_true", help="Consultar eventos y clima reales")
    parser.add_argument("--proveedor", choices=["open-meteo", "openweathermap"], default="open-meteo")
    parser.add_argument("--datos", type=Path, help="Carpeta con CSV, Excel, JSON, ZIP y eventos.html propios")
    parser.add_argument("--salida", type=Path, default=RAIZ / "salida", help="Carpeta para reportes")
    parser.add_argument("--enviar", action="store_true", help="Enviar el boletín mediante SMTP configurado")
    parser.add_argument("--para", help="Destinatarios separados por coma; reemplaza EMAIL_RECEIVER")
    return parser


def main() -> None:
    load_dotenv(RAIZ / ".env")
    parser = crear_parser()
    opciones = parser.parse_args()
    try:
        semana = inicio_semana(opciones.fecha)
        carpeta = opciones.salida / semana.strftime("%Y-%m-%d")
        nombres = [opciones.destino] if opciones.destino else None
        # Cada módulo tiene una responsabilidad: analizar, exportar, graficar y correo.
        datos = construir_tablero(
            nombres, usar_red=opciones.en_vivo, fecha=semana, carpeta_datos=opciones.datos,
            carpeta_demo=opciones.salida / "entradas_demo", proveedor=opciones.proveedor,
        )
        archivos = exportar_resultados(datos["tablero"], datos["eventos"], datos["historico"], carpeta)
        graficos = generar_graficos(datos["tablero"], datos["historico"], carpeta)
        remitente = os.getenv("EMAIL_USER") or "demo@example.com"
        texto_destinatarios = opciones.para or os.getenv("EMAIL_RECEIVER") or "equipo.turismo@example.com"
        destinatarios = [email.strip() for email in texto_destinatarios.split(",") if email.strip()]
        mensaje = crear_boletin(datos["tablero"], archivos + graficos, datos["advertencias"],
                                remitente, destinatarios)
        guardar_boletin(mensaje, carpeta / "boletin.eml")
        print(datos["tablero"][["destino", "eventos", "ocupacion", "variacion", "clasificacion"]].to_string(index=False))
        for aviso in datos["advertencias"]:
            print(f"Aviso: {aviso}")
        print(f"Reportes, gráficos y boletín: {carpeta}")
        if opciones.enviar:
            if not opciones.para and not os.getenv("EMAIL_RECEIVER"):
                raise ValueError("Para enviar, configure EMAIL_RECEIVER o --para")
            if not os.getenv("EMAIL_USER"):
                raise ValueError("Para enviar, configure EMAIL_USER")
            enviar_boletin(mensaje)
            print("Boletín enviado.")
        else:
            print("Boletín guardado para revisión. Use --enviar con SMTP configurado.")
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
