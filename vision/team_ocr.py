"""
Reconoce a tus COMPAÑEROS de equipo en la fase de preparación -- la fila
con los 5 integrantes de TU equipo y el operador que cada uno eligió, que
el juego le muestra a todo el equipo (nunca información del enemigo). Es
lectura de pantalla, igual que floor_ocr.py y map_ocr.py: nunca se lee
memoria del proceso.

Reemplaza tener que ciclar con F6 el operador de cada compañero a mano
(F6 sigue estando para fijar/corregir el TUYO, porque tu propio nombre de
operador no siempre es legible en pantalla de forma confiable -- pero el
de tus compañeros sí, porque el juego lo escribe/muestra al lado de cada
nombre).

LAYOUT REAL (confirmado con una captura de la fase de preparación): es
una FRANJA HORIZONTAL abajo de la pantalla con 5 COLUMNAS, una por
integrante -- cada columna tiene el ícono del operador junto a su nombre
("MELUSI", "VIGIL", "MUTE", "THUNDERBIRD", "ELA" en el ejemplo visto) y,
debajo, el nombre de usuario. Antes esto asumía una lista VERTICAL a la
izquierda -- era una estimación equivocada, corregida con la captura real.

Combina DOS lecturas independientes por columna:
  1. Ícono: compara el emblema junto al nombre contra los 77 íconos de
     referencia en assets/ui/badges/ (ver vision/operator_icon_match.py)
     -- no necesita Tesseract instalado, y si cv2 no cargó en esta
     máquina, esta vía simplemente no aporta nada (no rompe el resto).
  2. Texto: OCR del nombre escrito al lado, comparado por similitud
     contra data.gadgets.ALL_OPERATORS para tolerar errores.
Si el ícono da una coincidencia confiable se usa esa (más estable que el
texto a esta escala); si no, se cae al texto. Una columna que no calza
con confianza en NINGUNO de los dos se descarta en vez de adivinar.

La región sigue siendo una ESTIMACIÓN (coordenadas de una captura a
1920x1080 -- en otra resolución o si Ubisoft reordena el HUD puede no
coincidir). Si en tu pantalla no cae justo ahí, ajustala con:
    python -m tools.calibrate_region team_sidebar
"""

import difflib
import re

from vision.screen_capture import capture_region
from vision.minimap_reader import _region_from_fractions
from vision.operator_icon_match import match_icon, MIN_CONFIDENCE as ICON_MIN_CONFIDENCE
from vision.native_lock import NATIVE_LOCK
from data.gadgets import ALL_OPERATORS

try:
    import pytesseract
    from vision.tesseract_setup import configure_tesseract
    TESSERACT_AVAILABLE = configure_tesseract()
except ImportError:
    TESSERACT_AVAILABLE = False


# Calibrado por el usuario con tools/calibrate_region.py (clave
# "team_sidebar") sobre su propia pantalla/HUD -- reemplaza la estimación
# original, que no calzaba (el OCR leía basura/texto del HUD de juego en
# vez de la fila de equipo). El nombre de la clave quedó igual aunque es
# una franja horizontal, no una sidebar. Si deja de calzar (Ubisoft cambia
# el HUD), recalibrar con:
#   python -m tools.calibrate_region team_sidebar
TEAM_SIDEBAR_REGION_FRACTIONS = {
    "left": 0.0312, "top": 0.6778, "width": 0.9333, "height": 0.0593,
}
TEAM_SIDEBAR_REGION = _region_from_fractions(TEAM_SIDEBAR_REGION_FRACTIONS)

# 5 integrantes = 5 columnas, una al lado de la otra.
NUM_COLS = 5
# Qué fracción del ancho de cada columna ocupa el ícono (el resto es texto).
ICON_WIDTH_FRACTION = 0.22

