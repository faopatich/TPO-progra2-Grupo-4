# Plataforma de análisis turístico

Entrega modular del Trabajo Práctico de Programación II, implementada hasta la funcionalidad N13.

## Puesta en marcha

```powershell
cd C:\Users\andre\Desktop\ejercicios_python\TPO
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

La ejecución normal usa `datos/eventos_demo.html`, por lo que es reproducible sin internet. Para intentar la agenda oficial y Open-Meteo:

```powershell
python main.py --en-vivo --destino "Buenos Aires"
```

Si una fuente externa falla, el programa muestra un aviso y conserva la demostración local.

## API HTTP y Postman

Iniciar el servidor desde la raíz del proyecto:

```powershell
uvicorn plataforma_turistica.api:app --reload
```

La API queda disponible en `http://127.0.0.1:8000`. FastAPI publica una interfaz
interactiva en `http://127.0.0.1:8000/docs` y el contrato OpenAPI en
`http://127.0.0.1:8000/openapi.json`.

Endpoints para Postman:

| Método | URL | Función |
| --- | --- | --- |
| GET | `http://127.0.0.1:8000/` | comprobar el estado de la API |
| GET | `http://127.0.0.1:8000/destinos` | listar destinos configurados |
| GET | `http://127.0.0.1:8000/analisis/Buenos%20Aires` | analizar mediante parámetros de URL |
| GET | `http://127.0.0.1:8000/analisis/Buenos%20Aires?en_vivo=true` | intentar fuentes externas |
| POST | `http://127.0.0.1:8000/analisis` | analizar mediante un cuerpo JSON |

Cuerpo para el POST:

```json
{
  "destino": "Mendoza",
  "en_vivo": false
}
```

## Pruebas

```powershell
python -m unittest discover -v
```

## Arquitectura

- `main.py`: interfaz de consola.
- `api.py`: endpoints FastAPI para Postman y documentación OpenAPI.
- `esquemas.py`: contratos Pydantic de entrada y salida.
- `servicio.py`: coordina el caso de uso.
- `config.py` y `destinos.py`: listas, diccionarios y destinos.
- `normalizacion.py`: cadenas y limpieza.
- `indicadores.py`: ocupación, demanda, menciones y prioridad.
- `clasificacion.py`: reglas y recomendaciones.
- `eventos.py`: `requests`, BeautifulSoup, robots.txt, frecuencia, atributos y variantes de `find_all`.
- `clima.py`: cliente GET de Open-Meteo y parseo JSON.
- `reputacion.py`: conteo básico de opinión.
- `etl.py`, `visualizacion.py` y `boletines.py`: límites de módulos previstos por N01; su ampliación con Pandas, gráficos y SMTP pertenece a N19-N24.

## Trazabilidad N01-N13

| Necesidad | Evidencia principal |
| --- | --- |
| N01 | paquete `plataforma_turistica` con módulos separados |
| N02 | `indicadores.py` |
| N03 | `clasificacion.py` |
| N04 | `normalizacion.py`, `eventos.extraer_fecha`, `clima.consultar_clima`, `indicadores.py` |
| N05 | listas de `config.py` |
| N06 | diccionarios de destinos, endpoints y criterios en `config.py` |
| N07 | funciones de cadenas en `normalizacion.py` |
| N08 | `docs/evidencia_web.md` y `web_info.py` |
| N09 | inventario de etiquetas en `eventos.inventario_html` y documentación |
| N10 | `eventos.descargar_html` |
| N11 | dataclass `Evento` y `eventos.extraer_eventos` |
| N12 | `eventos.demostrar_find_all` y sus pruebas |
| N13 | `clima.py` y comparación pública/privada en la documentación |

## Decisiones académicas

El código aplica los contenidos de las clases: operadores, `if/elif/else`, bucles, funciones, módulos, listas, diccionarios, cadenas, cliente-servidor, URL, GET, JSON, códigos HTTP, `timeout`, errores y separación de responsabilidades. No incluye credenciales. Las etapas posteriores a N13 están delimitadas para no presentar como terminadas funciones que todavía pertenecen a N14-N25.

Fuentes externas de la integración:

- Documentación de Open-Meteo: <https://open-meteo.com/en/docs>
- Agenda oficial: <https://turismo.buenosaires.gob.ar/es/categoria-general/eventos2026>
- Términos del GCBA: <https://buenosaires.gob.ar/gcaba_historico/terminos-y-condiciones>
# TPO-progra2
