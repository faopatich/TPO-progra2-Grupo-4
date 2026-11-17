"""EmailMessage, adjuntos y envío SMTP (N24-N25)."""
from email.message import EmailMessage
from email.utils import parseaddr
from pathlib import Path
import mimetypes
import os
import smtplib
import ssl
from html import escape
import pandas as pd


def validar_email(direccion: str) -> str:
    """Validación básica de formato; no comprueba que la casilla exista."""
    direccion = direccion.strip()
    nombre, correo = parseaddr(direccion)
    if (nombre or correo != direccion or "\n" in direccion or "\r" in direccion
            or direccion.count("@") != 1 or " " in direccion):
        raise ValueError("Dirección de correo inválida")
    usuario, dominio = direccion.split("@")
    if not usuario or "." not in dominio or dominio.startswith(".") or dominio.endswith("."):
        raise ValueError("Dirección de correo inválida")
    return direccion


def crear_boletin(tablero, adjuntos: list[Path], advertencias: list[str],
                  remitente: str, destinatarios: list[str]) -> EmailMessage:
    """Crea el mensaje completo; no hace ninguna conexión de red."""
    if not destinatarios:
        raise ValueError("Configure al menos un destinatario")
    mensaje = EmailMessage()
    mensaje["From"] = validar_email(remitente)
    mensaje["To"] = ", ".join(validar_email(email) for email in destinatarios)
    semana = tablero["fecha"].iloc[0].strftime("%Y-%m-%d")
    mensaje["Subject"] = f"Boletín turístico semanal — {semana}"
    lineas = [f"Resumen de la semana desde {semana}",
              "Indicadores académicos; la no disponibilidad puede incluir reservas y bloqueos. Detalle en los adjuntos.", ""]
    partes_html = [f"<h2>Resumen turístico semanal</h2><p>Semana desde {semana}</p>",
                   "<p>Indicadores académicos; la no disponibilidad puede incluir reservas y bloqueos. Detalle en los archivos adjuntos.</p>"]
    for _, fila in tablero.iterrows():
        def mostrar(valor, sufijo=""):
            if pd.isna(valor):
                return "Sin datos"
            return f"{valor:g}{sufijo}" if isinstance(valor, (int, float)) else f"{valor}{sufijo}"

        fuente = str(fila.get("fuente_ocupacion", ""))
        if "insideairbnb" in fuente:
            captura = fila.get("captura_ocupacion")
            referencia = "No disponibilidad Airbnb" + (f" (captura {captura})" if pd.notna(captura) else "")
        else:
            periodo = fila.get("periodo_ocupacion")
            referencia = "Referencia histórica" + (f" ({periodo})" if pd.notna(periodo) and periodo not in ("sin datos", "no especificado") else "")
        datos = [
            (referencia, mostrar(fila["ocupacion_base"], "%")),
            ("Eventos encontrados", mostrar(fila["eventos"])),
            ("Probabilidad de lluvia", mostrar(fila["lluvia"], "%")),
            ("Indicador estimado", mostrar(fila["ocupacion"], "%")),
            ("Variación de la referencia", mostrar(fila["variacion"], "%")),
            ("Menciones turísticas", mostrar(fila["menciones"])),
            ("Clasificación", mostrar(fila["clasificacion"])),
        ]
        lineas.append(str(fila["destino"]))
        lineas.extend(f"{nombre}: {valor}" for nombre, valor in datos)
        lineas.append(f"Acción recomendada: {fila['recomendacion']}")
        lineas.append("")
        partes_html.append(f"<h3>{escape(str(fila['destino']))}</h3>")
        partes_html.append('<table style="border-collapse:collapse">')
        for nombre, valor in datos:
            partes_html.append(f'<tr><th style="text-align:left;padding:4px 16px 4px 0">{escape(nombre)}</th><td>{escape(valor)}</td></tr>')
        partes_html.append('</table>')
        partes_html.append(f"<p><strong>Acción recomendada:</strong> {escape(str(fila['recomendacion']))}</p>")
    mensaje.set_content("\n".join(lineas))
    mensaje.add_alternative("".join(partes_html), subtype="html")
    for ruta in adjuntos:
        tipo = mimetypes.guess_type(ruta.name)[0] or "application/octet-stream"
        principal, subtipo = tipo.split("/", 1)
        mensaje.add_attachment(ruta.read_bytes(), maintype=principal, subtype=subtipo, filename=ruta.name)
    return mensaje


def guardar_boletin(mensaje: EmailMessage, ruta: Path) -> Path:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(mensaje.as_bytes())
    return ruta


def enviar_boletin(mensaje: EmailMessage) -> None:
    """SSL para Gmail; STARTTLS o SMTP local según las variables de entorno."""
    host = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    modo = os.getenv("SMTP_MODE", "ssl").lower()
    puerto = int(os.getenv("SMTP_PORT", "465" if modo == "ssl" else "587"))
    usuario = os.getenv("EMAIL_USER", "")
    clave = os.getenv("EMAIL_PASSWORD", "")
    if modo not in {"ssl", "starttls", "local"}:
        raise ValueError("SMTP_MODE debe ser ssl, starttls o local")
    if modo == "local" and host not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("El modo local solo admite un servidor de esta computadora")
    if modo != "local" and (not usuario or not clave):
        raise ValueError("Configure EMAIL_USER y EMAIL_PASSWORD para enviar")
    contexto = ssl.create_default_context()
    try:
        if modo == "ssl":
            servidor = smtplib.SMTP_SSL(host, puerto, timeout=15, context=contexto)
        else:
            servidor = smtplib.SMTP(host, puerto, timeout=15)
        with servidor:
            if modo == "starttls":
                servidor.starttls(context=contexto)
            if modo != "local":
                servidor.login(usuario, clave)
            rechazados = servidor.send_message(mensaje)
            if rechazados:
                raise ValueError("El servidor rechazó uno o más destinatarios")
    except (smtplib.SMTPException, OSError):
        # No se incluyen credenciales ni respuestas remotas en el error público.
        raise ValueError("No se pudo enviar el correo; revise la configuración SMTP") from None
