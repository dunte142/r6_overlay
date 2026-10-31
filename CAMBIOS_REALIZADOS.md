# Cambios realizados — R6 Overlay Final

## Launcher
- `launcher.py` queda como punto de entrada de la aplicación de escritorio.
- Hub PyQt6 con pestañas de Noticias, Agentes y Mapas, estilo oscuro táctico,
  filtros de bando, fichas de operador y selectores de piso.
- El botón de inicio ejecuta `main.py` como subproceso independiente y guarda
  su salida en `overlay_log.txt`.
- `iniciar.bat` instala las dependencias declaradas y abre el launcher.

## Estabilidad del overlay
- Quitado el auto-ocultado forzado a los seis segundos; el HUD nuevo no depende de la fase de preparación.
- Un `threading.RLock` global (`vision/native_lock.py`) serializa llamadas de
  captura `mss`, OpenCV y Tesseract desde los detectores.
- Captura por instancia `mss` local a cada hilo, validación de regiones y
  detección explícita de frames vacíos.
- Los loops de visión/audio capturan excepciones temporales, registran errores y
  esperan antes de reintentar, en vez de finalizar por una transición de pantalla.
- Las señales de `main.py` conectan con slots Qt mediante `QueuedConnection`;
  los detectores no manipulan widgets desde sus hilos de trabajo.
- Se conserva `WindowStaysOnTopHint` y se reafirma `HWND_TOPMOST` mediante una
  llamada Win32 `SetWindowPos` protegida.

## Portabilidad y recursos
- Las rutas del launcher, `ui/assets.py` y `data/map_calibration.py` parten de
  `os.path.abspath(__file__)`; no dependen de una unidad/carpeta fija.
- Recursos organizados bajo `assets/ui/` por tipo y bando, incluyendo los
  badges originales y las exportaciones de referencia recibidas.
- Completa la ficha de Goyo y corrige su clasificación en el catálogo junto con
  Solid Snake; el catálogo queda con 39 defensores y 39 atacantes.

## Verificación realizada
- Sintaxis/AST de 25 archivos Python: correcta.
- `py_compile` de los archivos Python: correcto.
- 106 rutas de planos de calibración verificadas; no falta ningún archivo.
- 20 rutas de iconos de `ui/assets.py` y 18 fuentes `.ttf` verificadas.
- 78 operadores, 78 badges con nombre coincidente y reparto 39/39 verificados.
- La UI y la captura en vivo no se pudieron ejecutar dentro de este entorno de
  preparación porque no están instalados PyQt6 ni `mss`. En Windows, instalar
  `requirements.txt` desde `iniciar.bat` antes de probar en el juego.


## Ajuste visual del overlay in-game (referencia proporcionada)

- Reemplacé el panel compacto de preparación por una composición diegética a pantalla completa, manteniendo visible el fondo del juego y usando coordenadas escalables para 1920×1080 y resoluciones 16:9 similares.
- Añadí el marco perimetral naranja, el título y los iconos de la columna derecha, las cabeceras por bando, cuatro tarjetas de compañeros y cinco plazas de rivales.
- Integré los 78 PNG transparentes de `assets/ui/operator_portraits/` mediante un mapa operador→recurso para mostrar el personaje, el gadget y el consejo correctos.
- Las tarjetas de equipo usan badges existentes; los compañeros aún no leídos y rivales no identificados se muestran como pendientes o `?`, sin inventar identidades.
- Corregí la ruta del icono de operador desconocido para usar `Group 69.png` (la tarjeta con `?`, en lugar del icono de ajustes).
- Las teclas globales y los paneles F1/F2/F3 siguen siendo independientes del HUD táctico nuevo.


## Revisión del launcher y HUD persistente (30/10/2026)

- El launcher usa una estructura persistente: encabezado, banner con el arte `launcher_hero.png`, navegación NOTICIAS/AGENTES/MAPAS y un único panel de contenido. Al cambiar de pestaña, únicamente cambia el contenido inferior; al abrir una ficha o un mapa, la barra de navegación conserva su posición dentro del documento.
- La cuadrícula de noticias conserva cuatro tarjetas 2×2; Agentes y Mapas usan el mismo panel central con sus respectivas cuadrículas y vistas de detalle.
- Al seleccionar un operador se carga su composición PNG correspondiente de `assets/ui/operator_portraits/attackers/` o `defenders/`. Esas fichas incluyen render, gadget, descripción y consejo de uso. Los 78 operadores tienen recurso mapeado y datos de `data/gadgets.py`.
- Se retiró la nomenclatura y el estado del antiguo HUD táctico: el renderizador principal se llama ahora `tactical_hud` y F1 ejecuta `toggle_tactical_hud()`.
- F1 abre/cierra el HUD nuevo. La detección del operador solo actualiza sus datos y no abre/cierra el HUD. No hay temporizador de auto-ocultado ni lógica vinculada al cambio preparación→ronda 3D.
- La ventana transparente se mantiene viva, no acepta foco y reafirma su geometría y `HWND_TOPMOST` mediante `SetWindowPos` cada 100 ms sin activar la ventana.
- F2-F6 conservan sus funciones; las notificaciones automáticas y el arco de sonido quedan vinculados a la visibilidad del HUD principal.


## Corrección adicional (2026-10-30)

- El launcher tiene exactamente un `QScrollArea` global que envuelve encabezado, banner, navegación y contenido. Se eliminaron los scrolls internos de Noticias, Agentes, Mapas y fichas de detalle.
- La altura del documento se sincroniza con la página/ficha activa para que cada pestaña utilice el mismo scroll general sin reservar el alto de las otras categorías.
- `vision/screen_capture.py` admite `from mss import MSS`, la fábrica `mss.mss()` y el backend específico de Windows; normaliza monitores antiguos tipo diccionario y nuevos modelos `Monitor` basados en atributos.
- La región del minimapa se inicializa de forma perezosa y no se calcula durante el import.
- Se sustituyó SoundCard por PyAudioWPatch para loopback WASAPI en un proceso independiente, intentando eliminar el cierre nativo reportado en el proceso de audio.
- El worker de visión registra ruta del módulo MSS y las APIs disponibles para detectar instalaciones duplicadas o módulos locales que sombreen el paquete.


## Corrección de dependencia de audio (30/10/2026)

- `iniciar.bat` comprueba el import `pyaudiowpatch` con el intérprete seleccionado y, si falta, instala explícitamente `PyAudioWPatch==0.2.12.9` usando wheels binarios.
- `audio/worker.py` intenta una única instalación automática usando `sys.executable` cuando se inicia `main.py` sin pasar por el BAT.
- Si la instalación no está disponible, el worker informa el comando exacto y finaliza de forma controlada; el proceso Qt y el worker de visión permanecen activos.
- `main.py` reconoce los estados `installing` y `unavailable` del protocolo JSONL.
