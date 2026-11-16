# Plataforma de análisis turístico — TPO Programación II

Implementa la solicitud 4 mediante Python, requests, BeautifulSoup, Pandas, gráficos con .plot() y correo con smtplib y EmailMessage.

## Ejecutar

Requiere Python 3.11 o superior. Abrir una terminal en la carpeta del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

El modo predeterminado es una demostración reproducible y no usa Internet ni envía correos. Procesa los tres destinos. Los eventos, hoteles, comentarios, ocupación histórica y clima demo son ejemplos académicos, no datos reales.

```powershell
python main.py --destino "Mendoza"
python main.py --fecha 2026-11-16
python main.py --en-vivo --destino "Buenos Aires"
```

La fecha selecciona la semana de lunes a domingo. Los eventos fuera de ella se excluyen. En vivo solo se admite la semana actual porque se consulta un pronóstico actual, no clima histórico. El riesgo climático usa la probabilidad consultada, no un pronóstico de toda la semana.

## Modularización

`main.py` lee argumentos y llama a los módulos. La API reutiliza el servicio:

| Archivo | Responsabilidad |
| --- | --- |
| main.py | Coordina análisis, exportación, gráficos y boletín |
| servicio.py | Combina las fuentes y calcula una fila por destino |
| datos.py | Prepara ejemplos identificados y lee CSV, Excel, JSON y ZIP |
| eventos.py | Descarga HTML permitido y extrae texto, fechas y atributos |
| clima.py / geocodificacion.py | Consultas GET a Open-Meteo |
| practica_api.py | GET con clave, JSON/XML y POST como cliente local |
| normalizacion.py / reputacion.py | Limpieza y conteo básico de opinión |
| indicadores.py / clasificacion.py | Fórmulas y reglas de recomendación |
| etl.py | Pandas: nulos, tipos, fechas, agrupación, merge, join, concat y exportación |
| visualizacion.py | Barras y líneas con Series.plot y DataFrame.plot |
| boletines.py | Validación básica de emails, EmailMessage, adjuntos, archivo EML y SMTP |
| config.py / destinos.py | Catálogo, palabras clave, fuentes y criterios |
| api.py / esquemas.py | Rutas FastAPI y validación de entradas/salidas |

## Resultados

En `salida/AAAA-MM-DD/` se guardan:

- tablero.csv y tablero.json: indicadores, recomendaciones, fuentes y avisos.
- reporte.xlsx: hojas Tablero, Eventos e Historico.
- eventos.csv: detalle con fecha, dirección, enlace e imagen.
- historico.csv: registros anteriores y estimación de la semana, sin duplicar destino/fecha.
- ocupacion.png y tendencia.png: gráficos; si no hay datos numéricos se omite el gráfico correspondiente.
- boletin.eml: mensaje revisable con texto, HTML, reportes y gráficos adjuntos.

Una clasificación de **datos insuficientes** evita recomendar usando clima inexistente o eventos de otra ciudad. Las columnas de fuentes distinguen demo, archivo del usuario y API/web. La ocupación actual siempre es una estimación del modelo académico; no es una medición ni un pronóstico validado.

## Datos propios

```powershell
python main.py --datos .\mis_datos
```

La carpeta debe contener:

| Archivo | Columnas / estructura |
| --- | --- |
| destinos.csv | destino, latitud, longitud, zona, ocupacion_base |
| hoteles.xlsx | destino, hotel, habitaciones |
| comentarios.json | Lista de objetos con destino y comentario |
| historico.zip | Un único CSV con destino, fecha y ocupacion |
| eventos.html | Tarjetas article/div con clase evento, data-destino, título y time datetime="AAAA-MM-DD"; opcional a href, img src y dirección |

CSV usa coma y UTF-8. Las fechas del histórico deben ser ISO. Los destinos se unen sin diferencias de espacios, acentos o mayúsculas. Los nulos de ocupación no se inventan como ceros; comentarios vacíos se excluyen, eventos se deduplican y fechas inválidas se descartan. Para cada destino se toma el último histórico anterior a la semana. Sin base anterior mayor que cero no se calcula variación ni prioridad.

Las plantillas de `datos/` generan Excel y ZIP en `salida/entradas_demo/` para demostrar lectura real de esos formatos. Las fechas de eventos e histórico demo se ubican respecto de la semana elegida. Los archivos originales no se modifican.

En vivo, la fuente web configurada es Buenos Aires. No se reutiliza para Mendoza, Mar del Plata ni destinos libres. Agregar nuevas fuentes requiere inspeccionar su HTML y verificar términos y robots.txt. Si una página cambia sus selectores o carece de fechas interpretables, se informa la limitación. Los archivos históricos y comentarios siguen siendo demo a menos que se indique --datos.

