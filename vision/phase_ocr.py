"""Detecta el cartel de inicio de la fase de preparación usando solo pantalla."""

import re
import time
import unicodedata

from vision.screen_capture import capture_region
from vision.minimap_reader import _region_from_fractions
from vision.native_lock import NATIVE_LOCK

try:
    import cv2
    import pytesseract
    from vision.tesseract_setup import configure_tesseract
    TESSERACT_AVAILABLE = configure_tesseract()
except ImportError:
    cv2 = None
    pytesseract = None
    TESSERACT_AVAILABLE = False


# El título "FASE DE PREPARACIÓN" aparece centrado, por encima del punto de mira.
PREPARATION_REGION = _region_from_fractions({
    "left": 0.34, "top": 0.25, "width": 0.32, "height": 0.14,
})


def detect_preparation_banner() -> bool:
    if not TESSERACT_AVAILABLE:
        return False
    frame = capture_region(PREPARATION_REGION)
    if frame is None or getattr(frame, "size", 0) == 0 or frame.ndim != 3:
        return False
    gray = cv2.cvtColor(frame[:, :, :3], cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    with NATIVE_LOCK:
        text = pytesseract.image_to_string(binary, config="--psm 6")
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower()
    compact = re.sub(r"[^a-z]", "", normalized)
    return "prepar" in compact or "fortific" in compact


def run_preparation_detection_loop(on_round_start, interval_s: float = 0.45):
    if not TESSERACT_AVAILABLE:
        print("[phase_ocr] Tesseract no disponible; se omite la detección del cartel de preparación.", flush=True)
        return
    print("[phase_ocr] OCR activo; buscando el cartel de preparacion en el centro.", flush=True)
    announced = False
    clear_since = time.monotonic()
    errors = 0
    while True:
        try:
            visible = detect_preparation_banner()
            errors = 0
            now = time.monotonic()
            if visible:
                clear_since = now
                if not announced:
                    print("[phase_ocr] Cartel 'Fase de preparación' detectado.", flush=True)
                    on_round_start()
                    announced = True
            else:
                if announced and now - clear_since >= 2.0:
                    announced = False
        except Exception as exc:
            errors += 1
            if errors <= 3 or errors % 100 == 0:
                print(f"[phase_ocr] Error transitorio (reintento {errors}): {type(exc).__name__}: {exc}", flush=True)
        time.sleep(max(0.1, interval_s))
