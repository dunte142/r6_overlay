"""
Lee por OCR el indicador de piso que el juego YA muestra en el HUD (visto
en tu propia partida grabada: "P1 Sala de estar", cerca del centro-inferior
de pantalla) y lo traduce al nombre de piso que usa el resto del proyecto
("Primer Piso", "Sotano", etc.).

Esto reemplaza tener que cambiar el piso a mano: el overlay se entera solo
de en qué piso estás porque lee lo mismo que vos ya estás viendo en pantalla.

Requiere: pytesseract + el binario de Tesseract OCR instalado en el sistema
  Windows: https://github.com/UB-Mannheim/tesseract/wiki (instalador .exe)
  Después: pip install pytesseract

Si no tenés Tesseract instalado, este módulo no rompe el resto del proyecto
-- simplemente no va a poder actualizar el piso automáticamente (fallback:
seguís pudiendo fijar CURRENT_FLOOR a mano en main.py).
"""

import re

import numpy as np

from vision.screen_capture import capture_region
from vision.minimap_reader import _region_from_fractions
from vision.native_lock import NATIVE_LOCK

try:
    import pytesseract
    from vision.tesseract_setup import configure_tesseract
    TESSERACT_AVAILABLE = configure_tesseract()
except ImportError:
    TESSERACT_AVAILABLE = False


# Región del indicador de piso, como PORCENTAJE de pantalla (no píxeles
# fijos) -- ver vision/minimap_reader.py para el mismo criterio. Medido
# sobre una captura real donde el HUD mostraba "P1 Sala de estar" cerca
# del centro-inferior de la pantalla. Ajustá con tools/calibrate_region.py
# si en tu resolución no cae justo ahí.
FLOOR_INDICATOR_FRACTIONS = {
    "left": 0.44, "top": 0.80, "width": 0.14, "height": 0.035,
}
FLOOR_INDICATOR_REGION = _region_from_fractions(FLOOR_INDICATOR_FRACTIONS)

# Traduce lo que el juego escribe al nombre de piso que usa el resto del
# proyecto (data/cameras.py, ui/assets.py FLOOR_ICONS). Cubre el formato
# visto en pantalla ("P1 Sala de estar") y variantes comunes por si el
# juego lo muestra distinto en otro idioma/versión.
FLOOR_TEXT_MAP = {
    "PB": "Sotano", "SS": "Sotano", "S": "Sotano", "B": "Sotano",
    "P1": "Primer Piso", "1F": "Primer Piso",
    "P2": "Segundo Piso", "2F": "Segundo Piso", "P3": "Segundo Piso",
    "PT": "Tejado", "T": "Tejado", "RF": "Tejado", "R": "Tejado",
}


def _parse_floor_text(raw_text: str) -> str | None:
    """Extrae el prefijo de piso (P1, PB, T...) del texto reconocido por
    OCR y lo mapea a nuestro nombre de piso interno."""
    cleaned = raw_text.strip().upper()
    match = re.match(r"^(PB|SS|P\d|PT|RF|[SBTR])\b", cleaned)
    if not match:
        return None
    return FLOOR_TEXT_MAP.get(match.group(1))


def detect_current_floor(region: dict = None) -> str | None:
    """Devuelve el nombre de piso detectado (ej. "Primer Piso") o None si
    no se pudo leer nada reconocible en este frame."""
    if not TESSERACT_AVAILABLE:
        return None

    region = region or FLOOR_INDICATOR_REGION
    frame = capture_region(region)
    if frame is None or getattr(frame, "size", 0) == 0 or frame.ndim != 3:
        return None
    bgr = frame[:, :, :3]

    # NATIVE_LOCK: pytesseract spawnea tesseract.exe (subprocess) y lee/
    # escribe archivos temporales -- correrlo a la vez que OTRO hilo hace
    # lo mismo (floor/map/team OCR corren en paralelo) fue una de las
    # causas que apareció en un faulthandler_dump.txt como corrupción de
    # heap. Ver vision/native_lock.py.
    with NATIVE_LOCK:
        raw_text = pytesseract.image_to_string(
            bgr, config="--psm 7"  # psm 7 = una sola línea de texto
        )
    return _parse_floor_text(raw_text)


def run_floor_detection_loop(on_floor_change, region: dict = FLOOR_INDICATOR_REGION, interval_s: float = 1.0):
    """Detecta el piso continuamente y reintenta tras frames/transiciones fallidos."""
    import time
    if not TESSERACT_AVAILABLE:
        print("[floor_ocr] Tesseract no disponible; se conserva el piso manual (F2).")
        return
    last_floor = None
    errors = 0
    while True:
        try:
            floor = detect_current_floor(region)
            errors = 0
            if floor and floor != last_floor:
                on_floor_change(floor)
                last_floor = floor
        except Exception as e:
            errors += 1
            if errors <= 3 or errors % 100 == 0:
                print(f"[floor_ocr] Error transitorio (reintento {errors}): {type(e).__name__}: {e}")
            time.sleep(min(1.0, max(interval_s, 0.2)))
            continue
        time.sleep(max(0.05, interval_s))

