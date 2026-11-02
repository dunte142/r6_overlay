"""
Capas transparentes, siempre-arriba y click-through durante la partida.
Contiene:
- Capa ligera de sonido, siempre visible
- HUD táctico (ficha de operador + equipos), visible por F1 durante toda la partida
- Notificación efímera (validación visual de hallazgo) -- aparece y desaparece sola
- Bitácora de drone (acumula hallazgos categorizados durante el droneo)
- Capa de cámaras del mapa -- consulta voluntaria
- Indicador de sonido -- aro verde alrededor de la brújula inferior
"""

import os
import sys
import unicodedata
from dataclasses import dataclass, field

from PyQt6.QtCore import Qt, QTimer, QPointF, QRect, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QPixmap, QPolygonF, QTransform, QImage, QRegion
from PyQt6.QtWidgets import QApplication, QWidget

from data.gadgets import get_operator_info, WALL_REINFORCEMENT_INFO
from data.cameras import get_cameras
from data.map_calibration import get_map_image_path
from ui.assets import (
    ICON, FLOOR_ICONS, FONT_FAMILY, BADGES_DIR, OPERATOR_PORTRAITS, register_fonts,
    COLOR_ORANGE_TEXT, COLOR_LIME, COLOR_BLUE, COLOR_RED, COLOR_TEXT_LIGHT,
)

# Usado por _reassert_topmost() -- ver el comentario grande ahí abajo sobre
# por qué hace falta reclamar el "topmost" de la ventana a repetición en vez
# de una sola vez al arrancar.
if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes
    _user32 = ctypes.WinDLL("user32", use_last_error=True)
    _user32.SetWindowPos.argtypes = (
        wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_int, wintypes.UINT,
    )
    _user32.SetWindowPos.restype = wintypes.BOOL
    _user32.GetWindowLongW.argtypes = (wintypes.HWND, ctypes.c_int)
    _user32.GetWindowLongW.restype = ctypes.c_long
    _user32.SetWindowLongW.argtypes = (wintypes.HWND, ctypes.c_int, ctypes.c_long)
    _user32.SetWindowLongW.restype = ctypes.c_long
    _HWND_TOPMOST = wintypes.HWND(-1)
    _SWP_NOMOVE = 0x0002
    _SWP_NOSIZE = 0x0001
    _SWP_NOACTIVATE = 0x0010
    _SWP_FRAMECHANGED = 0x0020
    _SWP_NOOWNERZORDER = 0x0200
    _GWL_EXSTYLE = -20
    _WS_EX_TRANSPARENT = 0x00000020
    _WS_EX_LAYERED = 0x00080000
    _WS_EX_NOACTIVATE = 0x08000000
else:
    _user32 = None


def _enable_clickthrough(widget) -> bool:
    """Set click-through/no-activate before a transparent window is shown."""
    if _user32 is None:
        return True
    try:
        hwnd = wintypes.HWND(int(widget.winId()))
        ctypes.set_last_error(0)
        style = _user32.GetWindowLongW(hwnd, _GWL_EXSTYLE)
        required = _WS_EX_TRANSPARENT | _WS_EX_LAYERED | _WS_EX_NOACTIVATE
        changed = (style & required) != required
        if changed:
            ctypes.set_last_error(0)
            _user32.SetWindowLongW(hwnd, _GWL_EXSTYLE, style | required)
            error = ctypes.get_last_error()
            if error:
                if not getattr(widget, "_clickthrough_warning_logged", False):
                    widget._clickthrough_warning_logged = True
                    print(f"[overlay] No se pudo configurar click-through (WinError {error}).", flush=True)
                return False
            _user32.SetWindowPos(
                hwnd, _HWND_TOPMOST, 0, 0, 0, 0,
                _SWP_NOMOVE | _SWP_NOSIZE | _SWP_NOACTIVATE | _SWP_FRAMECHANGED | _SWP_NOOWNERZORDER,
            )
        ctypes.set_last_error(0)
        ready = (_user32.GetWindowLongW(hwnd, _GWL_EXSTYLE) & required) == required
        if not ready and not getattr(widget, "_clickthrough_warning_logged", False):
            widget._clickthrough_warning_logged = True
            print("[overlay] Windows no confirmó los estilos click-through; no se mostrará el HUD táctico.", flush=True)
        return ready
    except Exception as exc:
        print(f"[overlay] Error configurando click-through: {type(exc).__name__}: {exc}", flush=True)
        return False


# Debajo del HUD superior del juego (marcador + timer), para no taparlo.
NOTICE_Y = 120
_MINI_DATA_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "recursos")

