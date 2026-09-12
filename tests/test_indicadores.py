import unittest

from plataforma_turistica.clasificacion import clasificar_destino
from plataforma_turistica.indicadores import (
    calcular_ocupacion_estimada,
    calcular_variacion_demanda,
    contar_menciones,
)


class IndicadoresTests(unittest.TestCase):
    """Casos límite de fórmulas, menciones y reglas de clasificación."""

    def test_ocupacion_permanece_entre_cero_y_cien(self):
        """Comprueba los límites superior e inferior de la estimación."""
        self.assertEqual(calcular_ocupacion_estimada(99, 20, 10, 0, 0), 100)
        self.assertEqual(calcular_ocupacion_estimada(0, 0, 0, 10, 100), 0)

    def test_variacion_controla_division_por_cero(self):
        """Evita que una base histórica igual a cero rompa el programa."""
        self.assertEqual(calcular_variacion_demanda(25, 0), 0)

    def test_menciones_ignoran_acentos_y_mayusculas(self):
        """Verifica la normalización y el conteo único por texto."""
        textos = ["Gran FERIA gastronómica", "Sin coincidencias"]
        self.assertEqual(contar_menciones(textos, ["gastronomia", "feria"]), 1)

    def test_riesgo_climatico_tiene_prioridad(self):
        """Confirma que lluvia alta prevalezca aunque exista demanda alta."""
        self.assertEqual(clasificar_destino(90, 30, 10, 80), "riesgo climático")


if __name__ == "__main__":
    unittest.main()
