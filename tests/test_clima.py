import unittest

from plataforma_turistica.clima import consultar_clima


class RespuestaFalsa:
    """Imita la parte de requests.Response que utiliza consultar_clima."""

    def raise_for_status(self):
        """Simula un estado HTTP exitoso, por eso no lanza excepciones."""
        return None

    def json(self):
        """Entrega un JSON controlado con la estructura de Open-Meteo."""
        return {
            "current": {"temperature_2m": 21.5, "weather_code": 1},
            "daily": {"precipitation_probability_max": [35]},
        }


class SesionFalsa:
    """Sustituye la sesión de red para probar sin conectarse a Internet."""

    def get(self, url, params, timeout):
        """Guarda los argumentos y devuelve la respuesta simulada."""
        self.url = url
        self.params = params
        self.timeout = timeout
        return RespuestaFalsa()


class ClimaTests(unittest.TestCase):
    """Pruebas de conversión y configuración del cliente meteorológico."""

    def test_convierte_json_de_api(self):
        """Comprueba datos convertidos y que se utilice un timeout de 10 s."""
        sesion = SesionFalsa()
        clima = consultar_clima(-34.6, -58.4, session=sesion)
        self.assertEqual(clima.temperatura, 21.5)
        self.assertEqual(clima.probabilidad_lluvia, 35)
        self.assertEqual(sesion.timeout, 10)


if __name__ == "__main__":
    unittest.main()
