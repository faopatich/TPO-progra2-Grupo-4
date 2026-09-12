import unittest
from pathlib import Path

from plataforma_turistica.eventos import demostrar_find_all, extraer_eventos, inventario_html

# La ruta se calcula desde el test para que funcione desde cualquier terminal.
ARCHIVO = Path(__file__).resolve().parent.parent / "datos" / "eventos_demo.html"


class EventosTests(unittest.TestCase):
    """Pruebas del parseo, los atributos y las búsquedas BeautifulSoup."""

    @classmethod
    def setUpClass(cls):
        """Lee el HTML una vez y lo comparte entre todas las pruebas de la clase."""
        cls.html = ARCHIVO.read_text(encoding="utf-8")

    def test_extrae_texto_y_atributos(self):
        """Verifica cantidad, título, URL absoluta y atributo data-* extraído."""
        eventos = extraer_eventos(self.html, "https://turismo.buenosaires.gob.ar")
        self.assertEqual(len(eventos), 2)
        self.assertEqual(eventos[0].titulo, "Festival de Tango")
        self.assertTrue(eventos[0].enlace.endswith("/es/evento/festival-tango"))
        self.assertEqual(eventos[0].datos_html["data-tipo"], "cultural")

    def test_find_all_cubre_todos_los_criterios(self):
        """Exige al menos una coincidencia para cada variante pedida en N12."""
        conteos = demostrar_find_all(self.html)
        self.assertTrue(all(valor > 0 for valor in conteos.values()))

    def test_inventario_incluye_etiquetas_solicitadas(self):
        """Comprueba que el inventario cuenta tablas e imágenes correctamente."""
        inventario = inventario_html(self.html)
        self.assertEqual(inventario["table"], 1)
        self.assertEqual(inventario["img"], 2)


if __name__ == "__main__":
    unittest.main()
