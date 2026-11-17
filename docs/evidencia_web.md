# Evidencia web para N08 y N09

## Fuente actual de eventos

- URL inspeccionada: https://turismo.buenosaires.gob.ar/es/article/que-hacer-esta-semana
- Protocolo: HTTPS. Dominio DNS: `turismo.buenosaires.gob.ar`.
- Resolución DNS IPv4 realizada el 16/11/2026: `200.16.89.208`. Puede cambiar.
- El 16/11/2026 se consultó el HTML con `requests` y se revisó su estructura con BeautifulSoup. Se observaron `html`, `head`, `body`, `div`, `a`, `img`, `span` y `script`; no se observaron tablas `table`, `tr` ni `td` en esa respuesta. Se observaron enlaces con `href` e imágenes con `src`.
- La agenda de esta página incorpora la lista de actividades como JSON dentro de un `script`. El programa identifica ese contenido y obtiene título, fecha de inicio, dirección, enlace e imagen. CABA cuenta solo eventos con fecha de inicio en la semana; pueden faltar los ya iniciados.
- `eventos.descargar_html` consulta `robots.txt`, identifica el agente y espera antes de solicitar la página. Si la página o las reglas no permiten obtenerla, el programa informa datos no disponibles; no sustituye eventos reales por demo.

**Pendiente académico:** completar la inspección manual en el navegador que use el equipo (por ejemplo, Edge o Chrome, herramientas de desarrollador), registrar el navegador y guardar la evidencia. Si una etiqueta no existe en la página, indicarlo; no atribuir al sitio los elementos de `datos/eventos_demo.html`. La IP y el HTML pueden cambiar.

## Búsquedas HTML de la materia

`eventos.inventario_html` cuenta etiquetas. `eventos.demostrar_find_all` muestra búsquedas por etiqueta, clase, id, atributo, texto, función y criterios combinados. `datos/eventos_demo.html` es una reproducción académica y no una captura del sitio oficial.

Para ejecutar ambas prácticas desde la carpeta del proyecto (PowerShell):

```powershell
.\.venv\Scripts\python.exe -c "from pathlib import Path; from plataforma_turistica.eventos import inventario_html, demostrar_find_all; html = Path('datos/eventos_demo.html').read_text(encoding='utf-8'); print('Etiquetas:', inventario_html(html)); print('Búsquedas:', demostrar_find_all(html))"
```

Este archivo de ejemplo sirve únicamente para practicar; no representa eventos reales.

## Otras localidades

La página nacional https://www.argentina.gob.ar/jefatura/turismo-y-ambiente/turismo/fiestas-y-eventos-de-argentina carga una planilla pública. `agenda_nacional.py` obtiene el CSV con `requests` y Pandas, filtra localidad y fecha, e identifica la fuente. Es una agenda parcial y no implica que no existan otros eventos. No se presenta esta consulta CSV como web scraping HTML.

## API pública y privada

Open-Meteo es la API pública para clima. Una API privada o interna está limitada a clientes autorizados y puede exigir token, VPN y permisos. La URL interna de `config.py` es ficticia y solo ilustra la diferencia; no se consulta.
