# Diagnóstico y aislamiento del cierre nativo

## Qué significaba el código observado

`3221226356` equivale a `0xC0000374` (`STATUS_HEAP_CORRUPTION`). Es una terminación nativa de Windows: no es una excepción Python que pueda resolver un `try/except` dentro del mismo proceso.

El registro anterior indicaba que Qt, las hotkeys y los detectores alcanzaban a arrancar. Separar solo WASAPI no bastaba porque OpenCV, MSS, NumPy y pytesseract aún se importaban y ejecutaban en el proceso principal del HUD.

## Cambios de esta versión

1. **Aislamiento completo de visión:** `vision/worker.py` ejecuta MSS, NumPy, OpenCV, pytesseract y los detectores en un proceso auxiliar. `main.py` ya no importa esos módulos nativos.
2. **Audio aislado:** `audio/worker.py` captura loopback WASAPI en otro proceso. Se sustituyó SoundCard por PyAudioWPatch/PortAudio para evitar el backend CFFI que en el equipo terminaba con `0xC0000374`.
3. **Comunicación segura:** ambos procesos envían mensajes JSON Lines. Los resultados llegan a Qt mediante `pyqtSignal` con conexión encolada; los widgets nunca se modifican desde los procesos auxiliares.
4. **Minimapa serializado:** el worker envía el recorte BGRA como bytes. El proceso Qt crea el `QImage` sin importar NumPy ni OpenCV.
5. **Recuperación limitada:** si el worker de visión termina, el HUD sigue activo y el supervisor intenta reiniciar la visión hasta tres veces con espera creciente.
6. **Python recomendado:** `iniciar.bat` prioriza Python 3.12 del launcher oficial y evita seleccionar primero el alias de Microsoft Store en `WindowsApps`.
7. **MSS compatible:** se prueba la API `from mss import MSS`, la fábrica `mss.mss()` y el constructor de Windows. Se normalizan objetos `Monitor` sin depender de `.items()`. La región del minimapa se calcula de forma diferida.
8. **Launcher con scroll global:** un solo `QScrollArea` envuelve encabezado, banner de rangos, navegación y contenido; no hay scroll interno en ninguna pestaña ni ficha. Su altura se recalcula según la página activa.
9. **Launcher extendido:** se maximiza al abrir; la imagen de los rangos ocupa aproximadamente el 60% del alto disponible y las cuatro tarjetas de Noticias quedan debajo del banner.

## Cómo probar

- Extraer el ZIP completo en una carpeta nueva.
- Ejecutar `iniciar.bat`.
- Confirmar en `overlay_log.txt` que aparecen `Proceso auxiliar de audio` y `Proceso auxiliar de visión`.
- Pulsar F1 para mostrar/ocultar el nuevo HUD.
- Entrar en una partida y observar si el HUD permanece visible al pasar de preparación a la ronda 3D.

Si un proceso auxiliar de visión o audio falla con `0xC0000374`, el overlay principal debería permanecer abierto; el log muestra qué proceso terminó. Si el propio proceso `main.py` aún termina, el fallo restante está en Qt/driver gráfico/hotkeys u otra DLL cargada en el proceso principal y hace falta el nuevo `overlay_log.txt` para acotar esa ruta.

## Alcance de validación

Se valida la sintaxis, importaciones estáticas, rutas de recursos, integridad del ZIP y el protocolo JSON del worker. No se puede confirmar la estabilidad real de Windows, MSS/GDI, WASAPI o el controlador gráfico desde este entorno de creación; esa comprobación final se realiza en el PC Windows.
