"""
Lee por OCR el nombre del mapa que el juego muestra en pantalla durante la
selección/baneo de mapa y la carga de partida (texto grande, antes de que
arranque la fase de preparación). Es lectura de pantalla, no de memoria:
el mismo texto que ya ve el jugador.

Por qué esto NO es continuo: ese texto solo aparece en esa pantalla
puntual, no vuelve a mostrarse durante el resto de la ronda (el HUD en
juego no repite el nombre del mapa). Por eso esto funciona como un
"detector de aparición": apenas reconoce un nombre de mapa válido avisa
una vez, y deja de insistir hasta que la pantalla deje de verse (ver
`run_map_detection_loop`) en vez de reintentar sin sentido contra el HUD
de juego.

Como esta pantalla puede variar de layout entre temporadas/resoluciones,
la región es una ESTIMACIÓN (franja superior-central, donde R6 viene
mostrando el nombre del mapa en las últimas temporadas) y el texto
reconocido se compara por SIMILITUD contra data.map_calibration.ALL_MAPS
en vez de exigir una coincidencia exacta (para tolerar errores de OCR).
Si no calza con suficiente confianza contra ningún mapa conocido, se
descarta el frame en vez de adivinar: es mejor no detectar que detectar
mal y mostrar un mapa equivocado.

Si en tu resolución/temporada el nombre no aparece en esa franja, ajustá
la región con:
    python -m tools.calibrate_region map_name
"""

import difflib
import re

from vision.screen_capture import capture_region
from vision.minimap_reader import _region_from_fractions
from vision.native_lock import NATIVE_LOCK
from data.map_calibration import ALL_MAPS

try:
    import pytesseract
    from vision.tesseract_setup import configure_tesseract
    TESSERACT_AVAILABLE = configure_tesseract()
except ImportError:
    TESSERACT_AVAILABLE = False


# Calibrado por el usuario con tools/calibrate_region.py (clave "map_name")
# sobre su propia pantalla/HUD -- reemplaza la estimación original, que no
# calzaba con su resolución/temporada (el OCR leía basura). Si en algún
# momento deja de calzar de nuevo (Ubisoft cambia el HUD), recalibrar con:
#   python -m tools.calibrate_region map_name
MAP_NAME_REGION_FRACTIONS = {
    "left": 0.3156, "top": 0.2509, "width": 0.4042, "height": 0.0889,
}
MAP_NAME_REGION = _region_from_fractions(MAP_NAME_REGION_FRACTIONS)

_NORMALIZED_MAPS = {m: re.sub(r"[^a-z0-9]", "", m.lower()) for m in ALL_MAPS}

# Similitud mínima (0-1) para aceptar una lectura. Más alto = menos falsos
# positivos pero puede ignorar lecturas con ruido de OCR; más bajo = al
# revés. 0.72 tolera 1-2 letras mal leídas en nombres cortos.
MIN_CONFIDENCE = 0.72


def _match_map_name(raw_text: str) -> str | None:
    cleaned = re.sub(r"[^a-z0-9]", "", raw_text.lower())
    if len(cleaned) < 3:
        return None
    best_map, best_score = None, 0.0
    for map_name, norm in _NORMALIZED_MAPS.items():
        score = difflib.SequenceMatcher(None, cleaned, norm).ratio()
        if score > best_score:
            best_map, best_score = map_name, score
    return best_map if best_score >= MIN_CONFIDENCE else None


def detect_map_name(region: dict = None) -> str | None:
    """Devuelve el nombre de mapa reconocido en este frame, o None si no
    hay texto reconocible o no calza con confianza contra ningún mapa
    conocido (nunca "adivina" un mapa de baja confianza)."""
    if not TESSERACT_AVAILABLE:
        return None
    region = region or MAP_NAME_REGION
    frame = capture_region(region)
    if frame is None or getattr(frame, "size", 0) == 0 or frame.ndim != 3:
        return None
    bgr = frame[:, :, :3]
    # NATIVE_LOCK: ver la nota en vision/floor_ocr.py -- pytesseract no
    # debe correr a la vez que otro hilo también lo esté usando.
    with NATIVE_LOCK:
        raw_text = pytesseract.image_to_string(bgr, config="--psm 7")  # una línea
    result = _match_map_name(raw_text)
    # Diagnóstico: un intento fallido antes se callaba en silencio -- sin
    # esto no hay forma de saber si la región está vacía/mal calibrada o
    # si está leyendo texto real que no llega a calzar con ningún mapa
    # conocido (que son dos problemas distintos con arreglos distintos).
    cleaned = raw_text.strip()
    if cleaned:
        print(f"[map_ocr] texto leído: '{cleaned}' -> "
              f"{'match: ' + result if result else 'sin coincidencia confiable'}", flush=True)
    return result


def run_map_detection_loop(on_map_detected, region: dict = MAP_NAME_REGION,
                           interval_s: float = 1.0, reset_after_s: float = 10.0):
    """Detecta mapas de la pantalla de carga, tolerando frames vacíos y DirectX."""
    import time
    if not TESSERACT_AVAILABLE:
        print("[map_ocr] Tesseract no disponible; el mapa se puede cambiar con F4.")
        return
    region = region or MAP_NAME_REGION
    last_detected = None
    last_seen_at = 0.0
    errors = 0
    while True:
        try:
            name = detect_map_name(region)
            errors = 0
            now = time.time()
            if name:
                if name != last_detected:
                    on_map_detected(name)
                    last_detected = name
                last_seen_at = now
            elif last_detected and now - last_seen_at > reset_after_s:
                last_detected = None
        except Exception as e:
            errors += 1
            if errors <= 3 or errors % 100 == 0:
                print(f"[map_ocr] Error transitorio (reintento {errors}): {type(e).__name__}: {e}")
            time.sleep(min(1.0, max(interval_s, 0.2)))
            continue
        time.sleep(max(0.05, interval_s))

