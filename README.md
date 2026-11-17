# Plataforma de análisis turístico

**Trabajo práctico — Taller de Programación II. Solicitud 4: análisis turístico, reputación web y recomendaciones operativas.**

El programa reúne información de alojamientos, eventos y clima para generar un tablero, gráficos y un boletín por correo. El usuario puede analizar CABA u otra localidad. Si una fuente no dispone de datos para el destino, el informe lo indica.

## Antes de empezar

Se necesita Python 3.11 o posterior, conexión a Internet y una terminal en la carpeta raíz del proyecto. En Windows se puede usar la terminal de Visual Studio Code con PowerShell.

```powershell
cd "RUTA\AL\PROYECTO"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Reemplazar `RUTA\AL\PROYECTO` por la ubicación de la carpeta que contiene `main.py`. Se puede seleccionar `.venv` como intérprete de Python en VS Code. Los comandos siguientes usan el intérprete del entorno directamente, por lo que no es obligatorio activarlo.

## Archivos que hay que descargar

Los archivos de Inside Airbnb se descargan **una vez**, se guardan localmente y no se descargan automáticamente cada vez que se ejecuta el programa. Crear la carpeta `datos/inside_airbnb/` si no existe.

| Archivo y enlace directo | Guardar en | Uso |
| --- | --- | --- |
| [calendar.csv.gz — calendario de CABA](https://data.insideairbnb.com/argentina/ciudad-aut%C3%B3noma-de-buenos-aires/buenos-aires/2026-09-23/data/calendar.csv.gz) | `datos/inside_airbnb/calendar.csv.gz` | Necesario para calcular la referencia de no disponibilidad de CABA. |
| [reviews.csv.gz — reseñas detalladas de CABA](https://data.insideairbnb.com/argentina/ciudad-aut%C3%B3noma-de-buenos-aires/buenos-aires/2026-09-23/data/reviews.csv.gz) | `datos/inside_airbnb/reviews.csv.gz` | Necesario para el análisis de reputación real de CABA. Si falta, se informa que no está disponible. |
| [EOH: anexo de cuadros del INDEC](https://www.indec.gob.ar/ftp/cuadros/economia/EOH_cuadros_dic25.zip) | `datos/eoh_cuadros_2025.zip` | Referencia de ocupación hotelera para otras localidades relevadas. Si ya está en el proyecto, no hace falta descargarlo nuevamente. |

**No descomprimir ni renombrar los archivos de Airbnb.** El ZIP de la EOH también se conserva comprimido y debe tener el nombre indicado en la tabla. Los dos archivos de Airbnb son de la captura identificada como **23/09/2026**; el código tiene esa fecha configurada. Si se sustituye una captura por otra, hay que revisar y actualizar `CAPTURA_AIRBNB` en `plataforma_turistica/ocupacion.py`. Los archivos de Airbnb están excluidos de Git, por lo que deben copiarse o descargarse en cada computadora. La [política de Inside Airbnb](https://insideairbnb.com/data-policies/) solicita no republicar los datos y citar la fuente; sus datos públicos se ofrecen con licencia CC BY 4.0. Los enlaces pueden cambiar cuando la captura se archive: si dejan de funcionar, consultar [Get the Data](https://insideairbnb.com/get-the-data/) y sus condiciones de acceso a archivos históricos.

La carpeta debe quedar así:

```text
TPO/
├── main.py
├── requirements.txt
├── .env.example
├── datos/
│   ├── destinos.csv
│   ├── eoh_cuadros_2025.zip
│   └── inside_airbnb/
│       ├── calendar.csv.gz
│       └── reviews.csv.gz
├── plataforma_turistica/
├── docs/
└── salida/                       (se crea al ejecutar)
```

El calendario nacional de eventos se consulta en línea; no requiere descarga manual. El archivo `datos/eventos_demo.html` se conserva solo para practicar HTML y no alimenta la ejecución normal.

## Configuración del correo

Para generar el boletín revisable o enviarlo, crear `.env` a partir de `.env.example`. El comando siguiente solo debe usarse si todavía no existe `.env`:

```powershell
Copy-Item .env.example .env
notepad .env
```

Completar los datos propios:

```text
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
SMTP_MODE=ssl
EMAIL_USER=tu_cuenta@gmail.com
EMAIL_PASSWORD=tu_contrasena_de_aplicacion
EMAIL_RECEIVER=destinatario@ejemplo.com
OPENWEATHER_API_KEY=tu_clave_de_openweather
```

Para Gmail, activar la verificación en dos pasos y generar una **contraseña de aplicación** siguiendo la [ayuda de Google](https://support.google.com/accounts/answer/185833?hl=es). Colocarla en `EMAIL_PASSWORD`: no se usa la contraseña habitual. Algunas cuentas de trabajo o educativas pueden no permitir esta opción. Para una primera prueba, usar la propia dirección en `EMAIL_RECEIVER` y comprobar que el correo y sus adjuntos llegaron. Se pueden indicar varios destinatarios separados por coma.

`.env` contiene credenciales y está excluido de Git: cada integrante debe crear su propio archivo y no compartirlo. Si ya existe `.env`, editarlo directamente y **no volver a copiar** `.env.example` encima. `OPENWEATHER_API_KEY` solo es necesaria si se utiliza OpenWeatherMap; Open-Meteo no requiere esa clave.

### Protocolos y envío semanal

El proyecto usa `EmailMessage` para preparar el mensaje y `smtplib` con **SMTP** para enviarlo. **POP** e **IMAP** se usan para recibir o consultar mensajes y no son necesarios para el envío. Para Gmail se usa SSL con el puerto 465 y una contraseña de aplicación; el proyecto no implementa OAuth.

Para automatizar un envío semanal en Windows, crear una tarea en el Programador de tareas con un desencadenador semanal. Como acción, elegir el ejecutable `python.exe` del entorno `.venv`, indicar `main.py --destino "CABA"` como argumentos y establecer la carpeta raíz del proyecto en **Iniciar en**. Configurar primero `.env`, los archivos de datos e Internet, y comprobar la recepción del mensaje y los adjuntos. Cada ejecución intenta un envío nuevo. El programa no crea la tarea automáticamente.

## Ejecutar el análisis

Para generar los reportes de CABA **sin enviar correo**:

```powershell
.\.venv\Scripts\python.exe main.py --destino "CABA" --sin-enviar
```

Para generar los reportes y **enviar el boletín en la misma ejecución**:

```powershell
.\.venv\Scripts\python.exe main.py --destino "CABA"
```

El envío es el comportamiento predeterminado; cada ejecución normal intenta enviar un correo nuevo. Con `--sin-enviar`, el programa nunca envía el mensaje. Si remitente y destinatarios están configurados, también guarda `boletin.eml` para revisarlo; de lo contrario genera los reportes sin crear ese archivo.

Ejemplos para otro destino y para consultar las opciones:

```powershell
.\.venv\Scripts\python.exe main.py --destino "Mendoza" --sin-enviar
.\.venv\Scripts\python.exe main.py --destino "Mar del Plata" --sin-enviar
.\.venv\Scripts\python.exe main.py --help
```

La fecha del informe se agrupa de lunes a domingo. En vivo se analiza la semana actual, porque el clima consultado no es histórico. Con `--sin-red` no se consultan eventos ni clima y esos datos se informan como no disponibles. El análisis de reseñas puede tardar porque se procesa un archivo grande por bloques.

## Archivos generados

Cada ejecución guarda sus resultados en `salida/AAAA-MM-DD/AAAAMMDD_HHMMSS_microsegundos/`. La primera fecha es el lunes de la semana del informe; la segunda identifica la ejecución y evita sobrescribir resultados anteriores:

- `tablero.csv` y `tablero.json`: indicadores, clasificación, recomendación, fuentes y advertencias.
- `reporte.xlsx`: tablero, eventos e histórico en hojas separadas.
- `eventos.csv` e `historico.csv`: detalle usado en el análisis.
- `ocupacion.png`, `tendencia.png` y `reputacion.png`: gráficos generados con Pandas cuando hay datos suficientes.
- `boletin.eml`: vista del correo con los reportes y gráficos adjuntos. Se guarda al ejecutar `main.py` cuando están configurados remitente y destinatarios; la API envía el mensaje pero no guarda este archivo.

## Fuentes e interpretación de los resultados

- **CABA — alojamientos:** [Inside Airbnb](https://insideairbnb.com/get-the-data/). El programa divide las noches marcadas como no disponibles por las noches registradas para la semana. Una noche no disponible puede estar reservada o bloqueada; **no es una ocupación hotelera medida**. El dato representa el estado registrado en la captura, no disponibilidad en tiempo real.
- **CABA — reputación:** reseñas de Inside Airbnb de los 90 días anteriores a la fecha nominal de captura. El código cuenta palabras de listas positivas y negativas. Las reseñas mixtas o sin coincidencias quedan agrupadas; el método no interpreta bien todos los idiomas, negaciones o contextos. No se exportan nombres ni textos de autores. Se excluyen reseñas con fecha posterior a la captura nominal.
- **Otras localidades — ocupación:** [Encuesta de Ocupación Hotelera del INDEC](https://www.indec.gob.ar/Nivel4/Tema/3/13/56). Se lee el anexo Excel comprimido con Pandas y se calcula la tasa mensual de habitaciones ocupadas sobre disponibles. El anexo incorporado llega a noviembre de 2025; es un dato histórico y solo cubre localidades relevadas. No se asignan datos de otra ciudad cuando falta una localidad.
- **Mendoza y Mar del Plata:** se usan las hojas de cada ciudad en el anexo EOH; la referencia y la comparación corresponden a los últimos dos meses disponibles anteriores al informe, no a ocupación actual.
- **Provincia de Buenos Aires:** si se solicita expresamente, se usa la hoja regional `Reg_ba` de la EOH como referencia; no representa necesariamente a cada localidad de la provincia. El programa no asigna el clima de una ciudad a toda la provincia, por lo que no calcula una recomendación completa con ese destino.
- **Eventos de CABA:** [agenda oficial de la Ciudad](https://turismo.buenosaires.gob.ar/es/article/que-hacer-esta-semana). Se consulta con `requests` y BeautifulSoup; los datos de actividades están en JSON dentro del HTML. La consulta respeta las reglas comprobadas por el programa y cuenta eventos según su fecha de inicio.
- **Eventos de otras localidades:** [agenda nacional de fiestas y eventos](https://www.argentina.gob.ar/jefatura/turismo-y-ambiente/turismo/fiestas-y-eventos-de-argentina). Se consulta el CSV de la planilla pública que alimenta esa página. Es una agenda parcial: cero resultados no demuestra que no existan otros eventos.
- **Clima:** [Open-Meteo](https://open-meteo.com/en/docs) por defecto; se consulta la temperatura actual y la probabilidad máxima de lluvia del día. Como alternativa está OpenWeatherMap con clave propia.

La estimación del proyecto usa reglas académicas: parte de la referencia de alojamiento, suma puntos por eventos y descuenta puntos por probabilidad de lluvia. **No es una medición de reservas ni un pronóstico validado.** La variación de CABA compara dos semanas de no disponibilidad de la misma captura; para EOH compara meses históricos. Las referencias de Airbnb y la EOH miden cosas distintas y no son directamente comparables. La reputación de Airbnb y de los archivos propios se informa por separado y no modifica la estimación ni la recomendación. Las menciones usadas para clasificar corresponden a los títulos de eventos; las menciones en reseñas se muestran aparte.

## Prueba recomendada: CABA

Para la demostración y para comprobar el circuito más completo, usar **CABA** como destino de referencia. El programa también acepta `Buenos Aires` y `Ciudad de Buenos Aires` como nombres de la ciudad; la provincia es un destino distinto.

1. Preparar el entorno y colocar los dos archivos de Inside Airbnb en `datos/inside_airbnb/`, como se indica en **Archivos que hay que descargar**. El calendario es necesario para la referencia de alojamiento y las reseñas para mostrar la reputación. Son archivos de la captura del 23/09/2026, no datos en tiempo real.
2. Contar con conexión a Internet para consultar la agenda de CABA y el clima. Para enviar el correo, completar además `.env` según **Configuración del correo**.
3. Desde la terminal de VS Code, ubicada en la carpeta que contiene `main.py`, ejecutar primero sin enviar el correo:

```powershell
.\.venv\Scripts\python.exe main.py --destino "CABA" --sin-enviar
```

El programa usa la semana actual: calcula la proporción de noches no disponibles de la captura de Airbnb, analiza las reseñas, consulta eventos y clima, y aplica las reglas académicas de ocupación y recomendación cuando hay datos suficientes. Compara la referencia con la semana anterior de la misma captura. **Una noche no disponible puede estar reservada o bloqueada; la estimación no es una medición real de ocupación ni un pronóstico validado.**

Revisar la tabla y los avisos en la terminal y los archivos generados en una carpeta propia dentro de `salida/AAAA-MM-DD/`: tablero CSV/JSON, Excel y gráficos disponibles. Si están configurados remitente y destinatario también se genera `boletin.eml` para revisión. Los resultados varían según la semana y las fuentes; si faltan datos, no hay cobertura de la captura o falla una consulta, puede aparecer `datos insuficientes` y se explicará en los avisos. El análisis de reseñas puede tardar.

Para generar los reportes y **enviar el boletín en la misma ejecución**, una vez configurado el correo:

```powershell
.\.venv\Scripts\python.exe main.py --destino "CABA"
```

Verificar en la casilla de destino el mensaje, el tablero y los gráficos adjuntos. Cada ejecución sin `--sin-enviar` intenta enviar un nuevo correo. Para comprobar solo la lectura local, sin consultar clima ni eventos en línea:

```powershell
.\.venv\Scripts\python.exe main.py --destino "CABA" --sin-red --sin-enviar
```

En ese último caso se esperan avisos de fuentes no consultadas y una recomendación incompleta; no es una prueba del circuito en vivo.

## Datos propios opcionales

Con `--datos` se pueden leer archivos propios mediante Pandas:

```powershell
.\.venv\Scripts\python.exe main.py --destino "CABA" --datos .\mis_datos --sin-enviar
```

La carpeta indicada debe contener `destinos.csv` (destino, latitud, longitud, zona), `hoteles.xlsx` (destino, hotel, habitaciones), `comentarios.json` (lista de objetos con destino y comentario) y `eventos.html` (tarjetas con destino, título y fecha). Para practicar la lectura de archivos comprimidos se puede incluir `historico.zip` con un único CSV (destino, fecha y ocupacion; fechas `AAAA-MM-DD`); es opcional. El campo `ocupacion_base` del CSV también es opcional y no se usa para reemplazar Airbnb o EOH.

Estos archivos permiten practicar la lectura de diferentes formatos y aportar información propia. El archivo de hoteles se carga para practicar Excel, pero sus capacidades no intervienen en el cálculo ni en el tablero final. El programa sigue tomando la referencia de alojamiento de Airbnb para CABA o de la EOH para otras localidades; no utiliza el histórico propio como reemplazo de esas fuentes. En modo en vivo se consultan las agendas externas; el HTML propio se utiliza con `--sin-red`, pero sin clima en línea no se calcula la recomendación completa.

## API y prueba de CABA con Postman

La API permite consultar el análisis en JSON. Para probarla se necesitan el entorno y los archivos de CABA indicados arriba. Abrir una terminal en la carpeta del proyecto, iniciar el servidor y dejar esa terminal abierta:

```powershell
.\.venv\Scripts\python.exe -m uvicorn plataforma_turistica.api:app --reload
```

En Postman:

1. Crear una solicitud **POST** a `http://127.0.0.1:8000/analisis`.
2. Elegir **Body → raw → JSON**, pegar el siguiente contenido y pulsar **Send**:

