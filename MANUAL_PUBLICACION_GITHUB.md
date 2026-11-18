# Manual para completar la entrega de la Fase 4

## 1. Verificar primero el proyecto en Windows

1. Abre la carpeta del proyecto en el Explorador de archivos.
2. En la barra de direcciones escribe `powershell` y presiona Entrar.
3. Confirma Python: `py --version`.
4. Ejecuta `py -m software_fj --demo`. Debe mostrar **Simulaciones superadas: 20/20**.
5. Ejecuta `py -m unittest discover -s tests -v`. Debe terminar en **Ran 39 tests** y **OK**.
6. Ejecuta `py -m software_fj` y prueba el menú con un cliente y una reserva.
7. Abre `%TEMP%\softwarefj_eventos.log` en Windows y comprueba que aparecen `INFO` y `ERROR` de casos inválidos. El programa imprime la ruta del registro al comenzar; en Linux/macOS utiliza `logs/eventos.log`.

## 2. Crear el repositorio (método GitHub web)

1. Inicia sesión en https://github.com/.
2. Pulsa **New repository** y elige un nombre, por ejemplo `UNAD-Fase4-SoftwareFJ`.
3. Configura el repositorio como **Public** si necesitas que el tutor lo consulte sin permisos (o da acceso explícito según lo que indique el curso).
4. Sube **el contenido de esta carpeta**, preservando las subcarpetas `software_fj`, `tests`, `evidencias` y `logs`. No subas solamente el archivo ZIP.
5. Confirma la carga con un mensaje descriptivo, por ejemplo `Entrega inicial: sistema POO con excepciones y pruebas`.
6. Copia la URL que realmente aparece en tu navegador. No inventes la dirección.

### Alternativa usando Git (PowerShell)

En la carpeta del proyecto, si ya creaste el repositorio vacío en GitHub y tienes Git instalado, ejecuta:

```powershell
git init
git add .
git commit -m "feat: sistema de clientes, servicios, reservas y manejo de excepciones"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/UNAD-Fase4-SoftwareFJ.git
git push -u origin main
```

**Importante:** reemplaza `TU_USUARIO` con tu usuario real de GitHub y confirma que el repositorio exista. Si Git te pide configurar nombre/correo, sigue las indicaciones que aparecen en pantalla. No fabriques historial de trabajo ni participaciones de terceros.

## 3. Completar el informe PDF

1. Abre `INFORME_FASE4_SOFTWARE_FJ.docx` en Word.
2. Busca la sección **Enlace del repositorio en GitHub**.
3. Sustituye `[PEGAR AQUÍ LA URL REAL DEL REPOSITORIO]` por la URL real copiada en el paso anterior.
4. Revisa nombre del estudiante y demás datos académicos.
5. Guarda los cambios y usa **Archivo → Guardar como → PDF** para obtener el PDF definitivo.
6. Abre el PDF y prueba el enlace en el documento.

## 4. Publicar en el foro y enviar la entrega

- Comparte en el foro la URL del repositorio, junto con una presentación breve del proyecto.
- Adjunta el PDF definitivo en el espacio de entrega indicado por el tutor (y el repositorio según sus instrucciones).
- La **guía clasifica la actividad como colaborativa** con cinco estudiantes; como deseas realizarla individualmente, solicita al tutor confirmación sobre cómo acreditará el componente de colaboración (30 puntos en la rúbrica). No se debe simular trabajo en equipo.
- La guía indica cierre el **domingo 22 de noviembre de 2026**.

## 5. Comprobación final

- [ ] El proyecto está publicado y puede abrirse desde el enlace.
- [ ] `python -m software_fj --demo` presenta 20/20.
- [ ] `python -m unittest discover -s tests -v` presenta 39/39.
- [ ] El repositorio muestra el código, pruebas, evidencia y README.
- [ ] El PDF incluye portada, introducción, enlace verdadero, conclusiones y referencias APA.
- [ ] Compartiste el enlace en el foro y gestionaste la condición individual con el tutor.