## API y práctica POST

```powershell
uvicorn plataforma_turistica.api:app --reload
```

- GET http://127.0.0.1:8000/ : estado.
- GET http://127.0.0.1:8000/destinos : catálogo predeterminado.
- GET http://127.0.0.1:8000/analisis/Mendoza : análisis demo.
- POST http://127.0.0.1:8000/analisis : JSON {"destino":"Mendoza","en_vivo":false}.
- Documentación: http://127.0.0.1:8000/docs.

La API devuelve resultados, sin enviar emails. La exportación y el boletín se ejecutan desde main. Con el servidor iniciado, el cliente requests de POST se demuestra con:

```powershell
python -m plataforma_turistica.practica_api --post-local "Mendoza"
```

GET consulta; POST solicita un análisis usando un cuerpo JSON. PUT reemplazaría una configuración completa, PATCH modificaría campos y DELETE eliminaría una configuración. No se agregan operaciones de escritura sin necesidad funcional.

## JSON, XML y autenticación

Open-Meteo es público y no requiere clave para esta práctica. Para demostrar autenticación y ambos formatos se usa OpenWeatherMap, también visto en clase. Copiar .env.example como .env y completar OPENWEATHER_API_KEY con una clave propia activa:

```powershell
python -m plataforma_turistica.practica_api --formato json
python -m plataforma_turistica.practica_api --formato xml
python main.py --en-vivo --proveedor openweathermap --destino "Buenos Aires"
```

JSON se interpreta con response.json(), diccionarios y listas. XML se interpreta con ElementTree, elementos y atributos. Ambos se convierten al mismo objeto Clima. OpenWeatherMap aporta el próximo intervalo de tres horas; Open-Meteo combina temperatura actual y probabilidad diaria, por lo que no representan ventanas idénticas.

La clave se lee del entorno y viaja en el parámetro appid; nunca se imprime ni se exporta. Los errores 401/403 indican rechazo de credenciales; 429 indica límite de solicitudes y no provoca reintentos automáticos. Se usan timeout, parámetros, headers, raise_for_status y una pausa. No se incluye una clave compartida ni se presenta como realizada una consulta autenticada sin credenciales.

## Boletín y SMTP

Sin --enviar se genera el archivo EML con todos sus adjuntos para revisarlo. Para un envío real completar en .env:

```text
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
SMTP_MODE=ssl
EMAIL_USER=tu_cuenta@gmail.com
EMAIL_PASSWORD=tu_contrasena_de_aplicacion
EMAIL_RECEIVER=destinatario@ejemplo.com
```

```powershell
python main.py --en-vivo --destino "Buenos Aires" --enviar
```

EMAIL_RECEIVER acepta varias direcciones separadas por coma; --para permite reemplazarlas. No se envía automáticamente a los destinatarios de ejemplo. Las credenciales se excluyen del repositorio. Ver docs/correo.md para SMTP local, Gmail y ejecución semanal.

## Verificación

```powershell
python -m unittest discover -s tests -v
```

Las pruebas verifican limpieza, unión por destino, histórico, formatos de salida, gráficos PNG, adjuntos, cliente POST, API GET/POST y errores de fuentes/autenticación. Las pruebas de red y SMTP usan respuestas controladas; no gastan cuota ni envían correos reales. GitHub Actions ejecuta las pruebas y genera un reporte demo descargable.

## Trazabilidad

| Requisito | Evidencia |
| --- | --- |
| N01-N07 | main, módulos de configuración, normalización, indicadores y clasificación |
| N08-N09 | docs/evidencia_web.md, web_info e inventario_html |
| N10-N12 | eventos: descarga responsable, atributos y demostrar_find_all |
| N13 | Open-Meteo y comparación pública/privada en docs/evidencia_web.md |
| N14-N18 | clima, practica_api, API local y documentación de formatos, HTTP y claves |
| N19-N22 | datos, etl y exportaciones |
| N23 | visualizacion y gráficos PNG |
| N24-N25 | boletines, archivo EML, envío SMTP y docs/correo.md |

Las integraciones con servicios reales requieren disponibilidad del sitio, credenciales propias cuando corresponda y revisar condiciones de uso. Tener un endpoint público no significa que carezca de autenticación; la URL interna ficticia de config solo sirve para explicar el concepto de API privada.

Fuentes técnicas: [Open-Meteo](https://open-meteo.com/en/docs), [OpenWeatherMap](https://openweathermap.org/api/forecast5), [smtplib](https://docs.python.org/3/library/smtplib.html).
