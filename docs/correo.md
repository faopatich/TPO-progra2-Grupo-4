# Correo electrónico y boletín semanal

## Protocolos de la materia

- SMTP envía mensajes del programa al servidor y entre servidores.
- POP permite descargar mensajes recibidos. No se necesita para este proyecto.
- IMAP permite consultar y sincronizar carpetas de correo en el servidor. Tampoco se necesita para enviar boletines.
- EmailMessage compone asunto, remitente, destinatarios, texto, HTML y adjuntos.
- smtplib conecta con SMTP. Se usa SSL en el puerto 465 o STARTTLS en el 587.

Gmail requiere una cuenta que permita contraseñas de aplicación, habitualmente con verificación en dos pasos. No se usa la contraseña habitual de la cuenta. Algunas organizaciones no permiten contraseñas de aplicación; en ese caso requieren OAuth, que debe configurarse con el proveedor. El proyecto implementa contraseña de aplicación, no OAuth.

## Prueba local

Para probar manualmente con el servidor local de los ejemplos de clase:

```powershell
python -m pip install aiosmtpd
python -m aiosmtpd -n -l 127.0.0.1:1025
```

En .env indicar SMTP_SERVER=127.0.0.1, SMTP_PORT=1025, SMTP_MODE=local, EMAIL_USER=demo@example.com y EMAIL_RECEIVER=prueba@example.com. Ejecutar python main.py. El servidor local muestra el mensaje; no lo entrega a Internet. El modo sin cifrado solo se admite para localhost.

## Ejecución semanal en Windows

El programa genera y envía un boletín para la semana de lunes a domingo. Use `--sin-enviar` para generar los reportes sin enviar correo. Para automatizarlo, configurar una tarea en el Programador de tareas:

1. Crear una tarea con desencadenador semanal y elegir día y hora.
2. Acción: iniciar el ejecutable Python del entorno virtual del proyecto.
3. Argumentos: main.py --destino "CABA".
4. Campo "Iniciar en": carpeta raíz del repositorio.
5. Configurar .env y realizar primero un envío de prueba al propio correo.

Para trabajar con datos propios, agregar --datos con la ruta de la carpeta. Sin ella, se usan las fuentes reales configuradas y se informan los datos no disponibles. Si se elige otro destino sin agenda web, el resultado informa datos insuficientes. La tarea debe tener acceso a Internet y a los archivos del proyecto.

No se instala una tarea ni se envía correo durante la preparación del código. Cada ejecución normal adicional produce otro envío: no hay un bloqueo de duplicados entre ejecuciones.

## Verificación del envío

boletin.eml sirve para revisar composición y adjuntos; no demuestra entrega. El mensaje "Boletín enviado" solo aparece si SMTP acepta a todos los destinatarios. La aceptación SMTP no garantiza lectura ni recepción en bandeja de entrada. Ante rechazo o error no se imprime la clave.