_MINI_DATA_FILES = {
    "Rook": ("defensores mini data", "Group 1071.png"),
    "Kapkan": ("defensores mini data", "Group 1072.png"),
    "Pulse": ("defensores mini data", "Group 1073.png"),
    "Castle": ("defensores mini data", "Group 1397.png"),
    "Fenrir": ("defensores mini data", "Group 1398.png"),
    "Solis": ("defensores mini data", "Group 1399.png"),
    "Azami": ("defensores mini data", "Group 1400.png"),
    "Thorn": ("defensores mini data", "Group 1401.png"),
    "Thunderbird": ("defensores mini data", "Group 1402.png"),
    "Melusi": ("defensores mini data", "Group 1403.png"),
    "Wamai": ("defensores mini data", "Group 1404.png"),
    "Goyo": ("defensores mini data", "Group 1405.png"),
    "Warden": ("defensores mini data", "Group 1406.png"),
    "Mozzie": ("defensores mini data", "Group 1407.png"),
    "Kaid": ("defensores mini data", "Group 1408.png"),
    "Clash": ("defensores mini data", "Group 1409.png"),
    "Maestro": ("defensores mini data", "Group 1410.png"),
    "Alibi": ("defensores mini data", "Group 1411.png"),
    "Vigil": ("defensores mini data", "Group 1412.png"),
    "Ela": ("defensores mini data", "Group 1413.png"),
    "Mira": ("defensores mini data", "Group 1414.png"),
    "Lesion": ("defensores mini data", "Group 1415.png"),
    "Echo": ("defensores mini data", "Group 1416.png"),
    "Caveira": ("defensores mini data", "Group 1417.png"),
    "Valkyrie": ("defensores mini data", "Group 1418.png"),
    "Frost": ("defensores mini data", "Group 1419.png"),
    "Smoke": ("defensores mini data", "Group 1420.png"),
    "Doc": ("defensores mini data", "Group 1421.png"),
    "Jager": ("defensores mini data", "Group 1422.png"),
    "Tachanka": ("defensores mini data", "Group 1423.png"),
    "Bandit": ("defensores mini data", "Group 1424.png"),
    "Mute": ("defensores mini data", "Group 1425.png"),
    "Skopos": ("defensores mini data", "Group 1426.png"),
    "Aruni": ("defensores mini data", "Group 1427.png"),
    "Denari": ("defensores mini data", "Group 1428.png"),
    "Oryx": ("defensores mini data", "Group 1429.png"),
    "Sentry": ("defensores mini data", "Group 1430.png"),
    "Noor": ("defensores mini data", "Group 1431.png"),
    "Osa": ("atacantes mini data", "Group 704.png"),
    "Flores": ("atacantes mini data", "Group 705.png"),
    "Thatcher": ("atacantes mini data", "Group 707.png"),
    "Thermite": ("atacantes mini data", "Group 709.png"),
    "IQ": ("atacantes mini data", "Group 710.png"),
    "Twitch": ("atacantes mini data", "Group 711.png"),
    "Glaz": ("atacantes mini data", "Group 714.png"),
    "Lion": ("atacantes mini data", "Group 722.png"),
    "Finka": ("atacantes mini data", "Group 723.png"),
    "Dokkaebi": ("atacantes mini data", "Group 724.png"),
    "Maverick": ("atacantes mini data", "Group 725.png"),
    "Jackal": ("atacantes mini data", "Group 727.png"),
    "Ying": ("atacantes mini data", "Group 728.png"),
    "Hibana": ("atacantes mini data", "Group 729.png"),
    "Capitao": ("atacantes mini data", "Group 730.png"),
}


@dataclass
class DroneFinding:
    category: str  # "operador" | "gadget" | "trampa" | "refuerzo"
    label: str


@dataclass
class OverlayState:
    tactical_hud_visible: bool = False
    selected_operator: str | None = None

    ephemeral_notice: str | None = None
    ephemeral_until_ms: int = 0

    drone_log: list[DroneFinding] = field(default_factory=list)
    drone_log_visible: bool = False

    my_kit: str | None = None
    my_side: str = "Defensores"  # "Defensores" | "Atacantes" -> define qué etiqueta lleva cada columna
    teammates: list[str] = field(default_factory=list)  # operadores de compañeros, leídos por OCR (vision/team_ocr.py)
    enemy_kit_known: dict[str, str] = field(default_factory=dict)  # id -> operador

    camera_layer_visible: bool = False
    camera_map: str | None = None
    camera_floor: str | None = None

    map_panel_visible: bool = False
    map_current_name: str | None = None
    map_current_floor: str | None = None
    map_pixmap: QPixmap | None = None
    minimap_live: QPixmap | None = None  # copia ampliada del minimapa NATIVO del juego (se actualiza en vivo)

    sound_direction_deg: float | None = None  # 0 = frente, 90 = derecha, etc.
    sound_intensity: float = 0.0  # 0-1, proxy de "qué tan fuerte" (distancia aprox)


