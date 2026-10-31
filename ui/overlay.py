"""
Overlay transparente, siempre-arriba, click-through cuando no se lo necesita.
Contiene:
- HUD táctico nuevo (ficha de operador + equipos), visible por F1 durante toda la partida
- Notificación efímera (validación visual de hallazgo) -- aparece y desaparece sola
- Bitácora de drone (acumula hallazgos categorizados durante el droneo)
- Capa de cámaras del mapa -- consulta voluntaria
- Indicador de dirección de sonido -- arco cerca del centro de pantalla
"""

import os
import sys
import unicodedata
from dataclasses import dataclass, field

from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QPixmap, QPolygonF, QTransform, QImage
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
    _HWND_TOPMOST = wintypes.HWND(-1)
    _SWP_NOMOVE = 0x0002
    _SWP_NOSIZE = 0x0001
    _SWP_NOACTIVATE = 0x0010
else:
    _user32 = None


# Debajo del HUD superior del juego (marcador + timer), para no taparlo.
NOTICE_Y = 120


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

        self.repaint_timer = QTimer(self)
        self.repaint_timer.timeout.connect(self._tick)
        # El HUD es estático salvo cuando llegan datos/se pulsa una hotkey;
        # no necesitamos repintar toda la pantalla a 30 FPS continuamente.
        self.repaint_timer.start(200)

        # Timer SEPARADO, más rápido, solo para reclamar "siempre encima".
        # Refuerza el z-order sin elevar la frecuencia de repintado.
        # El HUD táctico nuevo solo se dibuja cuando el usuario pulsa F1; permanece visible al iniciar la ronda.
        self.topmost_timer = QTimer(self)
        self.topmost_timer.timeout.connect(self._reassert_topmost)
        # Reafirmar el z-order 1-2 veces por segundo evita llamadas Win32
        # demasiado frecuentes al cambiar el juego entre preparación y 3D.
        self.topmost_timer.start(750)

        # Flags de diagnóstico -- el programa venía muriendo con un crash
        # NATIVO (no una excepción de Python) justo al entrar al loop
        # principal de Qt, sin que ningún checkpoint de main.py alcance a
        # imprimirse después. Estos imprimen UNA sola vez, la primera vez
        # que cada camino de código realmente se ejecuta, para acotar en
        # cuál de los tres (el primer _tick, el primer paintEvent, o el
        # primer panel con contenido real) pasa.
        self._logged_first_tick = False
        self._logged_first_paint = False

    # ---------- API pública para disparar eventos desde el resto del programa ----------

    def show_tactical_hud(self, operator_name: str | None = None):
        """Abre el HUD táctico nuevo. No está limitado a la fase de preparación."""
        if operator_name:
            self.state.selected_operator = operator_name
        self.state.tactical_hud_visible = True
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
        """F1 alterna únicamente el HUD táctico nuevo durante toda la partida."""
        self.state.tactical_hud_visible = not self.state.tactical_hud_visible
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
            # recrear el área visible. La ventana Qt permanece viva y se
            # vuelve a mostrar sin tomar el foco si Windows la ocultó.
            if not self.isVisible():
                self.show()
            screen = QApplication.primaryScreen()
            if screen is not None:
                geometry = screen.geometry()
                if self.geometry() != geometry:
                    self.setGeometry(geometry)
            hwnd = int(self.winId())
            ok = _user32.SetWindowPos(
                wintypes.HWND(hwnd), _HWND_TOPMOST, 0, 0, 0, 0,
                _SWP_NOMOVE | _SWP_NOSIZE | _SWP_NOACTIVATE | 0x0200,
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
            ("sound_indicator", self.state.tactical_hud_visible and self.state.sound_direction_deg is not None, self._draw_sound_indicator),
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

            # Composición del operador: retrato + gadget + consejo de uso.
            portrait_path = self._operator_portrait_path(operator_name)
            portrait = self._load_pixmap(portrait_path) if portrait_path else None
            if portrait and not portrait.isNull():
                fitted = portrait.scaled(
                    765, 705,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                px = 80 + (765 - fitted.width()) // 2
                py = 160 + (705 - fitted.height()) // 2
                painter.drawPixmap(px, py, fitted)
            else:
                self._draw_operator_fallback(painter, operator_name, info)

            # Separador sutil entre la ficha del operador y el equipo.
            painter.setPen(QPen(QColor(120, 184, 0, 180), 1.5))
            painter.drawLine(850, 160, 850, 855)

            mine_is_def = self.state.my_side == "Defensores"
            my_label = self._load_pixmap(
                ICON["label_mi_equipo_defensores" if mine_is_def else "label_mi_equipo_atacantes"]
            )
            enemy_label = self._load_pixmap(
                ICON["label_equipo_rival_atacantes" if mine_is_def else "label_equipo_rival_defensores"]
            )
            if my_label and not my_label.isNull():
                painter.drawPixmap(895, 190, my_label)
            else:
                painter.setPen(QColor(*COLOR_TEXT_LIGHT))
                painter.setFont(QFont(FONT_FAMILY, 25, QFont.Weight.Bold))
                painter.drawText(895, 215, "MI EQUIPO")
            if enemy_label and not enemy_label.isNull():
                painter.drawPixmap(1390, 190, enemy_label)
            else:
                painter.setPen(QColor(*COLOR_RED))
                painter.setFont(QFont(FONT_FAMILY, 25, QFont.Weight.Bold))
                painter.drawText(1390, 215, "EQUIPO RIVAL")

            # Cuatro compañeros identificados por OCR. Si aún no hay datos,
            # se reservan las mismas posiciones con un estado pendiente.
            team_names = list(dict.fromkeys(self.state.teammates))[:4]
            for index in range(4):
                teammate = team_names[index] if index < len(team_names) else None
                self._draw_team_card(
                    painter, 880, 242 + index * 142, 460, 125,
                    teammate, placeholder=(teammate is None),
                )

            # El overlay nunca inventa enemigos: solo muestra los ya observados.
            enemy_names = list(dict.fromkeys(self.state.enemy_kit_known.values()))[:5]
            self._draw_enemy_wide_card(
                painter, 1387, 242, 462, 115,
                enemy_names[0] if enemy_names else None,
            )
            for index in range(1, 5):
                self._draw_enemy_square(
                    painter, 1392, 402 + (index - 1) * 142,
                    76, 72,
                    enemy_names[index] if index < len(enemy_names) else None,
                )

            # Controles visuales de la maqueta; los atajos globales siguen siendo
            # los que realmente activan marcador, plano y ajustes.
            painter.setPen(QColor(*COLOR_TEXT_LIGHT))
            painter.setFont(QFont(FONT_FAMILY, 27, QFont.Weight.Bold))
            painter.drawText(1645, 58, "PARTIDA ACTUAL")
            for key, y in (("match_button", 18), ("sound_button", 83), ("settings_button", 148)):
                pix = self._load_pixmap(ICON[key])
                if pix and not pix.isNull():
                    painter.drawPixmap(QRectF(1837, y, 56, 56), pix, QRectF(pix.rect()))

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
        description = str(info.get("descripcion", "Información del operador disponible en su ficha."))
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
        points = [
            QPointF(x, y + 18), QPointF(x + 20, y), QPointF(x + w - 20, y),
            QPointF(x + w, y + 18), QPointF(x + w, y + h - 19),
            QPointF(x + w - 22, y + h), QPointF(x + 22, y + h), QPointF(x, y + h - 17),
        ]
        painter.setBrush(QColor(5, 7, 10, 215))
        painter.setPen(QPen(QColor(230, 126, 34, 235), 1.6))
        painter.drawPolygon(QPolygonF(points))

        if placeholder:
            unknown = self._load_pixmap(ICON["unknown_operator"])
            if unknown and not unknown.isNull():
                painter.drawPixmap(QRectF(x + 15, y + 28, 62, 60), unknown, QRectF(unknown.rect()))
            painter.setPen(QColor(120, 170, 205))
            painter.setFont(QFont(FONT_FAMILY, 21, QFont.Weight.Bold))
            painter.drawText(x + 94, y + 38, "ESPERANDO DETECCIÓN")
            painter.setPen(QColor(190, 190, 190))
            painter.setFont(QFont(FONT_FAMILY, 16))
            painter.drawText(QRectF(x + 94, y + 45, w - 112, 66), Qt.TextFlag.TextWordWrap,
                             "El operador aparecerá cuando sea legible en la pantalla.")
            return

        badge_path = self._operator_badge_path(operator_name)
        badge = self._load_pixmap(badge_path) if badge_path else None
        if badge and not badge.isNull():
            painter.drawPixmap(QRectF(x + 16, y + 28, 66, 66), badge, QRectF(badge.rect()))
        else:
            unknown = self._load_pixmap(ICON["unknown_operator"])
            if unknown and not unknown.isNull():
                painter.drawPixmap(QRectF(x + 16, y + 28, 62, 60), unknown, QRectF(unknown.rect()))

        name = operator_name or "Operador desconocido"
        info = get_operator_info(name) or {}
        painter.setPen(QColor(107, 171, 255))
        painter.setFont(QFont(FONT_FAMILY, 23, QFont.Weight.Bold))
        painter.drawText(x + 96, y + 35, name)
        painter.setPen(QColor(*COLOR_TEXT_LIGHT))
        painter.setFont(QFont(FONT_FAMILY, 16))
        description = self._short_description(name, info)
        painter.drawText(QRectF(x + 96, y + 43, w - 116, h - 48), Qt.TextFlag.TextWordWrap, description)

    def _draw_enemy_wide_card(self, painter: QPainter, x: int, y: int, w: int, h: int,
                              operator_name: str | None):
        points = [
            QPointF(x, y + 17), QPointF(x + 20, y), QPointF(x + w - 20, y),
            QPointF(x + w, y + 17), QPointF(x + w, y + h - 20),
            QPointF(x + w - 20, y + h), QPointF(x + 20, y + h), QPointF(x, y + h - 18),
        ]
        painter.setBrush(QColor(5, 7, 10, 215))
        painter.setPen(QPen(QColor(230, 126, 34, 235), 1.6))
        painter.drawPolygon(QPolygonF(points))
        if operator_name:
            badge_path = self._operator_badge_path(operator_name)
            badge = self._load_pixmap(badge_path) if badge_path else None
            if badge and not badge.isNull():
                painter.drawPixmap(QRectF(x + 18, y + 24, 68, 68), badge, QRectF(badge.rect()))
            painter.setPen(QColor(230, 140, 35))
            painter.setFont(QFont(FONT_FAMILY, 25, QFont.Weight.Bold))
            painter.drawText(x + 104, y + 43, operator_name)
            painter.setPen(QColor(205, 205, 205))
            painter.setFont(QFont(FONT_FAMILY, 16))
            painter.drawText(x + 104, y + 70, "Identificado en pantalla")
        else:
            painter.setPen(QColor(255, 140, 0))
            painter.setFont(QFont(FONT_FAMILY, 38, QFont.Weight.Bold))
            painter.drawText(x + 28, y + 70, "?")

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
        """Arco tipo Fortnite cerca del centro de pantalla.
        angle_deg: 0 = frente, 90 = derecha, -90 = izquierda, 180 = atrás (aprox)."""
        import math
        cx, cy = self.width() // 2, self.height() // 2 - 40
        radius = 90

        angle_rad = math.radians(self.state.sound_direction_deg - 90)
        px = cx + radius * math.cos(angle_rad)
        py = cy + radius * math.sin(angle_rad)

        alpha = int(80 + 175 * self.state.sound_intensity)
        pen = QPen(QColor(140, 255, 140, alpha), 4)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        span = 40  # grados de apertura del arco
        rect_x, rect_y = cx - radius, cy - radius
        start_angle = int((90 - self.state.sound_direction_deg - span / 2) * 16)
        span_angle = int(span * 16)
        painter.drawArc(rect_x, rect_y, radius * 2, radius * 2, start_angle, span_angle)


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
