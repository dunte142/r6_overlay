"""
Reconoce operadores por COMPARACIÓN DE ÍCONO contra los badges oficiales
(assets/ui/badges/*.png, extraídos de las fichas de diseño del proyecto),
aplicado sobre una región chica de pantalla que el juego YA te muestra --
pensado para el killfeed (el cartel "Fulano eliminó a Mengano" con el
ícono del operador al lado), que es información que el juego le da a
TODOS los jugadores, nunca algo leído de memoria.

Por qué comparación de imagen y no un modelo entrenado (YOLO, etc.): un
ícono de HUD es un gráfico fijo, siempre igual a sí mismo (no cambia de
ángulo, iluminación o pose como un personaje 3D) -- compararlo contra una
referencia es exacto y no necesita entrenamiento ni miles de capturas.
Esto es justamente lo que SÍ es viable sin entrenar nada; reconocer al
personaje en 3D corriendo por el mapa es un problema distinto y mucho más
grande (ver vision/detector.py).

Qué NO hace: no mira el mundo 3D del juego ni intenta identificar a un
enemigo a través de una pared. Solo compara un recorte de pantalla contra
íconos conocidos, y descarta la lectura si no hay confianza suficiente.
"""

import glob
import os

import numpy as np

from vision.native_lock import NATIVE_LOCK

from vision.screen_capture import capture_region
from vision.minimap_reader import _region_from_fractions

# cv2 (OpenCV) es una librería nativa -- en esta misma máquina, antes, otra
# librería nativa (numba) fue bloqueada por el Control de Aplicaciones de
# Windows. Por eso el import va protegido, igual que pytesseract en
# floor_ocr.py: si cv2 no carga por cualquier motivo, este módulo queda
# "apagado" (ICON_MATCH_AVAILABLE=False) en vez de tumbar TODO el programa
# -- sin esto, una falla acá impedía incluso que se abriera la ventana del
# overlay, porque este módulo se importa antes de crear la QApplication.
try:
    import cv2
    # El pipeline tiene varios detectores Python; limitar OpenCV a un único
    # worker interno reduce pools nativos y evita sobre-paralelismo en Windows.
    try:
        cv2.setNumThreads(1)
        cv2.ocl.setUseOpenCL(False)
    except Exception:
        pass
    ICON_MATCH_AVAILABLE = True
except ImportError as e:
    cv2 = None
    ICON_MATCH_AVAILABLE = False
    print(f"[operator_icon_match] No se pudo cargar cv2/OpenCV ({type(e).__name__}: {e}). "
          f"El reconocimiento de operador por ícono (compañeros y enemigos por killfeed) "
          f"queda desactivado -- el resto del programa sigue funcionando normal.")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BADGES_DIR = os.path.join(PROJECT_ROOT, "assets", "ui", "badges")

# Estimación: el killfeed de R6 aparece arriba a la derecha, debajo del
# timer. Ajustable con tools/calibrate_region.py (clave "killfeed") --
# recortá SOLO el ícono cuadrado del operador en la línea más reciente del
# killfeed, no el texto ni toda la franja.
KILLFEED_ICON_REGION_FRACTIONS = {
    "left": 0.80, "top": 0.10, "width": 0.045, "height": 0.045,
}
KILLFEED_ICON_REGION = _region_from_fractions(KILLFEED_ICON_REGION_FRACTIONS)

# Ícono de habilidad propia en la barra superior de juego -- el juego
# resalta con un recuadro blanco translúcido el ícono del gadget especial
# de TU operador (distinto del resto de la barra), y ese ícono es el mismo
# gráfico que los badges de assets/ui/badges/ -- así que se puede leer con
# la misma comparación de imagen, sin inventar un reconocedor nuevo.
# Reemplaza tener que elegir tu propio operador a mano con F6 (que sigue
# disponible como corrección manual si esto lee mal).
# Calibrado por el usuario con tools/calibrate_region.py (clave
# "my_operator") sobre su propia pantalla -- si deja de calzar (Ubisoft
# cambia el HUD), recalibrar con:
#   python -m tools.calibrate_region my_operator
MY_OPERATOR_ICON_REGION_FRACTIONS = {
    "left": 0.3922, "top": 0.0047, "width": 0.0292, "height": 0.0510,
}
MY_OPERATOR_ICON_REGION = _region_from_fractions(MY_OPERATOR_ICON_REGION_FRACTIONS)

# Cinco posiciones del equipo rival en la franja superior del HUD. Solo se
# aceptan iconos realmente revelados; las casillas con "?" no producen match.
ENEMY_ROSTER_REGION_FRACTIONS = {
    "left": 0.5781, "top": 0.0047, "width": 0.1303, "height": 0.0510,
}
ENEMY_ROSTER_REGION = _region_from_fractions(ENEMY_ROSTER_REGION_FRACTIONS)

