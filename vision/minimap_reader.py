"""
Lee el minimapa nativo que el juego YA muestra (esquina superior izquierda,
como en la captura que compartiste) y detecta:
  - Posición del triángulo del jugador dentro de ese recorte (normalizada 0-1)
  - Ángulo hacia dónde mira (orientación del triángulo)

Esto es 100% lectura de pantalla -- el juego ya le muestra esta info al
jugador, acá solo la extraemos para poder redibujarla en otro lugar/tamaño.

Requiere: opencv-python, numpy, mss
"""

import numpy as np
import threading

from vision.native_lock import NATIVE_LOCK
from vision.screen_capture import capture_region, get_primary_monitor

# cv2 (OpenCV) es una librería nativa -- en esta misma máquina, antes, otra
# librería nativa (numba) fue bloqueada por el Control de Aplicaciones de
# Windows (WDAC). Por eso el import va protegido: si cv2 no carga, este
# módulo queda "apagado" (MINIMAP_AVAILABLE=False) en vez de tumbar TODO el
# programa apenas arranca -- este módulo se importa desde main.py antes de
# crear la ventana, así que sin esta protección un cv2 bloqueado cerraba el
# programa al toque, sin ninguna chance de mostrar un error.
try:
    import cv2
    # El pipeline tiene varios detectores Python; limitar OpenCV a un único
    # worker interno reduce pools nativos y evita sobre-paralelismo en Windows.
    try:
        cv2.setNumThreads(1)
        cv2.ocl.setUseOpenCL(False)
    except Exception:
        pass
    MINIMAP_AVAILABLE = True
except ImportError as e:
    cv2 = None
    MINIMAP_AVAILABLE = False
    print(f"[minimap_reader] No se pudo cargar cv2/OpenCV ({type(e).__name__}: {e}). "
          f"La lectura del minimapa nativo (flecha de posición/orientación) "
          f"queda desactivada -- el resto del programa sigue funcionando normal.")

# ---------------------------------------------------------------------------
# CALIBRACIÓN: la región del minimapa se calcula como PORCENTAJE de tu
# pantalla (no píxeles fijos), así funciona sin importar tu resolución.
# Los valores por defecto están medidos sobre una captura real a 1280x720
# (esquina superior izquierda, aprox. 3%-14% del ancho, 8%-30% del alto).
# Si en tu pantalla el minimapa no cae justo ahí, ajustá estos porcentajes
# con tools/calibrate_region.py (mucho más fácil que calcular píxeles a mano).
# ---------------------------------------------------------------------------
MINIMAP_REGION_FRACTIONS = {
    # Medido sobre tu grabación: la caja del minimapa va de x=35 a 182 e
    # y=83 a 229 en un video de 1280x720 (marco incluido).
    "left": 0.027, "top": 0.114, "width": 0.116, "height": 0.206,
}


def _region_from_fractions(fractions: dict) -> dict:
    """Convierte fracciones de pantalla en una región del monitor primario."""
    monitor = get_primary_monitor()
    return {
        "left": monitor["left"] + int(fractions["left"] * monitor["width"]),
        "top": monitor["top"] + int(fractions["top"] * monitor["height"]),
        "width": max(1, int(fractions["width"] * monitor["width"])),
        "height": max(1, int(fractions["height"] * monitor["height"])),
    }


# La región se calcula de forma perezosa en la primera captura. Calcularla
# durante el import hacía que el worker muriera antes de arrancar si MSS no
# podía inicializarse aún o si su API cambiaba entre versiones.
MINIMAP_REGION: dict | None = None
_MINIMAP_REGION_LOCK = threading.Lock()


def get_minimap_region() -> dict:
    global MINIMAP_REGION
    if MINIMAP_REGION is None:
        with _MINIMAP_REGION_LOCK:
            if MINIMAP_REGION is None:
                MINIMAP_REGION = _region_from_fractions(MINIMAP_REGION_FRACTIONS)
    return dict(MINIMAP_REGION)

# Rango de color HSV del marcador del jugador (el cono celeste que se ve
# debajo del ícono de personaje en el minimapa nativo). Medido sobre una
# captura real -- si tu juego lo muestra con otro tono/brillo (distinto
# equipo, distinto gamma), ajustá con tools/calibrate_region.py.
PLAYER_MARKER_HSV_LOW = np.array([85, 70, 90])
PLAYER_MARKER_HSV_HIGH = np.array([110, 255, 255])

MIN_MARKER_AREA = 4  # el marcador es chico -- píxeles mínimos de contorno


def capture_minimap(region: dict | None = None) -> np.ndarray:
    """Captura el minimapa pasando por el mismo lock/validación global."""
    target = region if region is not None else get_minimap_region()
    return capture_region(target)


