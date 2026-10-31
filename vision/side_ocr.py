"""
Lee por OCR si jugás como Defensor o Atacante en la ronda actual, del
panel "MI EQUIPO <Defensores/Atacantes>" que el juego muestra SOLO al
terminar cada ronda -- a diferencia de otras pantallas, esta aparece
automáticamente, sin que el jugador tenga que apretar Tab, así que sirve
como "detector de aparición" confiable (igual que map_ocr.py).

Reemplaza tener que apretar F5 a mano cada vez que cambia tu lado (al
pasar de ronda en partidas normales, o en cada mitad en rankeds con
mapa dividido) -- F5 sigue disponible como corrección manual.

La región es una ESTIMACIÓN hasta que el usuario la calibre con:
    python -m tools.calibrate_region side
sobre esa pantalla de resumen de ronda (el panel "MI EQUIPO ...").
"""

import difflib
import re

from vision.screen_capture import capture_region
from vision.minimap_reader import _region_from_fractions
from vision.native_lock import NATIVE_LOCK

try:
    import pytesseract
    from vision.tesseract_setup import configure_tesseract
    TESSERACT_AVAILABLE = configure_tesseract()
except ImportError:
    TESSERACT_AVAILABLE = False


# Estimación inicial (franja bajo "MI EQUIPO" en el panel de resumen de
# ronda) -- ajustar con tools/calibrate_region.py (clave "side") apuntando
# justo al texto "Defensores"/"Atacantes" de TU equipo (el de la
# izquierda, "MI EQUIPO", nunca el de "EQUIPO RIVAL").
SIDE_REGION_FRACTIONS = {
    "left": 0.33, "top": 0.21, "width": 0.17, "height": 0.05,
}
SIDE_REGION = _region_from_fractions(SIDE_REGION_FRACTIONS)

_SIDES = ["Defensores", "Atacantes"]
_NORMALIZED_SIDES = {s: re.sub(r"[^a-z]", "", s.lower()) for s in _SIDES}
MIN_CONFIDENCE = 0.72


def _match_side(raw_text: str) -> str | None:
    cleaned = re.sub(r"[^a-z]", "", raw_text.lower())
    if len(cleaned) < 3:
        return None
    best_side, best_score = None, 0.0
    for side, norm in _NORMALIZED_SIDES.items():
        score = difflib.SequenceMatcher(None, cleaned, norm).ratio()
        if score > best_score:
            best_side, best_score = side, score
    return best_side if best_score >= MIN_CONFIDENCE else None


def detect_side(region: dict = None) -> str | None:
    if not TESSERACT_AVAILABLE:
        return None
    region = region or SIDE_REGION
    frame = capture_region(region)
    if frame is None or getattr(frame, "size", 0) == 0 or frame.ndim != 3:
        return None
    bgr = frame[:, :, :3]
    with NATIVE_LOCK:
        raw_text = pytesseract.image_to_string(bgr, config="--psm 7")
    result = _match_side(raw_text)
    cleaned = raw_text.strip()
    if cleaned:
        print(f"[side_ocr] texto leído: '{cleaned}' -> "
              f"{'match: ' + result if result else 'sin coincidencia confiable'}", flush=True)
    return result


def run_side_detection_loop(on_side_detected, region: dict = None, interval_s: float = 1.0,
                            reset_after_s: float = 15.0):
    """Detecta el bando visible en pantalla y reintenta si un frame falla."""
    import time
    if not TESSERACT_AVAILABLE:
        print("[side_ocr] Tesseract no disponible; se conserva F5 como corrección manual.")
        return
    region = region or SIDE_REGION
    last_detected = None
    last_seen_at = 0.0
    errors = 0
    while True:
        try:
            side = detect_side(region)
            errors = 0
            now = time.time()
            if side:
                if side != last_detected:
                    on_side_detected(side)
                    last_detected = side
                last_seen_at = now
            elif last_detected and now - last_seen_at > reset_after_s:
                last_detected = None
        except Exception as e:
            errors += 1
            if errors <= 3 or errors % 100 == 0:
                print(f"[side_ocr] Error transitorio (reintento {errors}): {type(e).__name__}: {e}")
            time.sleep(min(1.0, max(interval_s, 0.2)))
            continue
        time.sleep(max(0.05, interval_s))

