# Auto-invoice

Aplicación de escritorio en Python para automatizar la carga de facturas en una plataforma interna. Combina una interfaz PyQt5 para reunir los datos de una solicitud con automatización de navegador mediante Selenium.

## Problema que aborda

La carga manual de varias facturas exige repetir selecciones, fechas, campos y archivos. Este proyecto organiza esos datos en una interfaz y ejecuta el flujo de carga en el sistema al que tiene acceso la organización.

## Funciones implementadas

- Captura de departamento, clase, solicitud, fechas, caso, cliente y carpeta de facturas.
- Automatización del navegador para completar el proceso de carga.
- Procesamiento de archivos XML de facturas y apoyo de automatización de escritorio.
- Interfaz gráfica que inicia el proceso con los datos seleccionados.

## Tecnologías

Python · PyQt5 · Selenium · automatización de escritorio · procesamiento XML

## Ejecutar localmente

Instala las dependencias con `pip install -r requirements.txt` y ejecuta `python interface.py`. El flujo requiere una cuenta autorizada y acceso a la plataforma interna. La interfaz solicita la contraseña en cada ejecución; no la guarda en `settings.json` ni la envía como argumento de línea de comandos.

## Alcance de la demostración

Para mostrar el proyecto en un portafolio, usa capturas y datos ficticios; evita publicar facturas, credenciales, registros de sesión o información de clientes.

No se publican métricas de ahorro de tiempo hasta contar con una comparación documentada y reproducible.

## Estado del proyecto

El código se desarrolló para un proceso específico de una organización. La versión actual excluye del repositorio los archivos locales de configuración, registros y resultados generados. Las credenciales que estuvieron presentes en versiones anteriores deben cambiarse en el servicio correspondiente: retirarlas de la versión actual no las borra del historial de Git.
