# Corrección del problema de logs en Windows

**Síntomas en la versión inicial:**

- `OSError: [Errno 9] Bad file descriptor` al escribir en `logs/eventos.log`.
- `PermissionError: [WinError 32]` al terminar una prueba dentro de `TemporaryDirectory`.
- El resultado mostraba 20/20 simulaciones correctas, pero 38/39 pruebas válidas.

**Causa:** el manejador de archivos conservaba abierto un descriptor del log. Windows bloquea la eliminación de archivos abiertos; además el registrador temporal de los tests seguía instalado para las pruebas posteriores.

**Corrección aplicada:** `software_fj/registro.py` ahora usa `ManejadorRotativoSinBloqueo`, una subclase de `RotatingFileHandler` que abre, escribe y cierra el log en cada evento, conservando la rotación. En `tests/test_sistema.py` se cierra y desinstala el manejador temporal antes de que se elimine la carpeta temporal. Las demás funcionalidades del proyecto se conservan.

**Comprobación realizada en el entorno de preparación:**

- `python -m software_fj --demo`: 20/20 simulaciones aprobadas.
- `python -m unittest discover -s tests -v`: 39 pruebas correctas (`OK`).
- `python -m software_fj`: menú interactivo abre y sale correctamente.

**Importante:** la comprobación anterior se realizó en Linux con Python 3.13; debe repetirse en el Windows con Python 3.12 del estudiante. No se afirma que esa verificación de Windows se haya realizado.

**Si los archivos ya se publicaron en GitHub:** actualice como mínimo `software_fj/registro.py`, `tests/test_sistema.py` y `README.md`, y haga un nuevo commit (por ejemplo: `fix: corregir logging y pruebas en Windows`). Si no se han publicado, suba directamente el contenido del proyecto corregido.

**Comandos de verificación en Windows, desde la raíz:**

```bat
py -m software_fj --demo
py -m unittest discover -s tests -v
py -m software_fj
```

Si continúa un error de permisos sobre una ruta de OneDrive, cierre las ventanas o editores que hayan abierto `eventos.log`, copie el proyecto a una carpeta local fuera de OneDrive y vuelva a ejecutar. No borre las pruebas ni silencie errores para conseguir `OK`.

## Segunda corrección: ruta predeterminada de auditoría en Windows

En una segunda prueba real del estudiante, las 39 pruebas dieron OK y la demostración aprobó 20/20, pero seguía fallando la **escritura del log bajo OneDrive** (incluso con manejadores sin bloqueo). Al repetir `py -m software_fj --demo --log "%TEMP%\softwarefj_eventos.log"`, las 20 simulaciones funcionaron y Notepad mostró todas las líneas INFO/ERROR correctamente.

**Cambio:** `software_fj/registro.py` detecta Windows para usar por defecto `%TEMP%\softwarefj_eventos.log`; `software_fj/__main__.py` muestra la ruta real y respeta `--log` si se proporciona. No se han cambiado las validaciones, la lógica de reservas ni las 39 pruebas.

Para comprobarlo en Windows:

```bat
py -m software_fj --demo
notepad "%TEMP%\softwarefj_eventos.log"
py -m unittest discover -s tests -v
```

Esta corrección se ha probado en Linux, y la ruta temporal fue comprobada por el estudiante en Windows usando `--log`; queda pendiente comprobar este nuevo valor predeterminado en Windows y subir los archivos revisados a GitHub.
