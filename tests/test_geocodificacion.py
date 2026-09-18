"""Pruebas del cliente de geocodificación sin utilizar internet."""

import unittest
from unittest.mock import Mock

from plataforma_turistica.geocodificacion import geocodificar_destino


class GeocodificacionTests(unittest.TestCase):
    def test_convierte_resultado_en_coordenadas(self):
        sesion = Mock()
        respuesta = Mock()
        respuesta.json.return_value = {
            "results": [{"latitude": -41.13, "longitude": -71.31}]
        }
        sesion.get.return_value = respuesta

        coordenadas = geocodificar_destino("Bariloche", session=sesion)

        self.assertEqual(coordenadas.latitud, -41.13)
        self.assertEqual(coordenadas.longitud, -71.31)
        sesion.get.assert_called_once()


if __name__ == "__main__":
    unittest.main()