class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        register_fonts()
        self.state = OverlayState()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowDoesNotAcceptFocus
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        # Crear el HWND y activar click-through antes del primer show evita
        # que la ventana tape una entrada durante el cambio de ronda.
        self._clickthrough_ok = _enable_clickthrough(self)

        self.repaint_timer = QTimer(self)
        self.repaint_timer.timeout.connect(self._tick)
        # El HUD es estático salvo cuando llegan datos/se pulsa una hotkey;
        # no necesitamos repintar toda la pantalla a 30 FPS continuamente.
        self.repaint_timer.start(200)

        # Timer SEPARADO, más rápido, solo para reclamar "siempre encima".
        # Refuerza el z-order sin elevar la frecuencia de repintado.
        # El HUD táctico queda oculto hasta que el jugador pulsa F1.
        self.topmost_timer = QTimer(self)
        self.topmost_timer.timeout.connect(self._reassert_topmost)
        # Siege puede volver a ponerse encima al cerrar ESC y recuperar el
        # foco. Reafirmamos el z-order a ritmo de juego para recuperar la
        # capa táctica enseguida, sin activar ni enfocar esta ventana.
        self.topmost_timer.start(16)

        # Flags de diagnóstico -- el programa venía muriendo con un crash
        # NATIVO (no una excepción de Python) justo al entrar al loop
        # principal de Qt, sin que ningún checkpoint de main.py alcance a
        # imprimirse después. Estos imprimen UNA sola vez, la primera vez
        # que cada camino de código realmente se ejecuta, para acotar en
        # cuál de los tres (el primer _tick, el primer paintEvent, o el
        # primer panel con contenido real) pasa.
        self._logged_first_tick = False
        self._logged_first_paint = False

        # Esta ventana liviana es independiente: F1 solo controla el HUD
        # táctico y no puede ocultar la capa permanente de sonido.
        self.sound_layer = SoundLayer(self)
        self.sound_layer.show()
        self.sound_layer._reassert_topmost()

    # ---------- API pública para disparar eventos desde el resto del programa ----------

    def show_tactical_hud(self, operator_name: str | None = None):
        """Abre el HUD táctico nuevo. No está limitado a la fase de preparación."""
        if not _enable_clickthrough(self):
            print("[overlay] HUD táctico no mostrado: no se pudo asegurar click-through.", flush=True)
            return
        self._clickthrough_ok = True
        if operator_name:
            self.state.selected_operator = operator_name
        self.state.tactical_hud_visible = True
        self.show()
        self._reassert_topmost()
        self.update()

    def show_ephemeral_notice(self, text: str, duration_ms: int = 2500):
        import time
        self.state.ephemeral_notice = text
        self.state.ephemeral_until_ms = int(time.time() * 1000) + duration_ms
        self.update()

    def add_drone_finding(self, category: str, label: str):
        self.state.drone_log.append(DroneFinding(category, label))
        self.show_ephemeral_notice(f"{category.capitalize()} detectado", duration_ms=2500)

    def toggle_drone_log(self, visible: bool):
        self.state.drone_log_visible = visible
        self.update()

    def toggle_tactical_hud(self):
        """F1 muestra u oculta solo la capa táctica sin activar su ventana."""
        if self.state.tactical_hud_visible:
            self.state.tactical_hud_visible = False
            self.hide()
        else:
            # Reaplicar antes de mostrar: el juego nunca debe recibir una
            # ventana táctica opaca a teclado o mouse.
            self._clickthrough_ok = _enable_clickthrough(self)
            if not self._clickthrough_ok:
                print("[overlay] HUD táctico no mostrado: no se pudo asegurar click-through.", flush=True)
                return
            self.state.tactical_hud_visible = True
            self.show()
            self._reassert_topmost()
        print(
            f"[overlay] HUD táctico {'visible' if self.state.tactical_hud_visible else 'oculto'} (F1)",
            flush=True,
        )
        self.update()

    def set_my_kit(self, operator_name: str):
        self.state.my_kit = operator_name
        self.state.selected_operator = operator_name
        # Cambiar/descubrir el operador no debe abrir el HUD por sí solo.
        # La visibilidad queda exclusivamente bajo el control de F1.
        self.update()

    def set_teammates(self, operators: list[str]):
        """Lista de operadores de COMPAÑEROS (nunca el tuyo -- ese lo fija
        set_my_kit/F6), leída de la barra de preparación por vision/team_ocr.py.
        Reemplaza la lista completa en cada llamada (ya viene deduplicada)."""
        self.state.teammates = operators
        self.update()

    def register_enemy_kit(self, enemy_id: str, operator_name: str):
        """Llamar solo cuando el operador enemigo ya fue visto en pantalla
        (droneo, kill cam, combate). No inventa datos que el jugador no vio."""
        self.state.enemy_kit_known[enemy_id] = operator_name
        self.update()

    def toggle_map_panel(self, map_name: str, floor: str):
        """F2: mostrar/ocultar el panel de mapa + posición del jugador."""
        was_visible = self.state.map_panel_visible and self.state.map_current_name == map_name and self.state.map_current_floor == floor

        if was_visible:
            self.state.map_panel_visible = False
            self.update()
            return

        self.state.map_panel_visible = True
        self._set_current_map(map_name, floor)
        self.update()

    def _set_current_map(self, map_name: str, floor: str):
        """Cambia el mapa/piso mostrado, cargando la imagen correspondiente.
        Se llama automáticamente al detectar cambio de piso (ver main.py)."""
        if self.state.map_current_name == map_name and self.state.map_current_floor == floor and self.state.map_pixmap:
            return

        self.state.map_current_name = map_name
        self.state.map_current_floor = floor

        path = get_map_image_path(map_name, floor)
        pixmap = QPixmap(path) if path else None
        self.state.map_pixmap = pixmap if (pixmap and not pixmap.isNull()) else None

    def update_minimap_frame(self, frame_bgra, width: int | None = None, height: int | None = None):
        """Recibe BGRA serializado desde vision/worker.py (o numpy por compatibilidad).

        El proceso de Qt no importa NumPy/OpenCV: crea el QImage desde bytes
        inmutables enviados por el proceso auxiliar de captura.
        """
        if not self.state.map_panel_visible:
            return
        if isinstance(frame_bgra, (bytes, bytearray, memoryview)):
            w, h = int(width or 0), int(height or 0)
            if w <= 0 or h <= 0 or len(frame_bgra) != w * h * 4:
                return
            raw = bytes(frame_bgra)
            img = QImage(raw, w, h, w * 4, QImage.Format.Format_ARGB32)
            self.state.minimap_live = QPixmap.fromImage(img.copy())
        else:
            # Compatibilidad con el modo demo/uso local anterior.
            h, w = frame_bgra.shape[:2]
            img = QImage(frame_bgra.data, w, h, frame_bgra.strides[0], QImage.Format.Format_ARGB32)
            self.state.minimap_live = QPixmap.fromImage(img.copy())
        self.update()

    def toggle_camera_layer(self, map_name: str, floor: str):
        self.state.camera_layer_visible = not self.state.camera_layer_visible
        self.state.camera_map = map_name
        self.state.camera_floor = floor
        self.update()

    def update_sound_direction(self, angle_deg: float, intensity: float):
        if self.state.sound_direction_deg is None:
            print("[checkpoint] primera actualización de dirección de sonido recibida", flush=True)
        self.state.sound_direction_deg = angle_deg
        self.state.sound_intensity = max(0.0, min(1.0, intensity))
        self.update()
        self.sound_layer.update_audio()

    # ---------- Render ----------

    def _reassert_topmost(self):
        """Windows no tiene un 'topmost' permanente -- gana el último que lo
        pide. WindowStaysOnTopHint de Qt lo pide UNA vez, al mostrar la
        ventana. Pero muchos juegos (incluso en modo 'sin bordes', como
        confirmó el usuario que ya está configurado acá) se reafirman ELLOS
        MISMOS como topmost cada vez que recuperan el foco -- eso empuja a
        cualquier otra ventana topmost (la nuestra incluida) para atrás en
        el z-order, en silencio, sin que Qt se entere ni dispare ningún
        evento. El HUD se mantiene en una ventana transparente independiente;
        su visibilidad táctica la controla F1, y este método conserva el
        orden superior mientras la ventana está activa."""
        if _user32 is None:
            return
        try:
            # Algunos cambios de modo/resolución al entrar a la ronda pueden
            # recrear el área visible; no mostrar una ventana que el jugador
            # ocultó con F1.
            if not self.isVisible():
                return
            screen = QApplication.primaryScreen()
            if screen is not None:
                geometry = screen.geometry()
                if self.geometry() != geometry:
                    self.setGeometry(geometry)
            hwnd_handle = wintypes.HWND(int(self.winId()))
            _enable_clickthrough(self)
            position_flags = _SWP_NOMOVE | _SWP_NOSIZE | _SWP_NOACTIVATE | _SWP_NOOWNERZORDER
            ok = _user32.SetWindowPos(
                hwnd_handle, _HWND_TOPMOST, 0, 0, 0, 0,
                position_flags,
            )
            if not ok and not getattr(self, "_topmost_warning_logged", False):
                self._topmost_warning_logged = True
                print(f"[overlay] SetWindowPos no pudo reafirmar topmost (WinError {ctypes.get_last_error()}).", flush=True)
        except Exception as exc:
            if not getattr(self, "_topmost_warning_logged", False):
                self._topmost_warning_logged = True
                print(f"[overlay] Error Win32 al reafirmar topmost: {type(exc).__name__}: {exc}", flush=True)

    def _tick(self):
        if not self._logged_first_tick:
            self._logged_first_tick = True
            print("[checkpoint] primer _tick() del timer de 30fps OK", flush=True)
        # _reassert_topmost tiene su propio timer (self.topmost_timer).
        import time
        if self.state.ephemeral_notice and time.time() * 1000 > self.state.ephemeral_until_ms:
            self.state.ephemeral_notice = None
            self.update()
        # Los cambios visuales llaman update() desde sus setters/señales.
        # Este timer solo retira avisos expirados; no fuerza repintados vacíos.

    def paintEvent(self, event):
        if not self._logged_first_paint:
            self._logged_first_paint = True
            print("[checkpoint] primer paintEvent() arrancando", flush=True)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # IMPORTANTE: PyQt6 aborta el proceso ENTERO sin traceback visible si
        # una excepción escapa de paintEvent (es un callback de Qt, no código
        # Python normal) -- por eso cada panel se dibuja en su propio
        # try/except. Así, si un panel tiene un bug, ese panel se salta (y
        # queda impreso en consola qué y por qué) en vez de cerrar todo el
        # overlay en silencio.
        panels = [
            ("tactical_hud", self.state.tactical_hud_visible, self._draw_tactical_hud),
            ("ephemeral_notice", self.state.tactical_hud_visible and bool(self.state.ephemeral_notice), self._draw_ephemeral_notice),
            ("drone_log", self.state.drone_log_visible, self._draw_drone_log),
            ("camera_layer", self.state.camera_layer_visible, self._draw_camera_layer),
            ("map_panel", self.state.map_panel_visible, self._draw_map_panel),
        ]
        # OJO: el log previo marcaba "primer paintEvent" como un todo, pero
        # el primer paintEvent casi siempre pinta CERO paneles (nada está
        # visible todavía apenas arranca) -- el panel que realmente importa
        # ver es el primero de CADA TIPO que se dibuja alguna vez (ej. el
        # indicador de sonido, que recién se activa cuando llega el primer
        # dato de audio, unos paintEvents después del primero). Por eso acá
        # se loguea la primera vez de CADA panel por separado, no solo
        # dentro del primer paintEvent.
        if not hasattr(self, "_logged_panels_once"):
            self._logged_panels_once = set()

        for name, visible, draw_fn in panels:
            if not visible:
                continue
            first_time = name not in self._logged_panels_once
            if first_time:
                self._logged_panels_once.add(name)
                print(f"[checkpoint] primera vez dibujando panel '{name}' -- por entrar", flush=True)
            try:
                draw_fn(painter)
            except Exception as e:
                import traceback
                print(f"[overlay] Error dibujando '{name}': {type(e).__name__}: {e}")
                traceback.print_exc()
            if first_time:
                print(f"[checkpoint] primera vez dibujando panel '{name}' -- OK", flush=True)

        painter.end()

    def _draw_tactical_hud(self, painter: QPainter):
        """Dibuja el HUD táctico de partida siguiendo la maqueta de referencia.

        El juego continúa visible: solo se dibujan composiciones PNG transparentes,
        tarjetas oscuras semitransparentes y el marco naranja. El diseño se define
        en coordenadas 1920x1080 y se escala al tamaño real del monitor.
        """
        operator_name = self.state.my_kit or self.state.selected_operator or ""
        info = get_operator_info(operator_name) or {}

        painter.save()
        try:
            sx = max(0.1, self.width() / 1920.0)
            sy = max(0.1, self.height() / 1080.0)
            painter.scale(sx, sy)

            # Oscurecimiento global suave como en la referencia.
            painter.fillRect(QRectF(0, 0, 1920, 1080), QColor(0, 0, 0, 132))

            # La ficha propia ocupa el panel izquierdo completo.
            portrait_path = self._operator_portrait_path(operator_name)
            portrait = self._load_pixmap(portrait_path) if portrait_path else None
            if portrait and not portrait.isNull():
                fitted = portrait.scaled(
                    793, 731,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                px = 30 + (793 - fitted.width()) // 2
                py = 160 + (731 - fitted.height()) // 2
                painter.drawPixmap(px, py, fitted)
            else:
                self._draw_operator_fallback(painter, operator_name, info)

            # Separador vertical claro entre la ficha y las listas.
            painter.setPen(QPen(QColor(235, 235, 235, 225), 2))
            painter.drawLine(829, 150, 829, 890)

            mine_is_def = self.state.my_side == "Defensores"
            my_label = self._load_pixmap(
                ICON["label_mi_equipo_defensores" if mine_is_def else "label_mi_equipo_atacantes"]
            )
            enemy_label = self._load_pixmap(
                ICON["label_equipo_rival_atacantes" if mine_is_def else "label_equipo_rival_defensores"]
            )
            if my_label and not my_label.isNull():
                painter.drawPixmap(859, 202, my_label)
            else:
                painter.setPen(QColor(*COLOR_TEXT_LIGHT))
                painter.setFont(QFont(FONT_FAMILY, 25, QFont.Weight.Bold))
                painter.drawText(859, 226, "MI EQUIPO")
            if enemy_label and not enemy_label.isNull():
                painter.drawPixmap(1337, 202, enemy_label)
            else:
                painter.setPen(QColor(*COLOR_RED))
                painter.setFont(QFont(FONT_FAMILY, 25, QFont.Weight.Bold))
                painter.drawText(1337, 226, "EQUIPO RIVAL")

            # Tarjetas compuestas entregadas en mini data: incluyen el icono,
            # nombre, descripción y gadget de cada operador.
            team_names = list(dict.fromkeys(self.state.teammates))[:4]
            for index, teammate in enumerate(team_names):
                x, y = 858, 256 + index * 120
                if not self._draw_mini_data_card(painter, teammate, x, y, 458, 110):
                    self._draw_team_card(painter, x, y, 458, 110, teammate)

            # Solo se completan las tarjetas rivales que el juego reveló; las
            # demás conservan el signo de interrogación de la referencia.
            enemy_names = list(dict.fromkeys(self.state.enemy_kit_known.values()))[:5]
            for index in range(5):
                x, y = 1337, 256 + index * 110
                if index < len(enemy_names):
                    name = enemy_names[index]
                    if not self._draw_mini_data_card(painter, name, x, y, 458, 100):
                        self._draw_enemy_wide_card(painter, x, y, 458, 105, name)
                else:
                    self._draw_enemy_square(painter, x, y + (14 if index == 0 else 0), 76, 72, None)

            # Controles visuales de la maqueta; los atajos globales siguen siendo
            # los que realmente activan marcador, plano y ajustes.
            painter.setPen(QColor(*COLOR_TEXT_LIGHT))
            painter.setFont(QFont(FONT_FAMILY, 27, QFont.Weight.Bold))
            painter.drawText(1605, 58, "PARTIDA ACTUAL")
            for key, y in (("match_button", 19), ("settings_button", 171)):
                pix = self._load_pixmap(ICON[key])
                if pix and not pix.isNull():
                    painter.drawPixmap(QRectF(1831, y, 65, 64), pix, QRectF(pix.rect()))

            # Marco perimetral naranja como en la referencia (se dibuja al final
            # para que permanezca visible por encima de todos los paneles).
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(255, 137, 0, 245), 5))
            painter.drawRect(QRectF(3, 3, 1914, 1074))
        finally:
            painter.restore()

    @staticmethod
    def _normalize_operator_name(name: str) -> str:
        value = (name or "").replace("ø", "o").replace("Ø", "O")
        value = unicodedata.normalize("NFKD", value)
        value = "".join(ch for ch in value if not unicodedata.combining(ch))
        return "".join(ch.lower() for ch in value if ch.isalnum())

    def _operator_portrait_path(self, name: str) -> str | None:
        direct = OPERATOR_PORTRAITS.get(name)
        if direct and os.path.isfile(direct):
            return direct
        normalized = self._normalize_operator_name(name)
        for key, path in OPERATOR_PORTRAITS.items():
            if self._normalize_operator_name(key) == normalized and os.path.isfile(path):
                return path
        return None

    def _operator_badge_path(self, name: str | None) -> str | None:
        if not name or not os.path.isdir(BADGES_DIR):
            return None
        wanted = self._normalize_operator_name(name)
        try:
            for filename in os.listdir(BADGES_DIR):
                if filename.lower().endswith(".png") and self._normalize_operator_name(filename[:-4]) == wanted:
                    return os.path.join(BADGES_DIR, filename)
        except OSError:
            return None
        return None

    def _draw_mini_data_card(self, painter: QPainter, operator_name: str,
                             x: int, y: int, w: int, h: int) -> bool:
        entry = _MINI_DATA_FILES.get(operator_name)
        if not entry:
            normalized = self._normalize_operator_name(operator_name)
            entry = next(
                (value for name, value in _MINI_DATA_FILES.items()
                 if self._normalize_operator_name(name) == normalized),
                None,
            )
        if not entry:
            return False
        path = os.path.join(_MINI_DATA_ROOT, entry[0], entry[1])
        pixmap = self._load_pixmap(path)
        if not pixmap or pixmap.isNull():
            return False
        painter.drawPixmap(QRectF(x, y, w, h), pixmap, QRectF(pixmap.rect()))
        return True

    @staticmethod
    def _short_description(name: str, info: dict) -> str:
        fixed = {
            "Fenrir": "Su dispositivo libera un gas que reduce la visión.",
            "Solis": "Su habilidad marca dispositivos rivales.",
            "Azami": "Su dispositivo crea una barrera antibalas que tapa agujeros.",
            "Thorn": "Detecta oponentes y expulsa hojas afiladas que causan daño letal.",
        }
        if name in fixed:
            return fixed[name]
        description = info.get("descripcion")
        if not description and info.get("gadget"):
            description = f"Su dispositivo es {info['gadget']}."
        if not description:
            description = "Operador identificado en la partida."
        description = str(description)
        description = description.split(". ")[0].strip()
        if len(description) > 105:
            description = description[:102].rsplit(" ", 1)[0] + "…"
        return description if description.endswith((".", "…")) else description + "."

    def _draw_operator_fallback(self, painter: QPainter, operator_name: str, info: dict):
        """Fallback legible para operadores sin composición gráfica instalada."""
        panel = QRectF(75, 190, 735, 650)
        painter.setBrush(QColor(7, 10, 14, 115))
        painter.setPen(QPen(QColor(*COLOR_LIME, 200), 1.5))
        painter.drawRoundedRect(panel, 4, 4)
        if not operator_name:
            unknown = self._load_pixmap(ICON["unknown_operator"])
            if unknown and not unknown.isNull():
                painter.drawPixmap(QRectF(115, 300, 230, 230), unknown, QRectF(unknown.rect()))
            painter.setPen(QColor(245, 245, 245))
            painter.setFont(QFont(FONT_FAMILY, 22, QFont.Weight.Bold))
            painter.drawText(390, 330, "TU OPERADOR")
            painter.setPen(QColor(*COLOR_BLUE))
            painter.setFont(QFont(FONT_FAMILY, 34, QFont.Weight.Bold))
            painter.drawText(QRectF(390, 345, 380, 110), Qt.TextFlag.TextWordWrap,
                             "ESPERANDO DETECCIÓN")
            painter.setPen(QColor(*COLOR_TEXT_LIGHT))
            painter.setFont(QFont(FONT_FAMILY, 20))
            painter.drawText(QRectF(390, 465, 370, 130), Qt.TextFlag.TextWordWrap,
                             "La ficha aparecerá cuando el programa reconozca tu agente.")
            return
        badge_path = self._operator_badge_path(operator_name)
        badge = self._load_pixmap(badge_path) if badge_path else None
        if badge and not badge.isNull():
            painter.drawPixmap(QRectF(100, 260, 300, 300), badge, QRectF(badge.rect()))
        painter.setPen(QColor(245, 245, 245))
        painter.setFont(QFont(FONT_FAMILY, 22, QFont.Weight.Bold))
        painter.drawText(435, 240, "TÚ")
        painter.setPen(QColor(*COLOR_BLUE))
        painter.setFont(QFont(FONT_FAMILY, 38, QFont.Weight.Bold))
        painter.drawText(QRectF(435, 245, 335, 60), Qt.AlignmentFlag.AlignLeft, operator_name.upper())
        painter.setPen(QColor(*COLOR_LIME))
        painter.setFont(QFont(FONT_FAMILY, 21, QFont.Weight.Bold))
        painter.drawText(QRectF(435, 320, 330, 60), Qt.TextFlag.TextWordWrap, str(info.get("gadget", "Dispositivo táctico")))
        painter.setPen(QColor(*COLOR_TEXT_LIGHT))
        painter.setFont(QFont(FONT_FAMILY, 19))
        painter.drawText(QRectF(435, 370, 330, 160), Qt.TextFlag.TextWordWrap, str(info.get("descripcion", "Ficha del operador.")))
        painter.setPen(QColor(*COLOR_ORANGE_TEXT))
        painter.setFont(QFont(FONT_FAMILY, 23, QFont.Weight.Bold))
        painter.drawText(435, 585, "CONSEJO DE USO")
        painter.setPen(QColor(*COLOR_TEXT_LIGHT))
        painter.setFont(QFont(FONT_FAMILY, 18))
        painter.drawText(QRectF(435, 600, 330, 180), Qt.TextFlag.TextWordWrap, str(info.get("consejo", "Consulta la ficha antes de iniciar la ronda.")))

    def _draw_team_card(self, painter: QPainter, x: int, y: int, w: int, h: int,
                        operator_name: str | None, placeholder: bool = False):
        if placeholder:
            self._draw_enemy_square(painter, x, y + 14, 76, 72, None)
            return

        badge_path = self._operator_badge_path(operator_name)
        badge = self._load_pixmap(badge_path) if badge_path else None
        if badge and not badge.isNull():
            painter.drawPixmap(QRectF(x, y + 10, 76, 72), badge, QRectF(badge.rect()))

        name = operator_name or "Operador desconocido"
        info = get_operator_info(name) or {}
        painter.setPen(QColor(107, 171, 255))
        painter.setFont(QFont(FONT_FAMILY, 23, QFont.Weight.Bold))
        painter.drawText(x + 86, y + 25, name)
        painter.setPen(QColor(*COLOR_TEXT_LIGHT))
        painter.setFont(QFont(FONT_FAMILY, 15))
        description = self._short_description(name, info)
        painter.drawText(QRectF(x + 86, y + 32, w - 100, h - 35), Qt.TextFlag.TextWordWrap, description)

    def _draw_enemy_wide_card(self, painter: QPainter, x: int, y: int, w: int, h: int,
                              operator_name: str | None):
        if not operator_name:
            return
        badge_path = self._operator_badge_path(operator_name)
        badge = self._load_pixmap(badge_path) if badge_path else None
        if badge and not badge.isNull():
            painter.drawPixmap(QRectF(x, y + 10, 76, 72), badge, QRectF(badge.rect()))
        painter.setPen(QColor(245, 90, 90))
        painter.setFont(QFont(FONT_FAMILY, 23, QFont.Weight.Bold))
        painter.drawText(x + 86, y + 25, operator_name)
        info = get_operator_info(operator_name) or {}
        painter.setPen(QColor(235, 235, 235))
        painter.setFont(QFont(FONT_FAMILY, 15))
        painter.drawText(QRectF(x + 86, y + 32, w - 192, h - 35),
                         Qt.TextFlag.TextWordWrap, self._short_description(operator_name, info))

    def _draw_enemy_square(self, painter: QPainter, x: int, y: int, w: int, h: int,
                           operator_name: str | None):
        painter.setBrush(QColor(5, 7, 10, 205))
        painter.setPen(QPen(QColor(230, 126, 34, 245), 2))
        painter.drawRect(QRectF(x, y, w, h))
        if operator_name:
            badge_path = self._operator_badge_path(operator_name)
            badge = self._load_pixmap(badge_path) if badge_path else None
            if badge and not badge.isNull():
                painter.drawPixmap(QRectF(x + 8, y + 7, w - 16, h - 14), badge, QRectF(badge.rect()))
                return
        painter.setPen(QColor(255, 140, 0))
        painter.setFont(QFont(FONT_FAMILY, 40, QFont.Weight.Bold))
        painter.drawText(QRectF(x, y + 1, w, h - 2), Qt.AlignmentFlag.AlignCenter, "?")

    def _load_pixmap(self, path: str) -> QPixmap | None:
        """Carga un QPixmap con cache simple para no releer el archivo en cada frame."""
        if not hasattr(self, "_pixmap_cache"):
            self._pixmap_cache = {}
        if path not in self._pixmap_cache:
            pix = QPixmap(path)
            self._pixmap_cache[path] = pix if not pix.isNull() else None
        return self._pixmap_cache[path]

    def _draw_ephemeral_notice(self, painter: QPainter):
        # Usa el asset "Detectado" (check verde) del diseño para el caso
        # genérico de droneo; si el texto no es "detectado", se dibuja
        # como texto libre encima del mismo estilo de cápsula.
        w = self.width()
        cx = w // 2
        notice_pix = self._load_pixmap(ICON["detected_notice"])

        if notice_pix and self.state.ephemeral_notice and "detectado" in self.state.ephemeral_notice.lower():
            px = cx - notice_pix.width() // 2
            painter.drawPixmap(px, NOTICE_Y, notice_pix)
            return

        painter.setBrush(QColor(20, 30, 25, 220))
        painter.setPen(QPen(QColor(*COLOR_LIME), 1))
        painter.drawRoundedRect(cx - 140, NOTICE_Y, 280, 40, 8, 8)
        painter.setPen(QColor(*COLOR_LIME))
        painter.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        painter.drawText(cx - 140, NOTICE_Y, 280, 40,
                          Qt.AlignmentFlag.AlignCenter, self.state.ephemeral_notice)

    def _draw_drone_log(self, painter: QPainter):
        x, y, w = self.width() - 260, 100, 240
        h = 30 + 22 * max(1, len(self.state.drone_log))
        painter.setBrush(QColor(10, 15, 20, 210))
        painter.setPen(QPen(QColor(*COLOR_ORANGE_TEXT), 1))
        painter.drawRoundedRect(x, y, w, h, 6, 6)

        painter.setPen(QColor(*COLOR_ORANGE_TEXT))
        painter.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
        painter.drawText(x + 10, y + 20, "BITÁCORA DE DRONEO")

        painter.setFont(QFont(FONT_FAMILY, 10))
        painter.setPen(QColor(220, 220, 220))
        for i, finding in enumerate(self.state.drone_log[-12:]):
            painter.drawText(x + 10, y + 38 + i * 20, f"• {finding.category}: {finding.label}")

    def _draw_camera_layer(self, painter: QPainter):
        if not (self.state.camera_map and self.state.camera_floor):
            return
        cams = get_cameras(self.state.camera_map, self.state.camera_floor)
        w, h = self.width(), self.height()

        painter.setBrush(QColor(0, 0, 0, 160))
        painter.drawRect(0, 0, w, h)

        painter.setPen(QColor(255, 200, 60))
        painter.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
        for cam in cams:
            px, py = int(cam["x"] * w), int(cam["y"] * h)
            painter.setBrush(QColor(255, 60, 60, 220))
            painter.drawEllipse(QPointF(px, py), 6, 6)
            painter.drawText(px + 10, py, cam["label"])

        # Panel de referencias real del diseño, esquina inferior izquierda
        legend_pix = self._load_pixmap(ICON["camera_legend"])
        if legend_pix:
            painter.drawPixmap(20, h - legend_pix.height() - 20, legend_pix)

    def _draw_map_panel(self, painter: QPainter):
        """Panel de F2: minimapa nativo ampliado (en vivo) + plano del piso.

        OJO: el minimapa del juego está centrado en el jugador y rota con la
        mirada (la flecha azul siempre apunta arriba y queda en el centro),
        así que NO se puede ubicar al jugador sobre un plano fijo con una
        calibración de 4 puntos. Por eso acá se muestra el minimapa real,
        más grande, y aparte el plano del piso como referencia."""
        panel_w = 320
        pad = 10
        # Debajo del minimapa nativo del juego (arriba-izquierda) y sin tapar
        # la vida/armadura (abajo-izquierda).
        panel_x, panel_y = 30, 370
        inner_w = panel_w - 2 * pad

        map_pix = self.state.map_pixmap
        plan_h = int(inner_w * (map_pix.height() / map_pix.width())) if map_pix and map_pix.width() else int(inner_w * 0.56)
        header_h, tabs_h = 26, 26
        live_size = inner_w
        panel_h = header_h + tabs_h + live_size + 8 + plan_h + pad

        painter.setBrush(QColor(8, 12, 16, 235))
        painter.setPen(QPen(QColor(*COLOR_ORANGE_TEXT), 1))
        painter.drawRoundedRect(panel_x, panel_y, panel_w, panel_h, 6, 6)

        # Encabezado con el nombre del mapa (para saber qué mapa está activo con F4)
        painter.setPen(QColor(*COLOR_ORANGE_TEXT))
        painter.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        painter.drawText(panel_x + pad, panel_y + 19, (self.state.map_current_name or "?").upper())

        # Tabs de piso: se escalan para que entren SIEMPRE dentro del panel
        tab_pixmaps = []
        for floor_name, icon_path in FLOOR_ICONS.items():
            pix = self._load_pixmap(icon_path)
            if pix:
                tab_pixmaps.append((floor_name, pix))
        gap = 10
        total_w = sum(p.width() for _, p in tab_pixmaps) + gap * max(0, len(tab_pixmaps) - 1)
        tab_scale = min(1.0, inner_w / total_w) if total_w else 1.0
        tab_h = max(10, int(16 * tab_scale))
        tx, ty = panel_x + pad, panel_y + header_h + 2
        for floor_name, pix in tab_pixmaps:
            scaled = pix.scaledToHeight(tab_h, Qt.TransformationMode.SmoothTransformation)
            painter.setOpacity(1.0 if floor_name == self.state.map_current_floor else 0.4)
            painter.drawPixmap(tx, ty, scaled)
            tx += scaled.width() + int(gap * tab_scale)
        painter.setOpacity(1.0)

        # Minimapa nativo ampliado, en vivo
        live_rect = QRectF(panel_x + pad, panel_y + header_h + tabs_h, live_size, live_size)
        if self.state.minimap_live:
            painter.drawPixmap(live_rect.toRect(), self.state.minimap_live)
            painter.setPen(QPen(QColor(*COLOR_ORANGE_TEXT), 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(live_rect)
        else:
            painter.setPen(QColor(160, 160, 160))
            painter.setFont(QFont(FONT_FAMILY, 11))
            painter.drawText(live_rect, Qt.AlignmentFlag.AlignCenter, "Esperando el minimapa del juego...")

        # Plano del piso (referencia estática)
        plan_rect = QRectF(panel_x + pad, live_rect.bottom() + 8, inner_w, plan_h)
        if map_pix:
            painter.drawPixmap(plan_rect.toRect(), map_pix)
        else:
            painter.setPen(QColor(200, 200, 200))
            painter.setFont(QFont(FONT_FAMILY, 11))
            painter.drawText(plan_rect, Qt.AlignmentFlag.AlignCenter, "Sin plano para este mapa/piso")

    def _draw_sound_indicator(self, painter: QPainter):
        """Aro de audio alrededor de la brújula, en la parte inferior.
        angle_deg: 0 = frente, 90 = derecha, -90 = izquierda, 180 = atrás (aprox)."""
        scale = min(self.width() / 1920.0, self.height() / 1080.0)
        cx, cy = self.width() // 2, int(self.height() * 0.915)
        radius = int(70 * scale)

        # Aro constante para enmarcar la brújula y arco brillante para indicar
        # la dirección estimada del sonido.
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(142, 255, 0, 175), max(1.5, 2.0 * scale)))
        painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))

        alpha = int(100 + 155 * self.state.sound_intensity)
        pen = QPen(QColor(142, 255, 0, alpha), max(2.0, 4.0 * scale))
        painter.setPen(pen)

        span = 42  # grados de apertura del arco direccional
        rect_x, rect_y = cx - radius, cy - radius
        start_angle = int((90 - self.state.sound_direction_deg - span / 2) * 16)
        span_angle = int(span * 16)
        painter.drawArc(rect_x, rect_y, radius * 2, radius * 2, start_angle, span_angle)


