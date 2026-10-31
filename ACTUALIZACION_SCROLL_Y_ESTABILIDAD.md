# Actualización: launcher extendido y procesos aislados

## Launcher

- La ventana se abre maximizada.
- El banner superior tiene altura adaptable y prioriza la ilustración de escudos/rangos.
- Noticias, Agentes y Mapas siguen en la misma barra fija.
- La zona inferior tiene scroll; la landing contiene cuatro tarjetas amplias y exige desplazamiento vertical para recorrerlas.

## Por qué se cerraba

El código `0xC0000374` es una corrupción del heap nativo de Windows. El parche anterior había separado WASAPI, pero el proceso Qt todavía importaba `vision.minimap_reader`, `floor_ocr`, `map_ocr`, `team_ocr`, `operator_icon_match` y `side_ocr`. Esos módulos cargaban MSS, NumPy, OpenCV y pytesseract en el mismo proceso que PyQt6.

## Qué se hizo ahora

- Toda la captura y visión se ejecuta en `vision/worker.py` (proceso independiente).
- El audio WASAPI sigue aislado en `audio/worker.py`.
- `main.py` recibe resultados JSON Lines y emite señales Qt encoladas; no carga OpenCV, MSS, NumPy ni pytesseract.
- Los frames del minimapa se transmiten como bytes BGRA y se convierten a QImage en Qt.
- Si la visión termina por una DLL nativa, se registra el código del worker y se intenta reiniciarlo hasta tres veces; el HUD Qt permanece separado.
- `data/map_calibration.py` carga NumPy/OpenCV de forma perezosa solo cuando se pide una homografía antigua.
- Se redujo la frecuencia de repintado sin cambios visuales y la frecuencia de `SetWindowPos` para evitar trabajo Win32 redundante.
- `iniciar.bat` prefiere Python 3.12 del launcher oficial y evita el alias WindowsApps de Microsoft Store.

## Pruebas disponibles en este paquete

- Compilación estática de los 25 archivos Python.
- Revisión de imports: el proceso Qt no importa módulos de visión ni bibliotecas C/C++ de visión al arranque.
- 106 referencias de planos verificadas; cero faltantes.
- ZIP comprobado con CRC.

No se pudo ejecutar una prueba real con PyQt6, MSS/GDI, WASAPI o Rainbow Six Siege en este entorno; la validación final de Windows se hace en el PC del usuario. Si `main.py` sigue cayendo, los archivos a compartir son `overlay_log.txt` y `faulthandler_dump.txt`.
