"""Listas y diccionarios de configuración del proyecto (N05 y N06)."""

# La clave normalizada permite buscar sin depender de mayúsculas o acentos; cada
# valor agrupa la información relacionada con ese destino.
DESTINOS = {
    "buenos aires": {
        "nombre": "Buenos Aires",
        "coordenadas": {"latitud": -34.6037, "longitud": -58.3816},
        "zona": "Centro",
    },
    "mar del plata": {
        "nombre": "Mar del Plata",
        "coordenadas": {"latitud": -38.0055, "longitud": -57.5426},
        "zona": "Costa Atlántica",
    },
    "mendoza": {
        "nombre": "Mendoza",
        "coordenadas": {"latitud": -32.8895, "longitud": -68.8458},
        "zona": "Cuyo",
    },
}

# Estas colecciones centralizan datos que podrían cambiar. Así no quedan URLs,
# palabras repetidas dentro de la lógica.
URLS_EVENTOS = [
    "https://turismo.buenosaires.gob.ar/es/article/que-hacer-esta-semana",
]
# La URL privada es ficticia y solo sirve para la comparación académica de N13.
ENDPOINTS_API = {
    "clima_publica": "https://api.open-meteo.com/v1/forecast",
    "geocodificacion_publica": "https://geocoding-api.open-meteo.com/v1/search",
    "reservas_privada_ejemplo": "https://api.interna.example/reservas",
}
PALABRAS_CLAVE = ["festival", "feria", "museo", "gastronomía", "tango"]

# Umbrales usados por clasificacion.py. Se pueden ajustar sin reescribir los if.
CRITERIOS_RECOMENDACION = {
    "alta_demanda": {"ocupacion_minima": 75, "variacion_minima": 15},
    "riesgo_climatico": {"probabilidad_lluvia_minima": 70},
    "oportunidad": {"ocupacion_minima": 50, "menciones_minimas": 3},
}

# Solo Buenos Aires tiene una fuente web configurada. No se reutiliza en otras ciudades.
FUENTES_EVENTOS = {"buenos aires": URLS_EVENTOS[0]}