```json
{
  "destino": "CABA",
  "en_vivo": true
}
```

La respuesta muestra el destino como `Buenos Aires`, eventos, clima, indicadores, clasificación, recomendación, reputación, fuentes y advertencias. Revisar especialmente `fuente_ocupacion`, `periodo_ocupacion`, `fuente_eventos`, `fuente_clima` y `advertencias`. No se deben esperar números fijos: dependen de la captura, la semana y la disponibilidad de las fuentes. `null` o `datos insuficientes` indican que faltan datos para parte del cálculo. Para no consultar clima ni eventos, enviar `"en_vivo": false`; en ese caso no se obtiene una recomendación completa.

Como alternativa se puede crear una solicitud **GET** a `http://127.0.0.1:8000/analisis/CABA?en_vivo=true`. Para comprobar que el servidor responde, usar **GET** en `http://127.0.0.1:8000/`. La documentación interactiva también está en [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Para que el mismo POST genere los reportes y envíe el boletín, configurar el correo en `.env` y usar este cuerpo:

```json
{
  "destino": "CABA",
  "en_vivo": true,
  "enviar_correo": true
}
```

La API ejecuta el análisis una sola vez, guarda los reportes y gráficos disponibles en una carpeta propia dentro de `salida/AAAA-MM-DD/` y los adjunta al correo enviado a `EMAIL_RECEIVER`. La respuesta indica `"correo_enviado": true` después de que el servidor SMTP acepta el mensaje. Si falla la generación de los archivos o el envío, devuelve un error HTTP 502; un calendario Airbnb faltante produce 503, un error de análisis puede producir 400 y un JSON que no cumple el formato esperado puede producir 422. Cada POST con `enviar_correo: true` intenta un nuevo envío. Si se omite o se indica `false`, solo se consulta el análisis: no genera archivos ni envía correo. El GET nunca envía correo. La API usa Open-Meteo para el clima. Detener el servidor con `Ctrl + C` en la terminal.

### Usar OpenWeatherMap

Open-Meteo es el proveedor predeterminado. Para usar OpenWeatherMap en el análisis completo:

1. Crear y verificar una cuenta en [OpenWeatherMap](https://openweathermap.org/guide) y obtener la clave desde la sección **API keys** de la cuenta. La clave debe estar activa y tener acceso al pronóstico de 5 días usado por el proyecto.
2. Agregar o completar en `.env` la línea `OPENWEATHER_API_KEY=tu_clave`, sin compartirla.
3. Ejecutar el análisis indicando el proveedor:

```powershell
.\.venv\Scripts\python.exe main.py --destino "CABA" --proveedor openweathermap --sin-enviar
```

Quitar `--sin-enviar` para enviar el boletín en la misma ejecución, siempre que el correo esté configurado. Si la clave es rechazada, verificar que esté activa y tenga acceso al producto; si se alcanza el límite de consultas, esperar antes de reintentar. El programa informa el error sin mostrar la clave.

Para practicar por separado el consumo autenticado en JSON y XML:

```powershell
.\.venv\Scripts\python.exe -m plataforma_turistica.practica_api --formato json
.\.venv\Scripts\python.exe -m plataforma_turistica.practica_api --formato xml
```

Los comandos de JSON y XML muestran el resultado de la consulta en la terminal; no generan el tablero ni envían correo. Requieren conexión y una clave activa de OpenWeatherMap. OpenWeatherMap aporta el próximo intervalo de tres horas; Open-Meteo usa temperatura actual y probabilidad máxima diaria, por lo que los valores no necesariamente coinciden.

GET consulta información; POST envía datos para solicitar un análisis. PUT serviría para reemplazar una configuración completa, PATCH para modificar una parte y DELETE para eliminarla.

## Estructura del código

Todos los archivos de la tabla, salvo `main.py`, están dentro de `plataforma_turistica/`.

| Archivo | Responsabilidad |
| --- | --- |
| `main.py` | Lee argumentos, ejecuta el análisis, exporta y envía el boletín. |
| `servicio.py` | Coordina las etapas del análisis. |
| `config.py`, `destinos.py` | Catálogo, coordenadas, listas, diccionarios y selección de destinos. |
| `eventos.py`, `agenda_servicio.py`, `agenda_nacional.py` | Descarga e interpretación de agendas y HTML. |
| `clima.py`, `geocodificacion.py` | Consultas meteorológicas y búsqueda de coordenadas. |
| `ocupacion.py`, `referencias.py` | Lectura de Airbnb y EOH e integración de referencias. |
| `reputacion.py`, `normalizacion.py` | Clasificación básica de reseñas y limpieza de cadenas. |
| `datos.py`, `etl.py` | Lectura de archivos, limpieza, agrupaciones, uniones y exportación. |
| `indicadores.py`, `clasificacion.py`, `analisis.py` | Indicadores, reglas y recomendaciones por destino. |
| `visualizacion.py`, `boletines.py` | Gráficos de Pandas y composición y envío del correo. |
| `api.py`, `esquemas.py`, `resultado.py` | API FastAPI y formato de entradas y respuestas. |
| `practica_api.py` | Consulta autenticada JSON/XML y cliente POST local. |

La documentación complementaria de inspección web está en `docs/evidencia_web.md`. El análisis normal no utiliza el HTML de ejemplo como si fuera una fuente real.

## Relación con los requisitos

Los nombres de módulos de la tabla se encuentran en `plataforma_turistica/`; los demás indican su ruta desde la raíz. Algunos requisitos se trabajan en varios archivos.

| Requisito | Contenido | Archivos principales |
| --- | --- | --- |
| N01 | Proyecto modular | `main.py`, `servicio.py` y módulos del paquete. |
| N02 | Ocupación estimada, variación, menciones y prioridad | `ocupacion.py`, `indicadores.py`, `analisis.py`. |
| N03 | Clasificación y recomendaciones | `clasificacion.py`, `config.py`. |
| N04 | Funciones de limpieza, fechas, clima e indicadores | `normalizacion.py`, `eventos.py`, `clima.py`, `indicadores.py`. |
| N05 | Listas de destinos, URL, palabras y destinatarios | `config.py`, `destinos.py`, `main.py`, `datos.py`. Los hoteles se leen de archivos propios; no hay una lista activa de hoteles piloto ni de métricas configurables. |
| N06 | Diccionarios | `config.py`, `destinos.py`. |
| N07 | Normalización de cadenas | `normalizacion.py`, `etl.py`, `reputacion.py`. |
| N08 | Navegador, URL, DNS e IP | `docs/evidencia_web.md`. Falta registrar el navegador usado en la inspección manual. |
| N09 | Inspección del HTML | `docs/evidencia_web.md`, `eventos.py`. La inspección manual en navegador debe registrarse como evidencia. |
| N10 | Web scraping y acceso responsable | `eventos.py`, `agenda_servicio.py`. |
| N11 | Texto y atributos HTML | `eventos.py`, `docs/evidencia_web.md`. |
| N12 | Búsquedas con `find_all` | `eventos.py`, función `demostrar_find_all`. |
| N13 | API pública y comparación con API privada | `clima.py`, `config.py`, `docs/evidencia_web.md`. |
| N14 | JSON y XML | `practica_api.py`. |
| N15 | GET, POST y documentación de otros métodos | `clima.py`, `practica_api.py`, `api.py` y sección API de este README. |
| N16 | `requests`, estados y errores | `clima.py`, `eventos.py`, `practica_api.py`. |
| N17 | Autenticación con clave | `practica_api.py`, `.env.example`. |
| N18 | Práctica con API pública y clave | `practica_api.py`; requiere una clave activa. |
| N19 | Extracción, transformación y carga | `datos.py`, `eventos.py`, `clima.py`, `etl.py`, `referencias.py`. |
| N20 | DataFrames, Series, tipos y nulos | `datos.py`, `etl.py`, `ocupacion.py`. |
| N21 | Lectura y exportación de formatos | `datos.py`, `etl.py`, `ocupacion.py`. |
| N22 | Agrupaciones, fechas, uniones y comparación | `etl.py`, `referencias.py`, `ocupacion.py`. |
| N23 | Gráficos con Pandas | `visualizacion.py`. |
| N24 | Correo, adjuntos y SMTP | `boletines.py`, `main.py`, `api.py` y la sección de correo de este README. |
| N25 | SMTP, POP, IMAP y acceso a Gmail | `boletines.py` y la sección de correo de este README. |

Para la demostración final se debe registrar la inspección manual del HTML y verificar la entrega real de un correo con sus adjuntos. El envío automático semanal requiere configurar el Programador de tareas de Windows como se explica en la sección de correo de este README. Las fuentes externas pueden cambiar o estar temporalmente no disponibles.