# La fila azul del HUD conserva los cinco operadores aliados durante la ronda.
TEAM_ROSTER_REGION_FRACTIONS = {
    "left": 0.2917, "top": 0.0047, "width": 0.1303, "height": 0.0510,
}
TEAM_ROSTER_REGION = _region_from_fractions(TEAM_ROSTER_REGION_FRACTIONS)

MIN_CONFIDENCE = 0.55  # umbral de correlación normalizada (0-1) para aceptar una lectura


ROSTER_MIN_CONFIDENCE = 0.68


def _load_templates() -> dict[str, np.ndarray]:
    """Carga cada badge como imagen en escala de grises (una sola vez al
    importar el módulo). Devuelve {nombre_operador: array_gris}. Si algo
    falla a mitad de camino (un archivo corrupto, sin permisos, etc.), se
    loguea y se sigue con los badges que sí cargaron en vez de abortar
    todo -- un ícono roto no debería tumbar los otros 76."""
    templates = {}
    if not ICON_MATCH_AVAILABLE:
        return templates
    try:
        paths = sorted(glob.glob(os.path.join(BADGES_DIR, "*.png")))
    except Exception as e:
        print(f"[operator_icon_match] No se pudo listar {BADGES_DIR}: {type(e).__name__}: {e}")
        return templates

    for path in paths:
        try:
            with NATIVE_LOCK:
                name = os.path.splitext(os.path.basename(path))[0].replace("_", " ")
                img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                if img is None or img.size == 0 or img.ndim < 2:
                    continue
                if img.ndim == 3 and img.shape[2] == 4:
                    # Aplanar transparencia para comparar con frames opacos.
                    bgr = img[:, :, :3].astype(np.float32)
                    alpha = img[:, :, 3:4].astype(np.float32) / 255.0
                    bg = np.full_like(bgr, 60.0)
                    flat = (bgr * alpha + bg * (1 - alpha)).astype(np.uint8)
                elif img.ndim == 3:
                    flat = img[:, :, :3]
                else:
                    flat = img
                gray = cv2.cvtColor(flat, cv2.COLOR_BGR2GRAY) if flat.ndim == 3 else flat.copy()
                if gray.size:
                    templates[name] = gray
        except Exception as e:
            print(f"[operator_icon_match] No se pudo cargar '{path}': {type(e).__name__}: {e}")
    return templates


_TEMPLATES = _load_templates()
if ICON_MATCH_AVAILABLE and not _TEMPLATES:
    print("[operator_icon_match] cv2 cargó pero no se pudo leer ningún ícono de "
          f"{BADGES_DIR} -- revisá que la carpeta assets/ui/badges/ viajó completa "
          "en el .zip. El reconocimiento por ícono no va a detectar nada hasta que esté.")


# CAUSA REAL del crash que costó varias vueltas de diagnóstico: esta
# función se llama desde DOS hilos distintos al mismo tiempo --
# vision/team_ocr.py (detección de compañeros) Y run_icon_watch_loop acá
# abajo (ícono del killfeed) -- y ambos usan OpenCV (cv2.resize,
# cv2.matchTemplate, cv2.cvtColor) sobre los mismos templates compartidos.
# OpenCV no garantiza que sea seguro llamarlo así, concurrentemente desde
# dos threads de Python sin coordinación -- en la máquina del usuario esto
# terminó corrompiendo el heap del proceso entero (Windows lo reportó como
# "Windows fatal exception: code 0xc0000374", STATUS_HEAP_CORRUPTION, vía
# faulthandler) un instante después, en código completamente distinto --
# por eso el crash parecía "aleatorio" y sin relación con su causa real.
#
# Usa el lock NATIVO global (vision/native_lock.py), compartido con
# pytesseract -- no solo con las otras llamadas a OpenCV. Un lock propio
# de este módulo alcanzaba para que dos comparaciones de ícono no corrieran
# a la vez entre sí, pero el crash siguió pasando con ese lock puesto (lo
# confirmó un faulthandler_dump.txt posterior, apuntando esta vez a la
# inicialización de audio) -- así que el lock se amplió para cubrir
# CUALQUIER llamada nativa (OpenCV o Tesseract), no solo esta función.