def find_player_marker(minimap_bgra: np.ndarray) -> tuple[float, float, float] | None:
    """
    Devuelve (x_norm, y_norm, angle_deg) o None si no se detecta el marcador.
    x_norm, y_norm: posición dentro del recorte del minimapa, 0.0 a 1.0
    angle_deg: orientación aproximada del triángulo (0 = arriba/norte)

    Si cv2 no está disponible en esta máquina, no hay forma de procesar la
    imagen del minimapa -- devuelve None en vez de intentar usar un cv2
    inexistente.
    """
    if not MINIMAP_AVAILABLE:
        return None
    if minimap_bgra is None or getattr(minimap_bgra, "size", 0) == 0 or minimap_bgra.ndim != 3:
        return None
    try:
        with NATIVE_LOCK:
            bgr = cv2.cvtColor(minimap_bgra, cv2.COLOR_BGRA2BGR)
            hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, PLAYER_MARKER_HSV_LOW, PLAYER_MARKER_HSV_HIGH)
            # Une pequeñas zonas fragmentadas por antialiasing/compresión.
            mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                return None
            largest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest) < MIN_MARKER_AREA:
                return None
            h, w = mask.shape[:2]
            M = cv2.moments(largest)
            if M["m00"] == 0:
                return None
            cx = M["m10"] / M["m00"]
            cy = M["m01"] / M["m00"]
            angle_deg = _estimate_triangle_orientation(largest, (cx, cy))
            return (cx / w, cy / h, angle_deg)
    except Exception as exc:
        # El loop dueño decide cuándo reintentar; no dejar excepciones
        # originadas en OpenCV salir del callback del detector.
        print(f"[minimap_reader] Falló el procesado OpenCV: {type(exc).__name__}: {exc}")
        return None


def _estimate_triangle_orientation(contour, center: tuple[float, float]) -> float:
    """
    Aproxima la dirección hacia donde apunta el triángulo: el vértice más
    alejado del centroide suele ser la "punta" (dirección de la mirada).
    Devuelve ángulo en grados, 0 = arriba (norte), sentido horario.
    """
    cx, cy = center
    points = contour.reshape(-1, 2)
    dists = np.sum((points - np.array([cx, cy])) ** 2, axis=1)
    tip = points[np.argmax(dists)]

    dx = tip[0] - cx
    dy = tip[1] - cy
    angle_rad = np.arctan2(dx, -dy)  # -dy porque en imagen Y crece hacia abajo
    return float(np.degrees(angle_rad)) % 360


def run_minimap_loop(on_update, region: dict = None, interval_s: float = 0.1):
    """
    on_update(x_norm, y_norm, angle_deg) se llama en cada detección exitosa.
    Pensado para correr en un thread separado, igual que el de audio.

    Resiliente a errores transitorios (ej. un frame corrupto de captura):
    los loguea una vez y sigue, en vez de morir silenciosamente y dejar el
    marcador "pegado" en la última posición detectada.
    """
    import time
    error_count = 0
    while True:
        try:
            frame = capture_minimap(region)
            if frame is not None and frame.size:
                result = find_player_marker(frame)
                if result:
                    on_update(*result)
            error_count = 0
        except Exception as e:
            error_count += 1
            if error_count <= 3 or error_count % 100 == 0:
                print(f"[minimap_reader] Error leyendo el minimapa (reintento {error_count}): {type(e).__name__}: {e}")
            time.sleep(min(1.0, max(interval_s, 0.15)))
            continue
        time.sleep(max(0.02, interval_s))


def run_minimap_stream(on_frame, region: dict = None, interval_s: float = 0.1):
    """
    Captura el minimapa nativo y le pasa cada frame (numpy BGRA) a
    on_frame(frame). Sirve para redibujarlo AMPLIADO en el panel de F2.

    Por qué no se calcula una posición: el minimapa del juego está centrado
    en el jugador y rota con la mirada (la flecha azul siempre queda en
    ~(0.51, 0.51) y apunta arriba). Verificado sobre tu video: el marcador
    se detecta bien, pero su posición nunca cambia, así que no aporta nada
    para ubicarte sobre un plano fijo.
    """
    import time
    error_count = 0
    while True:
        try:
            frame = capture_minimap(region)
            if frame is not None and frame.size:
                on_frame(frame)
            error_count = 0
        except Exception as e:
            error_count += 1
            if error_count <= 3 or error_count % 100 == 0:
                print(f"[minimap_reader] Error capturando el minimapa (reintento {error_count}): {type(e).__name__}: {e}")
            time.sleep(min(1.0, max(interval_s, 0.15)))
            continue
        time.sleep(max(0.02, interval_s))
