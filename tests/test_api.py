"""Pruebas HTTP de la aplicación FastAPI sin iniciar un servidor real."""

import unittest

from fastapi.testclient import TestClient

from plataforma_turistica.api import app


class ApiTests(unittest.TestCase):
    """Comprueba status codes y cuerpos JSON de los endpoints públicos."""

    @classmethod
    def setUpClass(cls):
        """Crea un cliente en memoria compartido por los casos de prueba."""
        cls.cliente = TestClient(app)

    def test_salud(self):
        """La raíz debe responder 200 e indicar que el servicio está disponible."""
        respuesta = self.cliente.get("/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["estado"], "ok")

    def test_lista_destinos(self):
        """El catálogo debe incluir Buenos Aires y una cantidad coherente."""
        respuesta = self.cliente.get("/destinos")
        datos = respuesta.json()
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("Buenos Aires", datos["destinos"])
        self.assertEqual(datos["cantidad"], len(datos["destinos"]))

    def test_analisis_get(self):
        """GET devuelve un análisis JSON sin utilizar fuentes de red."""
        respuesta = self.cliente.get("/analisis/Buenos%20Aires")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["clasificacion"], "oportunidad")

    def test_analisis_post(self):
        """POST acepta destino y modo de ejecución dentro del cuerpo JSON."""
        respuesta = self.cliente.post(
            "/analisis", json={"destino": "Mendoza", "en_vivo": False}
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["destino"], "Mendoza")

    def test_destino_libre(self):
        """Un destino fuera del catálogo se acepta en modo demo."""
        respuesta = self.cliente.get("/analisis/Atlantida")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["destino"], "Atlantida")


if __name__ == "__main__":
    unittest.main()