def match_operator_icon(frame_bgra: np.ndarray, min_confidence: float = MIN_CONFIDENCE,
                        search: bool = False) -> tuple[str | None, float]:
    """
    Compara un recorte de pantalla (el ícono solo, ya recortado -- ver
    KILLFEED_ICON_REGION) contra todos los badges conocidos. Devuelve
    (nombre, confianza) del mejor match, o (None, confianza) si ninguno
    supera `min_confidence` -- nunca "adivina" el más parecido si ese
    parecido es bajo.
    """
    if not _TEMPLATES or frame_bgra is None or getattr(frame_bgra, "size", 0) == 0:
        return None, 0.0
    if getattr(frame_bgra, "ndim", 0) != 3 or frame_bgra.shape[0] < 2 or frame_bgra.shape[1] < 2:
        return None, 0.0

    with NATIVE_LOCK:
        bgr = frame_bgra[:, :, :3] if frame_bgra.shape[2] == 4 else frame_bgra
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        best_name, best_score = None, -1.0
        for name, template in _TEMPLATES.items():
            if template is None or template.size == 0:
                continue
            if search:
                max_side = min(gray.shape[:2])
                min_side = max(22, int(max_side * 0.58))
                candidate_sides = list(range(min_side, max_side + 1, 2))
                if not candidate_sides or candidate_sides[-1] != max_side:
                    candidate_sides.append(max_side)
            else:
                candidate_sides = [min(gray.shape[1], gray.shape[0])]
            for side in candidate_sides:
                interpolation = cv2.INTER_AREA if side < template.shape[0] else cv2.INTER_LINEAR
                if search:
                    resized = cv2.resize(template, (side, side), interpolation=interpolation)
                else:
                    resized = cv2.resize(template, (gray.shape[1], gray.shape[0]), interpolation=interpolation)
                result = cv2.matchTemplate(gray, resized, cv2.TM_CCOEFF_NORMED)
                score = float(result.max())
                if score > best_score:
                    best_name, best_score = name, score

    if best_score >= min_confidence:
        return best_name, best_score
    return None, best_score


def run_enemy_roster_watch_loop(on_operator_seen, region: dict = None,
                                interval_s: float = 1.0):
    """Lee iconos rivales revelados en las cinco casillas del HUD superior."""
    import time
    region = region or ENEMY_ROSTER_REGION
    last_by_slot: list[str | None] = [None] * 5
    while True:
        try:
            frame = capture_region(region)
            if frame is None or getattr(frame, "size", 0) == 0 or frame.ndim != 3:
                time.sleep(max(0.1, interval_s))
                continue
            slot_width = frame.shape[1] / 5
            for index in range(5):
                x1 = int(index * slot_width)
                x2 = int((index + 1) * slot_width)
                slot = frame[:, x1:x2]
                name, _score = match_operator_icon(
                    slot, min_confidence=ROSTER_MIN_CONFIDENCE, search=True,
                )
                if name and name != last_by_slot[index]:
                    last_by_slot[index] = name
                    on_operator_seen(name)
        except Exception as exc:
            print(f"[operator_icon_match] Error leyendo la fila rival; se reintenta: {type(exc).__name__}: {exc}")
        time.sleep(max(0.1, interval_s))


def run_team_roster_watch_loop(on_roster_seen, region: dict = None,
                               interval_s: float = 1.0):
    """Lee los cinco iconos aliados de la fila azul superior durante la ronda."""
    import time
    region = region or TEAM_ROSTER_REGION
    last_roster: tuple[str | None, ...] | None = None
    while True:
        try:
            frame = capture_region(region)
            if frame is None or getattr(frame, "size", 0) == 0 or frame.ndim != 3:
                time.sleep(max(0.1, interval_s))
                continue
            slot_width = frame.shape[1] / 5
            roster = []
            for index in range(5):
                slot = frame[:, int(index * slot_width):int((index + 1) * slot_width)]
                name, _score = match_operator_icon(
                    slot, min_confidence=ROSTER_MIN_CONFIDENCE, search=True,
                )
                roster.append(name)
            current = tuple(roster)
            if current != last_roster:
                last_roster = current
                on_roster_seen([name for name in roster if name])
        except Exception as exc:
            print(f"[operator_icon_match] Error leyendo la fila aliada; se reintenta: {type(exc).__name__}: {exc}")
        time.sleep(max(0.1, interval_s))


# Alias corto -- vision/team_ocr.py compara el ícono de cada fila de la
# barra de preparación contra estos mismos badges antes de caer a OCR de
# texto, y lo importa con este nombre.
match_icon = match_operator_icon


def run_icon_watch_loop(on_operator_seen, region: dict = None, interval_s: float = 0.5,
                        cooldown_s: float = 2.0, search: bool = False,
                        min_confidence: float = MIN_CONFIDENCE):
    """
    on_operator_seen(name) se llama cuando el ícono recortado calza con
    confianza contra un operador conocido Y no se avisó el mismo operador
    en los últimos `cooldown_s` segundos (para no repetir el mismo aviso
    mientras ese ícono sigue en pantalla).

    No distingue por sí solo si el ícono visto es de un ENEMIGO o de un
    COMPAÑERO -- eso depende de qué región calibraste (killfeed de
    enemigos derribados vs. tu propia lista de equipo). Quien conecte este
    loop decide qué hacer con el nombre recibido.
    """
    import time
    region = region or KILLFEED_ICON_REGION
    last_name = None
    last_time = 0.0

    while True:
        try:
            frame = capture_region(region)
            name, score = match_operator_icon(frame, min_confidence=min_confidence, search=search)
        except Exception as e:
            print(f"[operator_icon_match] Error leyendo el ícono; se reintenta: {type(e).__name__}: {e}")
            time.sleep(min(1.0, max(interval_s, 0.15)))
            continue

        now = time.time()
        if name and (name != last_name or (now - last_time) > cooldown_s):
            last_name = name
            last_time = now
            on_operator_seen(name)
        time.sleep(interval_s)