# Subido de 0.75 a 0.86 -- un log real mostró un falso positivo ("Sens")
# a partir de texto basura de 5 caracteres leído FUERA de la fila de
# equipo (esta región también lee mensajes de chat/ping del juego cuando
# no está la fase de preparación en pantalla). difflib.SequenceMatcher es
# propenso a coincidencias altas por pura casualidad con strings cortos,
# así que además exigimos más caracteres mínimos (antes 3, ahora 4).
TEXT_MIN_CONFIDENCE = 0.86
_NORMALIZED_OPS = {op: re.sub(r"[^a-z]", "", op.lower()) for op in ALL_OPERATORS}


def _match_operator_text(raw_line: str) -> str | None:
    cleaned = re.sub(r"[^a-z]", "", raw_line.lower())
    if len(cleaned) < 4:
        return None
    best_op, best_score = None, 0.0
    for op, norm in _NORMALIZED_OPS.items():
        score = difflib.SequenceMatcher(None, cleaned, norm).ratio()
        if score > best_score:
            best_op, best_score = op, score
    return best_op if best_score >= TEXT_MIN_CONFIDENCE else None


def _detect_column(col_bgr) -> str | None:
    h, w = col_bgr.shape[:2]
    icon_w = max(1, int(w * ICON_WIDTH_FRACTION))

    icon_crop = col_bgr[:, :icon_w]
    icon_result = match_icon(icon_crop)
    if icon_result and icon_result[0] and icon_result[1] >= ICON_MIN_CONFIDENCE:
        return icon_result[0]

    if not TESSERACT_AVAILABLE:
        return None
    text_crop = col_bgr[:, icon_w:]
    # NATIVE_LOCK: ver la nota en vision/floor_ocr.py.
    with NATIVE_LOCK:
        raw_text = pytesseract.image_to_string(text_crop, config="--psm 7")
    result = _match_operator_text(raw_text)
    # Diagnóstico: ver la nota equivalente en vision/map_ocr.py -- sin esto,
    # una columna que no calza queda en silencio total, indistinguible de
    # una región vacía.
    cleaned = raw_text.strip()
    icon_score = f"{icon_result[1]:.2f}" if icon_result and icon_result[0] else "sin ícono"
    if cleaned or (icon_result and icon_result[0]):
        print(f"[team_ocr] columna -- ícono: {icon_result[0] if icon_result else None} "
              f"(score {icon_score}), texto: '{cleaned}' -> "
              f"{'match: ' + result if result else 'sin coincidencia confiable'}", flush=True)
    return result


def detect_team_operators(region: dict = None) -> list[str]:
    """Devuelve los operadores reconocidos en la fila, sin duplicados, en
    el orden en que aparecen (columna por columna, de izquierda a
    derecha). Puede devolver menos de 5 si todavía no todos eligieron o
    si alguna columna no se pudo leer con confianza por ninguno de los
    dos métodos -- nunca completa los que faltan con una adivinanza."""
    region = region or TEAM_SIDEBAR_REGION
    frame = capture_region(region)
    if frame is None or getattr(frame, "size", 0) == 0 or frame.ndim != 3:
        return []
    bgr = frame[:, :, :3]
    h, w = bgr.shape[:2]
    col_w = w // NUM_COLS

    found: list[str] = []
    for i in range(NUM_COLS):
        col = bgr[:, i * col_w: (i + 1) * col_w]
        if col.size == 0:
            continue
        op = _detect_column(col)
        if op and op not in found:
            found.append(op)
    return found


def run_team_detection_loop(on_team_update, region: dict = TEAM_SIDEBAR_REGION, interval_s: float = 2.0):
    """Actualiza operadores detectados y reintenta después de capturas transitorias."""
    import time
    last_found: list[str] = []
    errors = 0
    while True:
        try:
            found = detect_team_operators(region)
            errors = 0
            if found != last_found and found:
                on_team_update(found)
                last_found = found
        except Exception as e:
            errors += 1
            if errors <= 3 or errors % 100 == 0:
                print(f"[team_ocr] Error transitorio leyendo el equipo (reintento {errors}): {type(e).__name__}: {e}")
            time.sleep(min(1.0, max(interval_s, 0.25)))
            continue
        time.sleep(max(0.1, interval_s))

