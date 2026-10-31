"""
Lee por OCR tu PROPIO operador en la pantalla donde lo elegís (el nombre
grande que el juego muestra junto al retrato, antes de que arranque la
ronda) -- reemplaza tener que fijarlo a mano con F6.

Por qué esto SÍ es confiable y la fila de 5 compañeros (team_ocr.py) no lo
era para identificar "cuál sos vos": acá no hay que adivinar cuál de 5
columnas te corresponde -- es una sola pantalla, con un solo nombre grande,
exactamente el mismo patrón que ya usa vision/map_ocr.py para el nombre
del mapa (texto grande, aparece una vez, se compara por similitud contra
la lista conocida de operadores).

F6 se mantiene como respaldo manual -- por si esta pantalla no te calza en
tu resolución, o elegís rápido y no te da tiempo a leerla.

Requiere Tesseract, igual que floor_ocr.py/map_ocr.py/team_ocr.py -- si no
está disponible, este módulo se apaga solo sin romper el resto.
"""

import difflib
import re

from vision.screen_capture import capture_region
from vision.minimap_reader import _region_from_fractions
from vision.native_lock import NATIVE_LOCK
from data.gadgets import ALL_OPERATORS

try:
    import pytesseract
    from vision.tesseract_setup import configure_tesseract
    TESSERACT_AVAILABLE = configure_tesseract()
except ImportError:
    TESSERACT_AVAILABLE = False


# Placeholder -- sin calibrar todavía. Correr con la pantalla de selección
# de TU operador visible (antes de arrancar la ronda, donde se ve tu
# retrato y nombre grande):
#   python -m tools.calibrate_region my_operator
MY_OPERATOR_REGION_FRACTIONS = {
    "left": 0.40, "top": 0.85, "width": 0.20, "height": 0.08,
}
MY_OPERATOR_REGION = _region_from_fractions(MY_OPERATOR_REGION_FRACTIONS)

_NORMALIZED_OPS = {op: re.sub(r"[^a-z]", "", op.lower()) for op in ALL_OPERATORS}
MIN_CONFIDENCE = 0.75


def _match_operator_name(raw_text: str) -> str | None:
    cleaned = re.sub(r"[^a-z]", "", raw_text.lower())
    if len(cleaned) < 3:
        return None
    best_op, best_score = None, 0.0
    for op, norm in _NORMALIZED_OPS.items():
        score = difflib.SequenceMatcher(None, cleaned, norm).ratio()
        if score > best_score:
            best_op, best_score = op, score
    return best_op if best_score >= MIN_CONFIDENCE else None


def detect_my_operator(region: dict = None) -> str | None:
    """Devuelve tu operador reconocido en este frame, o None si no hay
    texto reconocible o no calza con confianza contra ningún operador
    conocido."""
    if not TESSERACT_AVAILABLE:
        return None
    region = region or MY_OPERATOR_REGION
    frame = capture_region(region)
    if frame is None or getattr(frame, "size", 0) == 0 or frame.ndim != 3:
        return None
    bgr = frame[:, :, :3]
    with NATIVE_LOCK:
        raw_text = pytesseract.image_to_string(bgr, config="--psm 7")
    result = _match_operator_name(raw_text)
    cleaned = raw_text.strip()
    if cleaned:
        print(f"[my_operator_ocr] texto leído: '{cleaned}' -> "
              f"{'match: ' + result if result else 'sin coincidencia confiable'}", flush=True)
    return result


def run_my_operator_detection_loop(on_operator_detected, region: dict = None,
                                   interval_s: float = 1.0, reset_after_s: float = 10.0):
    """Detecta el operador propio y mantiene F6 como corrección manual."""
    import time
    if not TESSERACT_AVAILABLE:
        print("[my_operator_ocr] Tesseract no disponible; se conserva F6 como respaldo.")
        return
    region = region or MY_OPERATOR_REGION
    last_detected = None
    last_seen_at = 0.0
    errors = 0
    while True:
        try:
            name = detect_my_operator(region)
            errors = 0
            now = time.time()
            if name:
                if name != last_detected:
                    on_operator_detected(name)
                    last_detected = name
                last_seen_at = now
            elif last_detected and now - last_seen_at > reset_after_s:
                last_detected = None
        except Exception as e:
            errors += 1
            if errors <= 3 or errors % 100 == 0:
                print(f"[my_operator_ocr] Error transitorio (reintento {errors}): {type(e).__name__}: {e}")
            time.sleep(min(1.0, max(interval_s, 0.2)))
            continue
        time.sleep(max(0.05, interval_s))

