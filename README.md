# Sistema Integral de Gestión de Clientes, Servicios y Reservas — Software FJ

**Universidad Nacional Abierta y a Distancia (UNAD)** · Ingeniería de Sistemas  
**Programación (213023) · Fase 4 — Componente práctico**  
**Estudiante:** Mateo Morales Bravo · **Fecha:** noviembre de 2026

## Descripción

Solución en **Python 3.10+** al **Ejercicio 1 del Anexo 3**. Gestiona clientes, salas, equipos y asesorías especializadas mediante **objetos y listas en memoria**, sin bases de datos. Los archivos `logs/*.log` se utilizan **únicamente para registrar eventos y errores**. La información de clientes y reservas se pierde al cerrar el proceso, por diseño y en cumplimiento del enunciado.

## Ejecución en Windows (PowerShell)

1. Descarga o descomprime la carpeta del proyecto.
2. Abre PowerShell en la carpeta que contiene `software_fj` y `tests`.
3. Comprueba que Python esté instalado: `py --version` (o `python --version`).
4. Ejecuta las 20 simulaciones: `py -m software_fj --demo`.
5. Ejecuta las 39 pruebas: `py -m unittest discover -s tests -v`.
6. Abre el menú interactivo: `py -m software_fj`.
7. Revisa el log en la ruta que imprime el programa. **En Windows** se guarda de forma predeterminada en `%TEMP%\softwarefj_eventos.log` para evitar problemas de escritura en OneDrive. **En Linux/macOS** se guarda en `logs/eventos.log`. El log de ejemplo `logs/eventos.log` está incluido como evidencia. Para elegir una ruta distinta utiliza `--log ruta/del/archivo.log`.

Si el comando `py` no funciona, sustitúyelo por `python`. No es necesario instalar paquetes de terceros.

## Estructura del proyecto

```text
software_fj/
    __init__.py     Exporta los componentes públicos
    __main__.py     Menú y punto de entrada (--demo / interactivo)
    demo.py         20 simulaciones con resultados esperados
    errores.py      Jerarquía de excepciones personalizadas
    gestion.py      Gestión de listas y reservas concurrentes
    modelos.py      Entidad, Cliente, Servicio, Sala, Equipo, Asesoria y Reserva
    registro.py     Registro rotativo de eventos y errores
 tests/
    test_sistema.py      39 pruebas unittest
 evidencias/
    pruebas_unittest.txt  Salida de pruebas reales
    simulaciones.txt      Salida de las 20 simulaciones
 logs/
    eventos.log          Registro real de la ejecución demostrativa
 INFORME_FASE4_SOFTWARE_FJ.docx / .pdf
 MANUAL_PUBLICACION_GITHUB.md
```

## Reglas de negocio implementadas

- Datos obligatorios: identificación y nombre del cliente, correo válido, teléfono con 7 a 15 dígitos.
- Identificadores únicos para clientes, servicios y reservas.
- Tarifa por hora positiva; capacidad de sala y unidades de equipo como enteros positivos.
- Duración de servicios por horas enteras: sala 1–12, equipo 1–72, asesoría 1–8. Estos límites constituyen **decisiones de diseño** para la simulación, no valores especificados en el Anexo 3.
- El sistema valida disponibilidad por horario. Las salas y asesorías admiten una reserva simultánea por servicio. Los equipos admiten reservas simultáneas hasta el número de unidades.
- La confirmación y cancelación son transiciones controladas; cancelar libera disponibilidad.
- Los importes se calculan con `Decimal`, impuestos/descuentos opcionales expresados como tasas entre 0 y 1. Fórmula: `(tarifa × horas + cargo de preparación) × (1 − descuento) × (1 + impuesto)`. El cargo fijo se usa sólo en asesorías y también es una decisión de diseño.
- No se utiliza ninguna base de datos; ni se guardan clientes ni reservas en archivos.

## Programación orientada a objetos

