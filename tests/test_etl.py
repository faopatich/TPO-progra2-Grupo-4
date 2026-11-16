"""Verifica limpieza y archivos usando Pandas y Excel reales."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import pandas as pd
from plataforma_turistica.datos import cargar_archivos, preparar_demo
from plataforma_turistica.etl import (limpiar_tablas, limpiar_eventos, integrar_tablas,
                                     combinar_historico, exportar_resultados)


class PruebasETL(unittest.TestCase):
    def setUp(self):
        self.temporal = TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name)
        self.fecha = pd.Timestamp("2026-11-16")
        preparar_demo(self.raiz / "datos", self.fecha)
        self.tablas = limpiar_tablas(cargar_archivos(self.raiz / "datos"))

    def eventos(self):
        return limpiar_eventos([
            {"destino": "Buenos Aires", "titulo": "Tango", "fecha": "2026-11-16"},
            {"destino": "Mendoza", "titulo": "Feria", "fecha": "2026-11-19"},
            {"destino": "Mendoza", "titulo": "Feria", "fecha": "2026-11-19"},
            {"destino": "Mendoza", "titulo": "Inválido", "fecha": "sin fecha"},
            {"destino": "Mendoza", "titulo": "Anterior", "fecha": "2026-11-15"},
        ], self.fecha)

    def test_formatos_y_limpieza(self):
        self.assertEqual(len(self.tablas["destinos"]), 3)
        self.assertEqual(len(self.tablas["historico"]), 6)
        self.assertFalse(self.tablas["comentarios"]["comentario"].eq("").any())
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(self.tablas["historico"]["fecha"]))

    def test_uniones_por_destino_y_fechas(self):
        eventos = self.eventos()
        self.assertEqual(len(eventos), 2)
        tabla = integrar_tablas(self.tablas, eventos, self.fecha).set_index("clave")
        self.assertEqual(tabla.loc["mendoza", "eventos"], 1)
        self.assertEqual(tabla.loc["mar del plata", "eventos"], 0)
        self.assertEqual(tabla.loc["buenos aires", "habitaciones"], 100)
        self.assertEqual(tabla.loc["mendoza", "ocupacion_anterior"], 52)
        self.assertTrue(tabla["fecha_anterior"].lt(self.fecha).all())

    def test_sin_historial_no_inventa_cero(self):
        self.tablas["historico"] = self.tablas["historico"].iloc[0:0]
        tabla = integrar_tablas(self.tablas, self.eventos(), self.fecha)
        self.assertTrue(tabla["ocupacion_anterior"].isna().all())

    def test_concat_exportacion_y_repeticion(self):
        tabla = integrar_tablas(self.tablas, self.eventos(), self.fecha)
        tabla["fecha"] = self.fecha
        tabla["ocupacion"] = [60., 46., 53.]
        historia = combinar_historico(self.tablas["historico"], tabla)
        repetida = combinar_historico(historia, tabla)
        self.assertEqual(len(historia), 9)
        self.assertEqual(len(repetida), 9)
        rutas = exportar_resultados(tabla, self.eventos(), historia, self.raiz / "salida")
        self.assertTrue(all(ruta.stat().st_size > 0 for ruta in rutas))
        self.assertEqual(len(pd.read_csv(rutas[0])), 3)
        self.assertEqual(len(pd.read_json(rutas[2])), 3)
        with pd.ExcelFile(rutas[1]) as libro:
            self.assertEqual(libro.sheet_names, ["Tablero", "Eventos", "Historico"])

    def test_ocupacion_fuera_de_rango_no_se_convierte_en_cero(self):
        originales = cargar_archivos(self.raiz / "datos")
        originales["destinos"].loc[0, "ocupacion_base"] = 200
        limpias = limpiar_tablas(originales)
        self.assertTrue(pd.isna(limpias["destinos"].iloc[0]["ocupacion_base"]))


if __name__ == "__main__":
    unittest.main()
