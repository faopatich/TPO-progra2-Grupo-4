# Requisitos del TPO y archivos relacionados

La consigna contiene conceptos que atraviesan varias partes del programa. Esta tabla indica dónde se puede estudiar y demostrar cada requisito; no supone que toda fuente externa o envío real haya sido verificado. Se agrupan funciones relacionadas en lugar de crear un archivo artificial por cada número.

| Requisito | Función solicitada | Archivos principales |
| --- | --- | --- |
| N01 | Proyecto modular | `main.py`, `servicio.py` y módulos de `plataforma_turistica/` |
| N02 | Cálculos turísticos con operadores | `indicadores.py`, `ocupacion.py`, `analisis.py` |
| N03 | Clasificaciones y reglas | `clasificacion.py`, `config.py`, `analisis.py` |
| N04 | Funciones de limpieza, fechas, clima e indicadores | `normalizacion.py`, `eventos.py`, `clima.py`, `indicadores.py` |
| N05 | Listas de destinos, URL, palabras y destinatarios; hoteles propios | `config.py`, `destinos.py`, `main.py`, `datos.py` |
| N06 | Diccionarios de destinos, coordenadas, API y criterios | `config.py`, `destinos.py` |
| N07 | Normalización de textos | `normalizacion.py`, `etl.py`, `reputacion.py` |
| N08 | Navegador, URL, DNS e IP | `docs/evidencia_web.md` |
| N09 | Inspección de etiquetas y atributos HTML | `docs/evidencia_web.md`, `eventos.py` (`inventario_html`) |
| N10 | Scraping con requests, BeautifulSoup y reglas | `eventos.py`, `agenda_servicio.py`, `agenda_nacional.py` |
| N11 | Valores y atributos de HTML | `eventos.py`, `datos/eventos_demo.html` |
| N12 | Distintas formas de `find_all` | `eventos.py` (`demostrar_find_all`) |
| N13 | API pública y distinción con API privada | `clima.py`, `config.py`, `docs/evidencia_web.md` |
| N14 | Consumo JSON y XML | `practica_api.py` |
| N15 | GET, POST y documentación de otros métodos | `clima.py`, `practica_api.py`, `api.py`, `README.md` |
| N16 | requests, HTTP, parámetros y errores | `clima.py`, `practica_api.py`, `eventos.py` |
| N17 | Autenticación con clave | `practica_api.py`, `.env.example` |
| N18 | Práctica de API pública con clave | `practica_api.py`, `README.md` (requiere clave propia para prueba real) |
| N19 | ETL desde fuentes web/API/archivo | `datos.py`, `eventos.py`, `clima.py`, `etl.py`, `referencias.py` |
| N20 | DataFrames, Series, tipos y nulos | `datos.py`, `etl.py`, `ocupacion.py` |
| N21 | Lectura y exportación de formatos | `datos.py`, `etl.py`, `ocupacion.py` |
| N22 | Agregaciones, fechas y uniones | `etl.py`, `referencias.py`, `ocupacion.py` |
| N23 | Visualización con Pandas | `visualizacion.py` |
| N24 | Mensajes, adjuntos y SMTP | `boletines.py`, `main.py`, `docs/correo.md` |
| N25 | Protocolos de correo y acceso a Gmail | `docs/correo.md`, `boletines.py` |

`servicio.py` coordina las etapas, `agenda_servicio.py` prepara la agenda, `referencias.py` integra la fuente de ocupación y `analisis.py` calcula cada fila. La disponibilidad de datos reales por destino, la validez estadística de la estimación, la clave de OpenWeatherMap y la entrega/programación real del correo deben verificarse por separado.