class SoundLayer(QWidget):
    """Capa permanente y pasiva para sonido y futuras animaciones ligeras."""

    def __init__(self, tactical_overlay: Overlay):
        super().__init__()
        self.tactical_overlay = tactical_overlay
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowDoesNotAcceptFocus
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setGeometry(QApplication.primaryScreen().geometry())
        self._sound_icon = QPixmap(ICON["sound_button"])
        self._clickthrough_ok = _enable_clickthrough(self)
        self._update_mask()
        self.topmost_timer = QTimer(self)
        self.topmost_timer.timeout.connect(self._reassert_topmost)
        self.topmost_timer.start(16)

    def _reassert_topmost(self):
        Overlay._reassert_topmost(self)
        self._update_mask()

    def _update_mask(self):
        sx = max(0.1, self.width() / 1920.0)
        sy = max(0.1, self.height() / 1080.0)
        sound_x = int(1831 * sx)
        sound_y = int(95 * sy)
        region = QRegion(QRect(sound_x, sound_y, max(1, int(65 * sx)), max(1, int(64 * sy))))
        if self._clickthrough_ok and self.tactical_overlay.state.sound_direction_deg is not None:
            cx, cy = self.width() // 2, int(self.height() * 0.915)
            radius = int(85 * min(sx, sy))
            region = region.united(QRegion(QRect(cx - radius, cy - radius, radius * 2, radius * 2)))
        self.setMask(region)

    def update_audio(self):
        self._update_mask()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        sx = max(0.1, self.width() / 1920.0)
        sy = max(0.1, self.height() / 1080.0)
        if not self._sound_icon.isNull():
            painter.drawPixmap(
                QRectF(1831 * sx, 95 * sy, 65 * sx, 64 * sy),
                self._sound_icon,
                QRectF(self._sound_icon.rect()),
            )
        owner = self.tactical_overlay
        if owner.state.sound_direction_deg is not None:
            owner._draw_sound_indicator(painter)
        painter.end()


def run_overlay_standalone_demo():
    """Demo mínima para probar el overlay solo, sin el resto del pipeline."""
    app = QApplication(sys.argv)
    overlay = Overlay()
    overlay.show()

    # Simulación de eventos para ver el overlay funcionando:
    QTimer.singleShot(1000, lambda: overlay.show_tactical_hud("Mute"))
    QTimer.singleShot(3000, lambda: overlay.add_drone_finding("operador", "Kapkan (visto en Cocina)"))
    QTimer.singleShot(4000, lambda: overlay.toggle_drone_log(True))
    QTimer.singleShot(5000, lambda: overlay.update_sound_direction(45, 0.7))
    QTimer.singleShot(6000, lambda: overlay.set_my_kit("Pulse"))

    sys.exit(app.exec())


if __name__ == "__main__":
    run_overlay_standalone_demo()
