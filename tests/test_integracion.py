"""Verifica flujo demo, fuentes, API y correo sin enviar a terceros."""
from email import policy
from email.parser import BytesParser
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch
import os
import unittest
import pandas as pd
import requests
from fastapi.testclient import TestClient
from plataforma_turistica.servicio import construir_tablero
from plataforma_turistica.clima import Clima, ErrorClima
from plataforma_turistica.eventos import extraer_eventos, demostrar_find_all
from plataforma_turistica.datos import preparar_demo
from plataforma_turistica.boletines import crear_boletin, guardar_boletin, enviar_boletin
from plataforma_turistica.practica_api import interpretar_pronostico, consultar_clima_autenticado, solicitar_analisis_post
from plataforma_turistica.visualizacion import generar_graficos
from plataforma_turistica.etl import exportar_resultados


class PruebasIntegracion(unittest.TestCase):
    def setUp(self):
        self.temporal = TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name)

    def demo(self):
        with patch("requests.sessions.Session.request", side_effect=AssertionError("Demo no debe usar red")):
            return construir_tablero(fecha="2026-11-16", carpeta_demo=self.raiz / "datos")

    def test_demo_destinos_separados(self):
        resultado = self.demo()
        tabla = resultado["tablero"].set_index("clave")
        self.assertEqual(tabla.loc["buenos aires", "eventos"], 2)
        self.assertEqual(tabla.loc["mendoza", "eventos"], 1)
        self.assertEqual(tabla.loc["mar del plata", "eventos"], 1)
        self.assertEqual(tabla.loc["buenos aires", "positivas"], 2)
        self.assertEqual(tabla.loc["mendoza", "positivas"], 1)
        esperado = (tabla.loc["mendoza", "ocupacion"] - 52) / 52 * 100
        self.assertAlmostEqual(tabla.loc["mendoza", "variacion"], round(esperado, 2))
        self.assertTrue(tabla["fuente_datos"].eq("demo académico").all())

    def test_graficos_exportaciones_y_adjuntos_reales(self):
        datos = self.demo()
        rutas = exportar_resultados(datos["tablero"], datos["eventos"], datos["historico"], self.raiz / "salida")
        graficos = generar_graficos(datos["tablero"], datos["historico"], self.raiz / "salida")
        self.assertEqual(len(graficos), 2)
        for grafico in graficos:
            self.assertEqual(grafico.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        mensaje = crear_boletin(datos["tablero"], rutas + graficos, [], "demo@example.com", ["prueba@example.com"])
        ruta = guardar_boletin(mensaje, self.raiz / "salida" / "boletin.eml")
        leido = BytesParser(policy=policy.default).parsebytes(ruta.read_bytes())
        self.assertEqual(len(list(leido.iter_attachments())), 7)
        self.assertIn("2026-11-16", leido["Subject"])
        self.assertIn("demo", leido.get_body(preferencelist=("plain",)).get_content().lower())

    def test_fallo_fuentes_no_inventa_resultados(self):
        with patch("plataforma_turistica.servicio.descargar_html", side_effect=requests.Timeout()), patch(
            "plataforma_turistica.servicio.consultar_clima", side_effect=ErrorClima("Clima no disponible")
        ):
            datos = construir_tablero(usar_red=True, carpeta_demo=self.raiz / "datos")
        self.assertTrue(datos["tablero"]["ocupacion"].isna().all())
        self.assertTrue(datos["tablero"]["clasificacion"].eq("datos insuficientes").all())
        self.assertTrue(datos["advertencias"])

    def test_agenda_buenos_aires_no_se_aplica_a_mendoza(self):
        carpeta = preparar_demo(self.raiz / "datos", pd.Timestamp.today().normalize())
        html = (carpeta / "eventos.html").read_text(encoding="utf-8")
        with patch("plataforma_turistica.servicio.descargar_html", return_value=html), patch(
            "plataforma_turistica.servicio.consultar_clima", return_value=Clima(20, 20, 0)
        ):
            datos = construir_tablero(["Mendoza"], usar_red=True, carpeta_demo=self.raiz / "datos2")
        self.assertEqual(datos["tablero"].iloc[0]["fuente_eventos"], "sin datos")
        self.assertTrue(pd.isna(datos["tablero"].iloc[0]["ocupacion"]))

    def test_scraping_atributos_y_busquedas(self):
        carpeta = preparar_demo(self.raiz / "datos", pd.Timestamp("2026-11-16"))
        html = (carpeta / "eventos.html").read_text(encoding="utf-8")
        eventos = extraer_eventos(html, "https://example.org/")
        self.assertEqual(len(eventos), 4)
        self.assertEqual(eventos[0].fecha, "2026-11-16")
        self.assertEqual(eventos[0].destino, "Buenos Aires")
        self.assertTrue(eventos[0].imagen)
        self.assertTrue(all(cantidad > 0 for cantidad in demostrar_find_all(html).values()))

    def test_json_xml_equivalentes(self):
        respuesta = Mock()
        respuesta.json.return_value = {"list": [{"main": {"temp": 21}, "pop": .3, "weather": [{"id": 500}]}]}
        respuesta.text = '<weatherdata><forecast><time><temperature value="21"/><precipitation probability="0.3"/><symbol number="500"/></time></forecast></weatherdata>'
        self.assertEqual(interpretar_pronostico(respuesta, "json"), interpretar_pronostico(respuesta, "xml"))

    def test_autenticacion_y_errores_no_exponen_clave(self):
        with patch.dict(os.environ, {"OPENWEATHER_API_KEY": ""}):
            with self.assertRaises(ErrorClima):
                consultar_clima_autenticado(0, 0)
        cliente = Mock()
        cliente.get.side_effect = requests.Timeout("clave-secreta")
        with patch.dict(os.environ, {"OPENWEATHER_API_KEY": "clave-secreta"}), patch("plataforma_turistica.practica_api.sleep"):
            with self.assertRaises(ErrorClima) as error:
                consultar_clima_autenticado(0, 0, session=cliente)
        self.assertNotIn("clave-secreta", str(error.exception))
        self.assertEqual(cliente.get.call_args.kwargs["params"]["appid"], "clave-secreta")

    def test_post_como_cliente(self):
        cliente = Mock()
        cliente.post.return_value.json.return_value = {"destino": "Mendoza"}
        self.assertEqual(solicitar_analisis_post("Mendoza", cliente)["destino"], "Mendoza")
        cliente.post.assert_called_once()
        self.assertEqual(cliente.post.call_args.kwargs["json"]["destino"], "Mendoza")

    def test_envio_smtp_local_controlado(self):
        datos = self.demo()
        mensaje = crear_boletin(datos["tablero"], [], [], "demo@example.com", ["prueba@example.com"])
        with patch.dict(os.environ, {"SMTP_MODE": "local", "SMTP_SERVER": "127.0.0.1", "SMTP_PORT": "1025"}), patch(
            "plataforma_turistica.boletines.smtplib.SMTP"
        ) as smtp:
            smtp.return_value.__enter__.return_value = smtp.return_value
            smtp.return_value.send_message.return_value = {}
            enviar_boletin(mensaje)
            smtp.return_value.send_message.assert_called_once_with(mensaje)

    def test_api_get_post_y_validacion(self):
        from plataforma_turistica.api import app
        cliente = TestClient(app)
        with patch("requests.sessions.Session.request", side_effect=AssertionError("No debe usar red")):
            get = cliente.get("/analisis/Mendoza")
            post = cliente.post("/analisis", json={"destino": "Mendoza"})
        self.assertEqual(get.status_code, 200)
        self.assertEqual(post.status_code, 200)
        self.assertEqual(get.json(), post.json())
        self.assertEqual(get.json()["eventos"], 1)
        self.assertEqual(cliente.post("/analisis", json={"destino": ""}).status_code, 422)


if __name__ == "__main__":
    unittest.main()
