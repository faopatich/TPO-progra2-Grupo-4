# Evidencia web para N08 y N09

## Recurso inspeccionado

- Navegador: Microsoft Edge, con DevTools y la pestaña **Elements** para la inspección manual.
- URL: `https://turismo.buenosaires.gob.ar/es/categoria-general/eventos2026`.
- Protocolo: HTTPS.
- Dominio DNS: `turismo.buenosaires.gob.ar`.
- Dirección IPv4 resuelta el 11/09/2026: `200.16.89.120`. La IP puede cambiar; `web_info.py` permite volver a resolverla.
- Finalidad: agenda oficial de eventos turísticos de la Ciudad de Buenos Aires.
- Términos: el sitio del GCBA incluye al portal de turismo dentro de sus términos y publica su contenido con licencia Creative Commons Reconocimiento 2.5 Argentina. Esto no reemplaza la revisión de los términos vigentes antes de una ejecución real.
- `robots.txt`: `eventos.descargar_html` lo consulta en cada ejecución. Ante un error o una prohibición, el programa no obtiene la página y usa el HTML académico local.
- Frecuencia: una solicitud por ejecución, espera mínima de un segundo y `User-Agent` identificable.

## Inspección HTML

En la página oficial se inspeccionaron la estructura principal, los contenedores de las tarjetas, sus enlaces e imágenes. Como el sitio puede cambiar su maquetado, `datos/eventos_demo.html` conserva las etiquetas necesarias para que la práctica y las pruebas sean estables:

| Etiqueta | Uso observado o reproducido |
| --- | --- |
| `html`, `head`, `body` | estructura principal del documento |
| `div` | contenedor de la agenda |
| `article` | tarjeta de cada evento |
| `table`, `tr`, `td` | resumen tabular de eventos |
| `a` | enlace al detalle; atributos `href`, `title` y `data-id` |
| `img` | imagen del evento; atributos `src` y `alt` |
| `span` | título, fecha o dirección; atributo `class` |

Las tarjetas también exponen `id`, `class` y atributos `data-*`. El módulo `eventos.py` recupera texto, `href`, `src`, clases, identificadores y atributos de datos sin asumir que todos existen.

## API pública y API privada

Open-Meteo es la API pública elegida. Su endpoint está publicado en Internet, no necesita credenciales para el uso académico previsto y devuelve JSON meteorológico mediante GET.

Una API privada o interna solo admite clientes autorizados por una organización. Puede exigir token, VPN y permisos por rol, y sus endpoints no se publican para consumo general. `config.py` contiene una URL interna ficticia únicamente para documentar la diferencia; el programa nunca la consulta.