- **Abstracción:** `Entidad` y `Servicio` son clases abstractas (`abc.ABC`).
- **Herencia:** `Cliente` y `Servicio` derivan de `Entidad`; `Sala`, `Equipo`, `Asesoria` derivan de `Servicio`.
- **Polimorfismo:** cada servicio redefine `validar_parametros`, `_subtotal` y `describir`.
- **Encapsulación:** los datos personales se almacenan como atributos privados por convención (`_correo`, `_telefono`), con propiedades validadoras. Las listas se exponen como tuplas de solo lectura.
- **Variantes/sobrecarga:** `Servicio.calcular_costo` admite argumentos opcionales y firmas `typing.overload`. En Python `@overload` ofrece sobrecarga de tipado; en ejecución sólo actúa una implementación.
- **Excepciones:** errores personalizados, `try/except`, `try/except/else`, `finally` y encadenamiento con `raise ... from`.

## Manejo de errores y logs

Cada operación ejecutada a través del menú y cada escenario de `--demo` captura los errores esperados, los registra y permite seguir trabajando. Las excepciones imprevistas se registran con traza. `ManejadorRotativoSinBloqueo` (derivado de `RotatingFileHandler`) rota el archivo y lo cierra después de cada evento. Para evitar errores en OneDrive, la ubicación predeterminada en Windows es `%TEMP%\softwarefj_eventos.log`; puede modificarse con `--log`. No se incluyen correos ni teléfonos en las líneas de auditoría.

## Importante para la entrega a la UNAD

La guía exige publicar el proyecto en **GitHub** y añadir al informe PDF el **enlace real del repositorio**. Este archivo no contiene un enlace falso. Tras subirlo, sustituye el indicador de enlace pendiente en el Word, exporta de nuevo a PDF y comparte la URL en el foro. La actividad es calificada como **colaborativa**; si se entrega individualmente, conviene consultar con el tutor la forma de acreditarlo. No inventar commits, ramas, integrantes ni participaciones ajenas.

## Fuentes

- Universidad Nacional Abierta y a Distancia. (2026). *Anexo 3 – Problema a desarrollar Fase 4: Ejercicio 1*. Material del curso Programación 213023.
- Universidad Nacional Abierta y a Distancia. (2026). *Guía para el desarrollo del componente práctico – Fase 4*. Material del curso Programación 213023.
- Python Software Foundation. (s. f.). *Errores y excepciones*. https://docs.python.org/es/3.12/tutorial/errors.html

## Corrección de compatibilidad con Windows (16 de noviembre de 2026)

Si una versión anterior del proyecto mostraba `OSError: [Errno 9] Bad file descriptor` y
`PermissionError: [WinError 32]`, se debía a los manejadores de log que
permanecían abiertos durante las pruebas, especialmente en Windows/OneDrive.

Se ha reemplazado el manejador de archivos persistente por una variante que
**abre, registra y cierra** el archivo en cada evento, manteniendo la
rotación y las mismas 39 pruebas. El test que utiliza `TemporaryDirectory`
comprueba además que no quedan streams abiertos.

Si ya publicaste una versión anterior en GitHub, reemplaza
`software_fj/registro.py` y `tests/test_sistema.py` por las versiones de esta
entrega; actualiza también este `README.md`. Vuelve a ejecutar las 20
simulaciones y las 39 pruebas desde tu instalación de Windows.

## Comprobación de Windows en el equipo del estudiante (16-11-2026)

El estudiante informó que **39/39 pruebas** y **20/20 simulaciones** se ejecutaron, pero que la escritura en `logs/eventos.log` fallaba con `Bad file descriptor`. Confirmó en su Windows que la misma demostración y el registro de todos los eventos **sí funcionaron** cuando utilizó `--log "%TEMP%\softwarefj_eventos.log"`. Por eso, a partir de esta revisión, esa ubicación es la opción predeterminada de Windows. Este comportamiento necesita volver a comprobarse después de instalar la actualización.
