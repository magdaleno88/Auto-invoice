# Auto-invoice | Case study

[Español](#español) · [English](#english)

## Español

### El problema

Una carga de facturas en una plataforma interna repetía la selección de departamento, clase, fechas, solicitud y archivos. La información fiscal llegaba en XML, mientras que el comprobante PDF debía acompañarla.

### Mi solución

Construí una interfaz PyQt5 para reunir los parámetros y un flujo Selenium que completa la carga. El código extrae del CFDI el emisor, UUID, fecha, subtotal e impuestos, comprueba la presencia del PDF con el mismo nombre y utiliza esos datos para rellenar líneas de factura.

### Demostración y límites

[Este XML ficticio](../examples/fictional_cfdi.xml) muestra la estructura de entrada. No es un CFDI válido y sus identificadores no pertenecen a ninguna factura real. El flujo completo depende de acceso autorizado a la plataforma interna; por eso aquí no se ofrece una ejecución pública ni se muestran pantallas o datos de clientes. El código actual utiliza automatización de interfaz y selectores específicos que pueden requerir mantenimiento si cambia la plataforma.

La aplicación no tiene una medición publicada de ahorro de tiempo ni pruebas automatizadas del flujo completo. Antes de uso externo, harían falta pruebas de integración en un entorno de ensayo y revisión de errores, permisos y manejo de datos.

## English

### The problem

Submitting invoices in an internal platform involved repeated choices of department, class, dates, request and files. Tax information came from XML, while its matching PDF had to be attached.

### What I built

I built a PyQt5 interface to collect parameters and a Selenium workflow to fill the submission form. The code extracts the issuer, UUID, date, subtotal and taxes from CFDI XML, checks for the PDF with the same filename and uses those values to populate invoice lines.

### Demo and limits

[This fictional XML](../examples/fictional_cfdi.xml) illustrates the input format. It is not a valid tax document and its identifiers do not represent a real invoice. The full workflow requires authorized access to an internal platform, so this repository does not offer a public execution or expose customer screens or data. The current automation relies on interface controls and selectors that may need updates when the platform changes.

There is no published time-saving measurement or automated test of the complete workflow. External use would require integration tests in a staging environment and a review of errors, permissions and data handling.
