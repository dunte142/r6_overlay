"""Hub táctico de escritorio para R6 Overlay.

Todas las rutas parten de este archivo, por lo que el proyecto puede moverse
completo de carpeta o ejecutarse desde un acceso directo de Windows.
"""
from __future__ import annotations

import os
import sys

from PyQt6.QtCore import Qt, QTimer, QSize, QObject, QEvent
from PyQt6.QtGui import QPixmap, QPainter, QColor, QLinearGradient, QBrush, QIcon, QCursor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QGridLayout, QStackedWidget,
    QFrame, QMessageBox, QDialog, QSizePolicy, QSpacerItem, QInputDialog, QBoxLayout, QLayout, QStackedLayout,
)

from data.gadgets import OPERATOR_INFO
from data.map_calibration import ALL_MAPS, get_map_image_path
from ui.assets import register_fonts, OPERATOR_PORTRAITS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ASSETS_UI = os.path.join(ASSETS_DIR, "ui")
BADGES_DIR = os.path.join(ASSETS_UI, "badges")
RECURSOS_DIR = os.path.join(ASSETS_DIR, "recursos")
INFO_BACKGROUND = os.path.join(ASSETS_DIR, "fondo_info.png")

BG = "#0c0f17"
PANEL = "#141a24"
PANEL_ALT = "#111722"
BORDER = "#263044"
TEXT = "#edf1f6"
MUTED = "#8b95a7"
GREEN = "#78b800"
ORANGE = "#e67e22"
ATTACKER_RED = "#c9363e"
BLUE = "#5e8cff"

DEFENDERS = {
    "Noor", "Denari", "Skopos", "Sentry", "Tubarao", "Fenrir", "Solis", "Azami",
    "Thorn", "Thunderbird", "Aruni", "Melusi", "Oryx", "Wamai", "Goyo", "Warden",
    "Mozzie", "Kaid", "Clash", "Maestro", "Alibi", "Vigil", "Ela", "Lesion",
    "Mira", "Echo", "Caveira", "Valkyrie", "Frost", "Mute", "Smoke", "Castle",
    "Pulse", "Doc", "Rook", "Jager", "Tachanka", "Kapkan", "Bandit",
}

MAP_DISPLAY_NAMES = {
    "Bank": "Banco", "Border": "Frontera", "Chalet": "Chalet",
    "Clubhouse": "Club", "Coastline": "Litoral", "Consulado": "Consulado",
    "Emerald Plains": "Praderas Esmeralda", "Favela": "Favela", "Fortress": "Fortaleza",
    "Kafe Dostoyevsky": "Kafe Dostoyevsky", "Kanal": "Kanal", "Lair": "Guarida",
    "Nighthaven Labs": "Laboratorio de Nighthaven", "Oregon": "Oregon", "Outback": "Outback",
    "Skyscraper": "Rascacielos", "Stadium Alpha": "Estadio Alfa", "Stadium Bravo": "Estadio Bravo",
    "Theme Park": "Parque de Atracciones", "Villa": "Villa", "Calypso Casino": "Casino Calypso",
    "Close Quarter": "Close Quarter", "Hereford Base": "Base Hereford", "House": "Casa",
    "Presidential Plane": "Avión Presidencial", "Tower": "Torre", "Yacht": "Yate",
}

MAP_RESOURCE_FILES = {
    "Bank": "BANCO", "Border": "FRONTERA", "Chalet": "CHALET",
    "Clubhouse": "CLUB", "Coastline": "LITORAL", "Consulado": "CONSULADO",
    "Emerald Plains": "PRADERAS ESMERALDA", "Favela": "FAVELA",
    "Fortress": "FORTALEZA", "Kafe Dostoyevsky": "KAFE DOSTOYEVSKY",
    "Kanal": "KANAL", "Lair": "GUARIDA", "Nighthaven Labs": "LABORATORIO DE NIGHTHAVEN",
    "Oregon": "OREGON", "Outback": "OUTBACK", "Skyscraper": "RASCACIELOS",
    "Stadium Alpha": "ESTADIO ALFA", "Stadium Bravo": "ESTADIO BRAVO",
    "Theme Park": "PARQUE DE ATRACCIONES", "Villa": "VILLA",
    "Calypso Casino": "CASINO CALYPSO", "House": "CASA",
    "Presidential Plane": "AVION PRESIDENCIAL", "Tower": "TORRE", "Yacht": "YATE",
}

DEFENDER_DETAIL_FRAMES = {
    "Noor": 2, "Denari": 3, "Skopos": 4, "Sentry": 5, "Tubarao": 6,
    "Fenrir": 7, "Wamai": 8, "Solis": 9, "Azami": 10, "Goyo": 11,
    "Warden": 12, "Lesion": 13, "Castle": 14, "Ela": 15, "Smoke": 16,
    "Bandit": 17, "Vigil": 18, "Thorn": 19, "Thunderbird": 20, "Aruni": 21,
    "Melusi": 22, "Oryx": 23, "Mozzie": 24, "Kaid": 25, "Clash": 26,
    "Maestro": 27, "Alibi": 28, "Mira": 29, "Echo": 30, "Caveira": 31,
    "Valkyrie": 32, "Frost": 33, "Mute": 34, "Pulse": 35, "Doc": 36,
    "Rook": 37, "Jager": 38, "Tachanka": 39, "Kapkan": 40,
}

ATTACKER_DETAIL_GROUPS = {
    "Solid Snake": 934, "Rauora": 1323, "Deimos": 1324, "Ram": 1325,
    "Brava": 1326, "Sens": 1327, "Osa": 1328, "Lion": 1329,
    "Maverick": 1330, "Nomad": 1331, "Nokk": 1332, "Kali": 1333,
    "Ace": 1334, "Zero": 1335, "Flores": 1336, "Finka": 1337,
    "Dokkaebi": 1338, "Zofia": 1339, "Ying": 1340, "Jackal": 1341,
    "Hibana": 1342, "Capitao": 1343, "Blackbeard": 1344, "Blitz": 1345,
    "Twitch": 1346, "Montagne": 1347, "Thermite": 1348, "Ash": 1349,
    "Thatcher": 1350, "Sledge": 1351, "Buck": 1352, "IQ": 1353,
    "Fuze": 1354, "Glaz": 1355, "Grim": 1356, "Amaru": 1357,
    "Gridlock": 1358, "Iana": 1359, "Striker": 1360,
}

ATTACKER_HOME_ICONS = {
    "Solid Snake": 1533, "Rauora": 1534, "Striker": 1535, "Deimos": 1536,
    "Ram": 1537, "Brava": 1538, "Sens": 1539, "Osa": 1540,
    "Flores": 1541, "Zero": 1542, "Ying": 1543, "Zofia": 1544,
    "Dokkaebi": 1545, "Finka": 1546, "Lion": 1547, "Maverick": 1548,
    "Nomad": 1549, "Nokk": 1550, "Kali": 1551, "Ace": 1552,
    "Jackal": 1553, "Hibana": 1554, "Capitao": 1555, "Blackbeard": 1556,
    "Buck": 1557, "Sledge": 1558, "Thatcher": 1559, "Ash": 1560,
    "Thermite": 1561, "Montagne": 1562, "Gridlock": 1563, "Iana": 1564,
    "Amaru": 1565, "Grim": 1566, "Glaz": 1567, "Fuze": 1568,
    "IQ": 1569, "Blitz": 1570, "Twitch": 1571,
}

MAP_DESCRIPTIONS = {
    "Calypso Casino": "Casino en Las Vegas con espacios abiertos, zonas de servicio y rutas de rotación interiores.",
    "Chalet": "Refugio alpino con varias rutas verticales, accesos exteriores y paredes destructibles.",
    "Bank": "Edificio bancario con bóveda subterránea, vestíbulo y conexiones verticales.",
    "Kafe Dostoyevsky": "Café de varios niveles con claraboyas, escaleras y oportunidades de control vertical.",
    "Border": "Puesto fronterizo con corredores de conexión y superficies destructibles.",
    "Hereford Base": "Instalación de entrenamiento con múltiples niveles y habitaciones conectadas.",
    "Coastline": "Complejo costero con patio central y rutas de flanqueo entre edificios.",
    "Consulado": "Complejo diplomático con oficinas, accesos exteriores y un sótano reforzable.",
    "Clubhouse": "Club de motociclistas con almacén, bar, túneles y zonas de rotación.",
    "Oregon": "Complejo rural con dormitorios, torre y conexiones subterráneas.",
    "Emerald Plains": "Mansión con alas conectadas, terrazas y rutas de acceso exteriores.",
    "Favela": "Zona urbana de calles estrechas, múltiples accesos y superficies ligeras.",
    "Fortress": "Fortaleza de varios niveles con patios interiores y espacios de transición.",
    "Kanal": "Instalación portuaria dividida por canales y conectada por puentes.",
    "Lair": "Instalación subterránea con pasillos y sectores de distintas alturas.",
    "Nighthaven Labs": "Complejo de investigación con salas conectadas y líneas de visión largas.",
    "Outback": "Parador de carretera con zonas de servicio y rutas laterales.",
    "Skyscraper": "Rascacielos con alas conectadas, terrazas y zonas abiertas.",
    "Stadium Alpha": "Estadio con sectores conectados y espacios de combate interiores.",
    "Stadium Bravo": "Estadio con áreas de transición, accesos laterales y líneas de tiro.",
    "Theme Park": "Parque de atracciones con edificios conectados y múltiples rutas interiores.",
    "Villa": "Villa de varios niveles con patios y amplias posibilidades de rotación vertical.",
    "Close Quarter": "Entorno compacto de combate cercano; verificá la disponibilidad del plano para cada piso.",
    "House": "Casa residencial con habitaciones pequeñas y accesos por ventanas y puertas.",
    "Presidential Plane": "Avión de fuselaje estrecho con corredores largos y compartimentos reducidos.",
    "Tower": "Torre con pasillos interiores y varios accesos a diferentes alturas.",
    "Yacht": "Yate con pasillos estrechos, cubiertas y compartimentos interiores.",
}

FLOOR_LABELS = ["SÓTANO", "PRIMER PISO", "SEGUNDO PISO", "TEJADO"]
FLOOR_KEYS = {
    "SÓTANO": "Sotano", "PRIMER PISO": "Primer Piso",
    "SEGUNDO PISO": "Segundo Piso", "TEJADO": "Tejado",
}

APP_STYLE = f"""
QMainWindow, QWidget {{ background: {BG}; color: {TEXT}; }}
QLabel {{ color: {TEXT}; font-family: 'Barlow Condensed', 'Segoe UI', sans-serif; }}
QScrollArea {{ background: transparent; border: none; }}
QScrollArea#globalLauncherScroll {{ background: {BG}; border: none; }}
QScrollBar:vertical {{ background: #111722; width: 9px; border: none; margin: 0; }}
QScrollBar::handle:vertical {{ background: {GREEN}; min-height: 24px; border-radius: 4px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ background: #111722; height: 9px; border: none; margin: 0; }}
QScrollBar::handle:horizontal {{ background: #344056; min-width: 24px; border-radius: 4px; }}
QPushButton {{ color: {TEXT}; background: {PANEL}; border: 1px solid {BORDER}; border-radius: 5px; padding: 8px 12px; }}
QPushButton:hover {{ border-color: {GREEN}; background: #1a2330; }}
QPushButton:pressed {{ background: #202c3b; }}
"""


def clear_layout(layout):
    """Vacia widgets/layouts anidados evitando dejar las vistas anteriores vivas."""
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        child_layout = item.layout()
        if widget is not None:
            widget.deleteLater()
        elif child_layout is not None:
            clear_layout(child_layout)


def label(text: str = "", *, color: str = TEXT, size: int = 12,
          bold: bool = False, wrap: bool = False) -> QLabel:
    result = QLabel(text)
    result.setWordWrap(wrap)
    result.setStyleSheet(f"background: transparent; color: {color}; font-size: {size}px; {'font-weight: bold;' if bold else ''}")
    return result


def card_frame() -> QFrame:
    frame = QFrame()
    frame.setObjectName("surfaceCard")
    frame.setStyleSheet(f"QFrame#surfaceCard {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 7px; }}")
    return frame


class MapCardHoverRelay(QObject):
    """Propaga Enter/Leave de la imagen y el título al botón contenedor."""
    def __init__(self, button: QPushButton, title: QLabel):
        super().__init__(button)
        self.button = button
        self.title = title
        self._hovered = False
        for widget in [button, *button.findChildren(QWidget)]:
            widget.installEventFilter(self)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.Enter:
            self._set_hovered(True)
        elif event.type() == QEvent.Type.Leave:
            QTimer.singleShot(0, self._refresh_hover)
        return False

    def _refresh_hover(self):
        target = QApplication.widgetAt(QCursor.pos())
        inside = target is self.button or (target is not None and self.button.isAncestorOf(target))
        self._set_hovered(inside)

    def _set_hovered(self, hovered: bool):
        if self._hovered == hovered:
            return
        self._hovered = hovered
        if hovered:
            self.button.setStyleSheet(
                f"QPushButton {{ background: #11151b; border: 2px solid {GREEN}; padding: 0; }}"
            )
        else:
            self.button.setStyleSheet(
                "QPushButton { background: #11151b; border: 1px solid #292d34; padding: 0; }"
            )


class HeroBanner(QWidget):
    """Banner superior reconstruido con el fondo local y elementos nativos."""
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self._pixmap = QPixmap(image_path) if os.path.isfile(image_path) else QPixmap()
        self.setMinimumHeight(320)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("background: #0c0f17; border: none;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 18, 12)
        layout.setSpacing(0)
        top = QHBoxLayout()
        top.addStretch(1)
        app_icon = QLabel()
        app_icon.setPixmap(QPixmap(os.path.join(ASSETS_DIR, "icono app.png")).scaled(
            58, 58, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation,
        ))
        app_icon.setFixedSize(58, 58)
        app_icon.setStyleSheet("background: transparent;")
        top.addWidget(app_icon, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        layout.addLayout(top)
        layout.addStretch(1)

        bottom = QHBoxLayout()
        bottom.setSpacing(10)
        title = QLabel("RANKED 3.0 UPDATE")
        title.setStyleSheet("color: white; font-size: 25px; font-weight: 900; background: transparent; border: none;")
        bottom.addWidget(title, 0, Qt.AlignmentFlag.AlignBottom)
        date = QLabel("17/05/2026")
        date.setStyleSheet("color: #d0d0d0; font-size: 10px; background: transparent; border: none;")
        bottom.addWidget(date, 0, Qt.AlignmentFlag.AlignBottom)
        line = QFrame()
        line.setFixedHeight(2)
        line.setStyleSheet("background: #78b800; border: none;")
        bottom.addWidget(line, 1, Qt.AlignmentFlag.AlignBottom)
        news = QLabel("NOTICIAS")
        news.setStyleSheet("color: #a3e600; font-size: 13px; font-weight: 900; background: transparent; border: none;")
        bottom.addWidget(news, 0, Qt.AlignmentFlag.AlignBottom)
        layout.addLayout(bottom)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.fillRect(self.rect(), QColor(BG))
        if not self._pixmap.isNull() and self.width() > 0 and self.height() > 0:
            # Cubre el área completa y recorta desde el centro sin deformar el arte.
            scaled = self._pixmap.scaled(
                self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(0, 0, 0, 45))
        gradient.setColorAt(0.45, QColor(0, 0, 0, 65))
        gradient.setColorAt(0.78, QColor(0, 0, 0, 180))
        gradient.setColorAt(1.0, QColor(0, 0, 0, 245))
        painter.fillRect(self.rect(), QBrush(gradient))
        painter.end()


class InfoBackground(QWidget):
    """Panel que cubre su área con el fondo texturizado de las referencias."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = QPixmap(INFO_BACKGROUND) if os.path.isfile(INFO_BACKGROUND) else QPixmap()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(BG))
        if not self._pixmap.isNull() and self.width() > 0 and self.height() > 0:
            scaled = self._pixmap.scaled(
                self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.drawPixmap(
                (self.width() - scaled.width()) // 2,
                (self.height() - scaled.height()) // 2,
                scaled,
            )
        painter.end()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajustes tácticos")
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setStyleSheet(APP_STYLE)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addWidget(label("AJUSTES Y CONTROLES", color=GREEN, size=19, bold=True))
        layout.addWidget(label("Atajos globales del overlay", color=ORANGE, size=13, bold=True))
        for key, description in [
            ("F1", "Mostrar u ocultar el HUD táctico nuevo"),
            ("F2", "Abrir o cerrar el plano y minimapa"),
            ("F3", "Mostrar u ocultar la bitácora del dron"),
            ("F4", "Cambiar al siguiente mapa"),
            ("F5", "Corregir manualmente el bando"),
            ("F6", "Ciclar/corregir el operador propio"),
        ]:
            row = QHBoxLayout()
            key_lbl = label(key, color=GREEN, size=13, bold=True)
            key_lbl.setFixedWidth(40)
            row.addWidget(key_lbl)
            row.addWidget(label(description, color=TEXT, size=12, wrap=True), 1)
            layout.addLayout(row)
        layout.addWidget(label("La lectura de visión usa solo píxeles visibles en pantalla. No consulta la memoria del juego ni APIs privadas.", color=MUTED, size=11, wrap=True))
        close_btn = QPushButton("CERRAR")
        close_btn.setStyleSheet(f"background: {GREEN}; color: #0c0f17; font-weight: bold; border: none;")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)


class R6Launcher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rainbow Six Siege — Tactical Assistant Hub")
        self.setWindowIcon(QIcon(os.path.join(ASSETS_DIR, "icono app.png")))
        self.resize(1440, 960)
        self.setMinimumSize(900, 650)
        self.setStyleSheet(APP_STYLE)

        # Un único scroll vertical envuelve el fondo, la navegación y el contenido.
        # No hay QScrollArea dentro de Noticias, Agentes ni Mapas.
        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        self.global_scroll = QScrollArea(central)
        self.global_scroll.setObjectName("globalLauncherScroll")
        self.global_scroll.setWidgetResizable(True)
        self.global_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.global_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.global_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.global_scroll.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.document = QWidget()
        self.document.setObjectName("launcherDocument")
        self.document.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.root_layout = QVBoxLayout(self.document)
        self.root_layout.setContentsMargins(16, 8, 16, 14)
        self.root_layout.setSpacing(8)
        self.root_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)

        self.global_scroll.setWidget(self.document)
        central_layout.addWidget(self.global_scroll)
        self.setCentralWidget(central)

        # La composición se dibuja con widgets sobre el nuevo fondo local;
        # launcher_hero.png queda solo como referencia visual y no se muestra.
        self.hero_banner = HeroBanner(os.path.join(ASSETS_DIR, "fondo home.png"))
        self.hero_banner.setFixedHeight(self._hero_height())
        self.top_panel_host = QWidget()
        top_panel_layout = QVBoxLayout(self.top_panel_host)
        top_panel_layout.setContentsMargins(0, 0, 0, 0)
        top_panel_layout.setSpacing(0)
        top_panel_layout.addWidget(self.hero_banner)
        compact_header = QWidget()
        compact_header.setFixedHeight(46)
        compact_header.setStyleSheet("background: #0b0b0b;")
        compact_layout = QHBoxLayout(compact_header)
        compact_layout.setContentsMargins(8, 0, 8, 0)
        compact_layout.setSpacing(10)
        compact_layout.addWidget(label("RANKED 3.0 UPDATE", color=TEXT, size=20, bold=True))
        compact_layout.addWidget(label("17/05/2026", color="#d0d0d0", size=10))
        compact_line = QFrame()
        compact_line.setFixedHeight(2)
        compact_line.setStyleSheet(f"background: {GREEN}; border: none;")
        compact_layout.addWidget(compact_line, 1, Qt.AlignmentFlag.AlignVCenter)
        compact_layout.addWidget(label("NOTICIAS", color="#a3e600", size=14, bold=True))
        compact_icon = QLabel()
        compact_icon.setPixmap(QPixmap(os.path.join(ASSETS_DIR, "icono app.png")).scaled(
            42, 42, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation,
        ))
        compact_icon.setFixedSize(42, 42)
        compact_icon.setStyleSheet("background: transparent;")
        compact_layout.addWidget(compact_icon)
        compact_header.hide()
        top_panel_layout.addWidget(compact_header)
        self.compact_header = compact_header
        self.root_layout.addWidget(self.top_panel_host)
        self._build_navigation_tabs()

        # Un único contenedor ocupa siempre el mismo lugar debajo de la navegación.
        self.stack = QStackedWidget()
        self.stack.setObjectName("mainContentStack")
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.stack.setMinimumHeight(640)
        self.root_layout.addWidget(self.stack, 0)

        self._init_landing_section()
        self._init_agents_section()
        self._init_maps_section()
        self._on_tab_click(0)


    def _hero_height(self) -> int:
        """Mantiene la proporción horizontal del fondo del banner."""
        content_w = max(900, self.width() - 48)
        # El documento conserva el formato desplazable del launcher; el banner
        # mantiene la proporción del fondo sin forzar todo el contenido a entrar.
        return max(360, int(content_w * 805 / 1920))

    def resizeEvent(self, event):
        if hasattr(self, "hero_banner"):
            self.hero_banner.setFixedHeight(self._hero_height())
        super().resizeEvent(event)
        if hasattr(self, "stack"):
            QTimer.singleShot(0, self._sync_global_scroll_document)
        if (hasattr(self, "agents_stack") and self.stack.currentIndex() == 1
                and self.agents_stack.currentIndex() == 1):
            QTimer.singleShot(0, self._resize_operator_detail)
        if (hasattr(self, "maps_stack") and self.stack.currentIndex() == 2
                and self.maps_stack.currentIndex() == 1):
            if getattr(self, "map_resource_pixmap", None) is not None:
                QTimer.singleShot(0, self._resize_map_resource)
            elif hasattr(self, "current_info_map"):
                QTimer.singleShot(0, lambda: self._update_map_floor_image(
                    self.current_info_map, self.current_floor_label,
                ))


    def _open_settings(self):
        SettingsDialog(self).exec()

    def _build_navigation_tabs(self):
        shell = QWidget()
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.addStretch(1)

        self.btn_tab_noticias = QPushButton("NOTICIAS")
        self.btn_tab_agentes = QPushButton("AGENTES")
        self.btn_tab_mapas = QPushButton("MAPAS")
        self.nav_btns = [self.btn_tab_noticias, self.btn_tab_agentes, self.btn_tab_mapas]
        for index, button in enumerate(self.nav_btns):
            button.setMinimumWidth(100)
            button.setMinimumHeight(39)
            button.clicked.connect(lambda _checked=False, i=index: self._on_tab_click(i))
            row.addWidget(button)
        row.addStretch(1)

        search = QPushButton("⌕")
        search.setToolTip("Buscar en el catálogo")
        search.setFixedSize(34, 34)
        search.setStyleSheet("QPushButton { background: transparent; border: none; color: #bfc4ca; font-size: 23px; } QPushButton:hover { color: #ffffff; }")
        search.clicked.connect(self._focus_current_search)
        row.addWidget(search)

        gear = QPushButton("⚙")
        gear.setToolTip("Ajustes y atajos")
        gear.setFixedSize(34, 34)
        gear.setStyleSheet("QPushButton { background: transparent; border: none; color: #bfc4ca; font-size: 19px; } QPushButton:hover { color: #ffffff; }")
        gear.clicked.connect(self._open_settings)
        row.addWidget(gear)
        shell_layout.addLayout(row)

        underline = QFrame()
        underline.setFixedHeight(2)
        underline.setStyleSheet(f"background: {ORANGE}; border: none;")
        shell_layout.addWidget(underline)
        self.root_layout.addWidget(shell)

    def _active_document_page(self) -> QWidget | None:
        """Devuelve la página visible real, también dentro de los stacks internos."""
        if not hasattr(self, "stack"):
            return None
        page = self.stack.currentWidget()
        if isinstance(page, QStackedWidget):
            return page.currentWidget()
        return page

    def _sync_global_scroll_document(self):
        """Ajusta la altura del único documento al contenido de la pestaña activa."""
        page = self._active_document_page()
        if page is None:
            return
        page.ensurePolished()
        page_layout = page.layout()
        if page_layout is not None:
            page_layout.activate()
        hint = page.sizeHint().height()
        minimum = page.minimumSizeHint().height()
        # Noticias conserva su panel desplazable; agentes/mapas crecen según
        # sus grillas y mantienen el desplazamiento global.
        document_height = max(640, int(hint), int(minimum))
        self.stack.setFixedHeight(document_height)
        self.stack.updateGeometry()
        self.document.adjustSize()
        self.document.updateGeometry()

    def _set_inner_page(self, stack: QStackedWidget, index: int):
        stack.setCurrentIndex(index)
        self._sync_global_scroll_document()

    def _focus_current_search(self):
        if self.stack.currentIndex() not in (1, 2):
            return
        prompt = "Buscar operador" if self.stack.currentIndex() == 1 else "Buscar mapa"
        value, accepted = QInputDialog.getText(self, "Búsqueda táctica", prompt + ":")
        if not accepted:
            return
        term = value.strip().casefold()
        if self.stack.currentIndex() == 1:
            self.agent_search_term = term
            self._render_agents_grid(self.current_agent_side == "Defensor")
        elif self.stack.currentIndex() == 2:
            visible = 0
            for button, internal_name, display_name in getattr(self, "map_buttons", []):
                match = not term or term in internal_name.casefold() or term in display_name.casefold()
                button.setVisible(match)
                visible += int(match)
            columns = max(2, min(5, (self.width() - 100) // 235))
            rows = (visible + columns - 1) // columns
            tile_height = getattr(self, "map_tile_height", 132)
            self.map_grid_content.setMinimumHeight(max(160, rows * tile_height + max(0, rows - 1) * 16 + 20))
            self._sync_global_scroll_document()

    def _on_tab_click(self, index: int):
        # Volver al grid de la pestaña elegida; el encabezado y la barra no se
        # reconstruyen, solo cambia el contenido del panel central.
        if index == 1 and hasattr(self, "agents_stack"):
            self.agents_stack.setCurrentIndex(0)
        elif index == 2 and hasattr(self, "maps_stack"):
            self.maps_stack.setCurrentIndex(0)
        self.stack.setCurrentIndex(index)
        if hasattr(self, "compact_header"):
            self.hero_banner.setVisible(index == 0)
            self.compact_header.setVisible(index != 0)
        # El tamaño del documento sigue el contenido activo; las otras
        # categorías no fuerzan espacio vacío al final de esta pestaña.
        self._sync_global_scroll_document()
        # Al cambiar de categoría se vuelve al inicio del único documento.
        self.global_scroll.verticalScrollBar().setValue(0)
        for i, button in enumerate(self.nav_btns):
            if i == index:
                button.setStyleSheet(f"QPushButton {{ background: transparent; border: none; border-top: 2px solid {ORANGE}; color: #ffffff; font-size: 13px; font-weight: 900; padding: 6px 14px; border-radius: 0; }}")
            else:
                button.setStyleSheet(f"QPushButton {{ background: transparent; border: none; color: {MUTED}; font-size: 13px; font-weight: 800; padding: 6px 14px; }} QPushButton:hover {{ color: {GREEN}; }}")

    def _init_landing_section(self):
        screen = self.screen() or QApplication.primaryScreen()
        reference_width = screen.availableGeometry().width() if screen else self.width()
        page = QWidget()
        page.setStyleSheet("background: #000000;")
        page.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 78, 0, 0)
        layout.setSpacing(0)

        body = QHBoxLayout()
        side_margin = int(reference_width * 0.14)
        body.setContentsMargins(side_margin, 0, side_margin, 0)
        body.setSpacing(max(32, int(reference_width * 0.045)))

        gallery = QWidget()
        gallery.setStyleSheet("background: transparent;")
        grid = QGridLayout(gallery)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(max(56, int(reference_width * 0.08)))
        grid.setVerticalSpacing(max(32, int(reference_width * 0.04)))

        tile_height = max(140, min(220, int(reference_width * 0.11)))
        for index in range(4):
            tile = QFrame()
            tile.setFixedHeight(tile_height)
            tile.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            tile.setStyleSheet("QFrame { background: #d8d8d8; border: none; }")
            grid.addWidget(tile, index // 2, index % 2)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        body.addWidget(gallery, 1)

        next_button = QPushButton()
        next_button.setIcon(QIcon(os.path.join(ASSETS_DIR, "flecha.png")))
        next_button.setIconSize(QSize(64, 82))
        next_button.setFixedSize(72, 90)
        next_button.setStyleSheet("QPushButton { background: transparent; border: none; padding: 0; }")
        body.addWidget(next_button, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addLayout(body)
        layout.addStretch(1)

        page.setMinimumHeight(660)
        self.stack.addWidget(page)

    def _badge_pixmap(self, name: str, size: QSize) -> QPixmap:
        candidates = [os.path.join(BADGES_DIR, f"{name}.png"),
                      os.path.join(BADGES_DIR, f"{name.replace(' ', '_')}.png")]
        path = next((candidate for candidate in candidates if os.path.isfile(candidate)), None)
        pixmap = QPixmap(path) if path else QPixmap()
        if not pixmap.isNull():
            return pixmap.scaled(size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        return QPixmap()

    def _operator_detail_resource(self, name: str) -> str | None:
        if name in DEFENDERS:
            frame = DEFENDER_DETAIL_FRAMES.get(name)
            filename = f"Frame {frame}.png" if frame is not None else None
            side = "defensores"
        else:
            group = ATTACKER_DETAIL_GROUPS.get(name)
            filename = f"Group {group}.png" if group is not None else None
            side = "atacantes"
        candidate = os.path.join(RECURSOS_DIR, side, filename) if filename else None
        if candidate and os.path.isfile(candidate):
            return candidate

        # Si falta una ficha completa, conservar el arte detallado sin panel.
        source_path = OPERATOR_PORTRAITS.get(name)
        if not source_path:
            return None
        side = "defensores" if name in DEFENDERS else "atacantes"
        fallback = os.path.join(RECURSOS_DIR, f"{side} in game", os.path.basename(source_path))
        return fallback if os.path.isfile(fallback) else source_path

    def _operator_icon(self, name: str, size: int = 60) -> QWidget:
        if name not in DEFENDERS:
            group = ATTACKER_HOME_ICONS.get(name)
            path = os.path.join(RECURSOS_DIR, "atacantes_home", f"Group {group}.png") if group else None
            pixmap = QPixmap(path) if path and os.path.isfile(path) else QPixmap()
            if not pixmap.isNull():
                target = QSize(round(size * 0.82), size)
                pixmap = pixmap.scaled(target, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                image = QLabel()
                image.setPixmap(pixmap)
                image.setAlignment(Qt.AlignmentFlag.AlignCenter)
                image.setFixedSize(target.width() + 4, target.height() + 4)
                return image
        else:
            pixmap = self._badge_pixmap(name, QSize(size, size))
        if not pixmap.isNull():
            image = QLabel()
            image.setPixmap(pixmap)
            image.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image.setFixedSize(size + 8, size + 8)
            return image
        placeholder = QFrame()
        placeholder.setFixedSize(size + 8, size + 8)
        placeholder.setStyleSheet(f"QFrame {{ background: #202a38; border: 1px solid {GREEN}; border-radius: 4px; }}")
        pl = QVBoxLayout(placeholder)
        pl.setContentsMargins(2, 2, 2, 2)
        initials = "".join(part[0] for part in name.split()[:2]).upper()
        initials_label = label(initials or "?", color=GREEN, size=max(13, size // 3), bold=True)
        initials_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pl.addWidget(initials_label)
        return placeholder

    def _init_agents_section(self):
        self.agents_stack = QStackedWidget()
        self.agents_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        grid_page = InfoBackground()
        page_layout = QVBoxLayout(grid_page)
        page_layout.setContentsMargins(8, 8, 8, 8)
        filter_bar = QHBoxLayout()
        filter_bar.addWidget(label("CATÁLOGO DE OPERADORES", color=GREEN, size=16, bold=True))
        filter_bar.addStretch(1)
        self.btn_f_def = QPushButton("DEFENSORES")
        self.btn_f_atk = QPushButton("ATACANTES")
        self.btn_f_def.clicked.connect(lambda: self._render_agents_grid(True))
        self.btn_f_atk.clicked.connect(lambda: self._render_agents_grid(False))
        filter_bar.addWidget(self.btn_f_def)
        filter_bar.addWidget(self.btn_f_atk)
        page_layout.addLayout(filter_bar)

        grid_content = QWidget()
        grid_content.setStyleSheet("background: transparent;")
        self.agent_grid_layout = QGridLayout(grid_content)
        self.agent_grid_layout.setContentsMargins(2, 8, 5, 10)
        self.agent_grid_layout.setHorizontalSpacing(12)
        self.agent_grid_layout.setVerticalSpacing(12)
        self.agent_grid_content = grid_content
        page_layout.addWidget(grid_content, 0, Qt.AlignmentFlag.AlignTop)
        self.agents_stack.addWidget(grid_page)

        self.agent_detail_view = InfoBackground()
        self.detail_layout = QVBoxLayout(self.agent_detail_view)
        self.detail_layout.setContentsMargins(4, 12, 4, 12)
        self.detail_layout.setSpacing(20)
        self.agent_detail_view.setMinimumHeight(500)
        self.agents_stack.addWidget(self.agent_detail_view)
        self.stack.addWidget(self.agents_stack)
        self._render_agents_grid(True)

    def _render_agents_grid(self, is_defender: bool = True):
        self.current_agent_side = "Defensor" if is_defender else "Atacante"
        active_color = GREEN if is_defender else ATTACKER_RED
        inactive_hover = ATTACKER_RED if not is_defender else GREEN
        active_style = f"QPushButton {{ background: {active_color}; color: #0c0f17; font-weight: 900; border: none; padding: 8px 18px; }}"
        inactive_style = f"QPushButton {{ background: #151b26; color: {MUTED}; font-weight: 800; border: 1px solid {BORDER}; padding: 8px 18px; }} QPushButton:hover {{ color: {TEXT}; border-color: {inactive_hover}; }}"
        self.btn_f_def.setStyleSheet(active_style if is_defender else inactive_style)
        self.btn_f_atk.setStyleSheet(inactive_style if is_defender else active_style)
        clear_layout(self.agent_grid_layout)
        self.agent_grid_layout.setHorizontalSpacing(12 if is_defender else 10)
        self.agent_grid_layout.setVerticalSpacing(12 if is_defender else 10)

        term = getattr(self, "agent_search_term", "")
        operators = [name for name in OPERATOR_INFO if (name in DEFENDERS) == is_defender and (not term or term in name.casefold())]
        columns = max(2, min(8 if not is_defender else 6, (self.width() - 70) // (136 if not is_defender else 142)))
        for idx, name in enumerate(operators):
            info = OPERATOR_INFO[name]
            button = QPushButton()
            if is_defender:
                button.setMinimumSize(120, 128)
                button.setMaximumSize(190, 160)
                button.setStyleSheet(f"QPushButton {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 7px; padding: 7px; }} QPushButton:hover {{ background: #1a2432; border: 1px solid {GREEN}; }}")
            else:
                button.setFixedSize(126, 154)
                button.setStyleSheet(f"QPushButton {{ background: transparent; border: 1px solid transparent; padding: 0; }} QPushButton:hover {{ background: transparent; border: 1px solid #ff5058; }}")
            cl = QVBoxLayout(button)
            cl.setContentsMargins(1, 1, 1, 1) if not is_defender else cl.setContentsMargins(3, 3, 3, 3)
            cl.setSpacing(4)
            cl.addWidget(self._operator_icon(name, 146 if not is_defender else 62), alignment=Qt.AlignmentFlag.AlignHCenter)
            if is_defender:
                cl.addWidget(label(name.upper(), color=TEXT, size=11, bold=True), alignment=Qt.AlignmentFlag.AlignHCenter)
                cl.addWidget(label(info.get("gadget", "DISPOSITIVO"), color=GREEN, size=9, wrap=True), alignment=Qt.AlignmentFlag.AlignHCenter)
            button.clicked.connect(lambda _checked=False, n=name, d=info, defender=is_defender: self._display_agent_details(n, d, defender))
            self.agent_grid_layout.addWidget(button, idx // columns, idx % columns)
        rows = (len(operators) + columns - 1) // columns
        self.agent_grid_layout.setRowStretch(rows, 0)
        card_height = 136 if is_defender else 154
        grid_spacing = 12 if is_defender else 10
        self.agent_grid_content.setMinimumHeight(max(150, rows * card_height + max(0, rows - 1) * grid_spacing + 24))
        self.agent_grid_content.adjustSize()

    def _display_agent_details(self, name: str, info: dict, is_defender: bool):
        clear_layout(self.detail_layout)
        self.detail_layout.setDirection(QBoxLayout.Direction.TopToBottom)
        self.detail_layout.setContentsMargins(18, 12, 18, 18)
        self.detail_layout.setSpacing(10)

        side_row = QHBoxLayout()
        side_row.setContentsMargins(0, 0, 0, 0)
        active_side = QPushButton("DEFENSORES" if is_defender else "ATACANTES")
        inactive_side = QPushButton("ATACANTES" if is_defender else "DEFENSORES")
        active_side.setStyleSheet(f"QPushButton {{ background: {GREEN}; color: white; border: none; border-radius: 0; padding: 3px 9px; font-size: 16px; font-weight: 900; }}")
        inactive_side.setStyleSheet("QPushButton { background: transparent; color: white; border: none; padding: 3px 9px; font-size: 16px; font-weight: 700; }")
        active_side.clicked.connect(lambda: self._set_inner_page(self.agents_stack, 0))
        inactive_side.clicked.connect(lambda: (self._render_agents_grid(not is_defender), self._set_inner_page(self.agents_stack, 0)))
        if is_defender:
            side_row.addWidget(active_side)
            side_row.addStretch(1)
            side_row.addWidget(inactive_side)
        else:
            side_row.addWidget(inactive_side)
            side_row.addStretch(1)
            side_row.addWidget(active_side)
        self.detail_layout.addLayout(side_row)

        resource_path = self._operator_detail_resource(name)
        self.operator_detail_pixmap = QPixmap(resource_path) if resource_path and os.path.isfile(resource_path) else QPixmap()
        self.operator_detail_label = QLabel()
        self.operator_detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.operator_detail_label.setStyleSheet("background: transparent;")
        self.operator_detail_label.setMinimumSize(600, 380)
        self.operator_detail_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        if self.operator_detail_pixmap.isNull():
            self.operator_detail_label.setText(f"{name.upper()}\n\n{info.get('descripcion', 'Descripcion no disponible.')}")
            self.operator_detail_label.setWordWrap(True)
            self.operator_detail_label.setStyleSheet(f"background: transparent; color: {TEXT}; font-size: 18px;")
        self.detail_layout.addWidget(self.operator_detail_label, 1)
        self._resize_operator_detail()
        self.agents_stack.setCurrentIndex(1)
        self._sync_global_scroll_document()

    def _resize_operator_detail(self):
        if getattr(self, "operator_detail_pixmap", QPixmap()).isNull():
            return
        self.operator_detail_label.setPixmap(self.operator_detail_pixmap.scaled(
            max(600, self.width() - 76), max(380, self.stack.height() - 78),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))

    def _init_maps_section(self):
        self.maps_stack = QStackedWidget()
        self.maps_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        grid_page = InfoBackground()
        grid_layout = QVBoxLayout(grid_page)
        grid_layout.setContentsMargins(8, 38, 8, 18)
        map_content = QWidget()
        map_content.setStyleSheet("background: transparent;")
        self.map_grid_layout = QGridLayout(map_content)
        self.map_grid_layout.setContentsMargins(2, 0, 5, 10)
        self.map_grid_layout.setHorizontalSpacing(16)
        self.map_grid_layout.setVerticalSpacing(16)

        self.map_buttons = []
        map_columns = max(2, min(5, (self.width() - 100) // 235))
        tile_width = max(180, min(320, (self.width() - 124 - (map_columns - 1) * 16) // map_columns))
        tile_height = max(100, int(tile_width * 0.46))
        self.map_tile_height = tile_height
        for column in range(map_columns):
            self.map_grid_layout.setColumnStretch(column, 1)
        for idx, internal_name in enumerate(ALL_MAPS):
            display_name = MAP_RESOURCE_FILES.get(
                internal_name, MAP_DISPLAY_NAMES.get(internal_name, internal_name),
            )
            button = QPushButton()
            button.setMinimumSize(tile_width, tile_height)
            button.setMaximumSize(tile_width + 40, tile_height + 20)
            button.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
            button.setStyleSheet("QPushButton { background: #11151b; border: 1px solid #292d34; border-radius: 0; padding: 0; }")

            tile = QWidget()
            tile.setStyleSheet("background: transparent;")
            tile.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            tile_layout = QStackedLayout(tile)
            tile_layout.setContentsMargins(0, 0, 0, 0)
            tile_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
            preview = QLabel()
            preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            preview.setPixmap(self._map_cover_pixmap(internal_name, QSize(tile_width, tile_height)))
            preview.setStyleSheet("background: #10141b;")
            title = label(display_name, color=ORANGE, size=20, bold=True, wrap=True)
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet("background: rgba(0, 0, 0, 92); color: #ff8a00; font-size: 20px; font-weight: 900; padding: 3px 8px;")
            title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            preview.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            tile_layout.addWidget(preview)
            tile_layout.addWidget(title)
            tile_layout.setCurrentWidget(title)
            bl = QVBoxLayout(button)
            bl.setContentsMargins(2, 2, 2, 2)
            bl.addWidget(tile)
            button._hover_relay = MapCardHoverRelay(button, title)
            button.clicked.connect(lambda _checked=False, m=internal_name: self._display_map_info(m))
            self.map_grid_layout.addWidget(button, idx // map_columns, idx % map_columns)
            self.map_buttons.append((button, internal_name, display_name))

        self.map_grid_content = map_content
        map_rows = (len(ALL_MAPS) + map_columns - 1) // map_columns
        self.map_grid_content.setMinimumHeight(max(160, map_rows * tile_height + max(0, map_rows - 1) * 16 + 20))
        grid_layout.addWidget(map_content, 0, Qt.AlignmentFlag.AlignTop)
        self.maps_stack.addWidget(grid_page)

        self.map_detail_page = InfoBackground()
        self.map_view_layout = QVBoxLayout(self.map_detail_page)
        self.map_view_layout.setContentsMargins(0, 5, 0, 0)
        self.map_view_layout.setSpacing(12)
        self.map_detail_page.setMinimumHeight(480)
        self.maps_stack.addWidget(self.map_detail_page)
        self.stack.addWidget(self.maps_stack)

    def _map_cover_pixmap(self, internal_name: str, size: QSize) -> QPixmap:
        stem = MAP_RESOURCE_FILES.get(internal_name)
        resource_path = os.path.join(RECURSOS_DIR, "mapas", f"{stem}.png") if stem else None
        source = QPixmap(resource_path) if resource_path and os.path.isfile(resource_path) else QPixmap()
        if not source.isNull():
            x = int(source.width() * 0.10)
            y = int(source.height() * 0.28)
            crop_w = int(source.width() * 0.40)
            crop_h = int(source.height() * 0.50)
            source = source.copy(x, y, crop_w, crop_h)
        else:
            preview_path = self._find_map_preview(internal_name)
            source = QPixmap(preview_path) if preview_path else QPixmap()
        if source.isNull():
            return QPixmap()
        scaled = source.scaled(size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        x = max(0, (scaled.width() - size.width()) // 2)
        y = max(0, (scaled.height() - size.height()) // 2)
        return scaled.copy(x, y, min(size.width(), scaled.width()), min(size.height(), scaled.height()))

    def _find_map_preview(self, internal_name: str) -> str | None:
        for floor in ("Primer Piso", "Segundo Piso", "Sotano", "Tejado", "Piso Extra"):
            path = get_map_image_path(internal_name, floor)
            if path and os.path.isfile(path):
                return path
        return None

    def _display_map_info(self, internal_map: str):
        clear_layout(self.map_view_layout)
        self.current_info_map = internal_map
        display_name = MAP_DISPLAY_NAMES.get(internal_map, internal_map)
        self.map_resource_pixmap = None
        self.map_resource_label = None

        resource_stem = MAP_RESOURCE_FILES.get(internal_map)
        resource_path = os.path.join(RECURSOS_DIR, "mapas", f"{resource_stem}.png") if resource_stem else None
        resource_pixmap = QPixmap(resource_path) if resource_path and os.path.isfile(resource_path) else QPixmap()
        if not resource_pixmap.isNull():
            # Los PNG de recursos incluyen la composición completa. Se recorta
            # su cabecera para conservar la navegación nativa del launcher.
            top_crop = min(220, max(0, resource_pixmap.height() - 1))
            self.map_resource_pixmap = resource_pixmap.copy(
                0, top_crop, resource_pixmap.width(), resource_pixmap.height() - top_crop,
            )
            self.map_resource_label = QLabel()
            self.map_resource_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.map_resource_label.setStyleSheet("background: transparent;")
            self.map_resource_label.setMinimumSize(600, 380)
            self.map_resource_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.map_view_layout.addWidget(self.map_resource_label, 1)
            self._resize_map_resource()
            self.maps_stack.setCurrentIndex(1)
            self._sync_global_scroll_document()
            return

        self.floor_buttons: dict[str, QPushButton] = {}
        self.floor_thumbnails: dict[str, QPushButton] = {}

        header = QHBoxLayout()
        header.addStretch(1)
        for floor_label in FLOOR_LABELS:
            button = QPushButton(FLOOR_KEYS.get(floor_label, floor_label).upper())
            button.setFlat(True)
            button.setStyleSheet("QPushButton { background: transparent; color: white; border: none; border-bottom: 2px solid transparent; padding: 5px 9px; font-size: 14px; font-weight: 700; } QPushButton:hover { color: #a3e600; }")
            button.clicked.connect(lambda _checked=False, m=internal_map, fl=floor_label: self._update_map_floor_image(m, fl))
            self.floor_buttons[floor_label] = button
            header.addWidget(button)
        self.map_view_layout.addLayout(header)

        body = QHBoxLayout()
        body.setSpacing(24)
        left = QVBoxLayout()
        left.setSpacing(10)
        self.lbl_plan_img = QLabel("Plano no disponible")
        self.lbl_plan_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_plan_img.setMinimumSize(380, 250)
        self.lbl_plan_img.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.lbl_plan_img.setStyleSheet("background: rgba(8, 10, 14, 210); border: 1px solid #333945; color: #8b95a7; padding: 4px;")
        left.addWidget(self.lbl_plan_img, 1)

        thumbnails = QHBoxLayout()
        thumbnails.setSpacing(8)
        for floor_label in FLOOR_LABELS:
            floor_key = FLOOR_KEYS.get(floor_label, "Primer Piso")
            path = get_map_image_path(internal_map, floor_key)
            if not path or not os.path.isfile(path):
                continue
            thumb = QPushButton()
            thumb.setFixedSize(94, 62)
            thumb.setStyleSheet("QPushButton { background: #10141b; border: 1px solid #454b55; padding: 2px; } QPushButton:hover { border: 2px solid #a3e600; }")
            thumb_layout = QVBoxLayout(thumb)
            thumb_layout.setContentsMargins(2, 2, 2, 2)
            preview = QLabel()
            preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pix = QPixmap(path)
            if not pix.isNull():
                preview.setPixmap(pix.scaled(86, 54, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            thumb_layout.addWidget(preview)
            thumb.clicked.connect(lambda _checked=False, m=internal_map, fl=floor_label: self._update_map_floor_image(m, fl))
            self.floor_thumbnails[floor_label] = thumb
            thumbnails.addWidget(thumb)
        thumbnails.addStretch(1)
        left.addLayout(thumbnails)
        body.addLayout(left, 5)

        right = QHBoxLayout()
        right.setSpacing(18)
        description_text = MAP_DESCRIPTIONS.get(internal_map, "Mapa competitivo de Rainbow Six Siege.")
        if internal_map == "Calypso Casino":
            description_text = (
                "Ubicado en el centro de Las Vegas, Casino Calypso rinde homenaje al legado de Rainbow Six: Vegas. "
                "Este mapa, hecho para el apartado competitivo, incluye una jugabilidad unica, con elementos "
                "destructibles y puntos de referencia emblematicos del casino. Baja haciendo rapel desde la grua "
                "de la azotea, recaba informacion por los conductos de dron verticales y usa demoliciones hasta "
                "llegar a la camara del sotano."
            )
        description = label(description_text, color="#eceef1", size=13, wrap=True)
        description.setMinimumWidth(180)
        description.setMaximumWidth(360)
        right.addWidget(description, 3, Qt.AlignmentFlag.AlignTop)

        references = QFrame()
        references.setMinimumWidth(188)
        references.setMaximumWidth(220)
        references.setStyleSheet("QFrame { background: #78b800; border: 1px solid #a3e600; border-radius: 7px; color: #10150a; }")
        ref_layout = QVBoxLayout(references)
        ref_layout.setContentsMargins(10, 8, 10, 8)
        ref_layout.setSpacing(1)
        ref_layout.addWidget(label("REFERENCIAS", color="#10150a", size=15, bold=True))
        for icon, text in [(chr(0x25a7), "Paredes destructibles"), (chr(0x25a6), "Trampillas de techo"), (chr(0x25cf), "Camaras de seguridad"), (chr(0x2195), "Escaleras"), (chr(0x25a4), "Trampillas"), (chr(0x25c9), "Claraboya"), (chr(0x25c6), "Punto de aparicion"), ("A/B", "Objetivos")]:
            line = QHBoxLayout()
            marker = label(icon, color="#10150a", size=12, bold=True)
            marker.setFixedWidth(22)
            line.addWidget(marker)
            line.addWidget(label(text, color="#10150a", size=10, bold=True, wrap=True), 1)
            ref_layout.addLayout(line)
        ref_layout.addStretch(1)
        right.addWidget(references, 2, Qt.AlignmentFlag.AlignTop)
        body.addLayout(right, 5)
        self.map_view_layout.addLayout(body, 1)

        separator = QFrame()
        separator.setFixedHeight(2)
        separator.setStyleSheet("background: #78b800; border: none;")
        self.map_view_layout.addWidget(separator)
        title_row = QHBoxLayout()
        title_row.addStretch(1)
        title_row.addWidget(label(display_name.upper(), color=ORANGE, size=25, bold=True))
        self.map_view_layout.addLayout(title_row)
        self.map_detail_page.setMinimumHeight(480)
        self._update_map_floor_image(internal_map, "PRIMER PISO")
        self.maps_stack.setCurrentIndex(1)
        self._sync_global_scroll_document()

    def _resize_map_resource(self):
        if self.map_resource_pixmap is None or self.map_resource_label is None:
            return
        target_width = max(600, self.width() - 72)
        target_height = max(380, self.stack.height() - 16)
        self.map_resource_label.setPixmap(self.map_resource_pixmap.scaled(
            target_width, target_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))

    def _update_map_floor_image(self, internal_map: str, floor_label: str):
        if not hasattr(self, "floor_buttons") or not hasattr(self, "lbl_plan_img"):
            return
        self.current_info_map = internal_map
        self.current_floor_label = floor_label
        for name, button in self.floor_buttons.items():
            active = name == floor_label
            button.setStyleSheet(
                f"QPushButton {{ background: transparent; color: {'#a3e600' if active else 'white'}; "
                f"border: none; border-bottom: 2px solid {'#ff8a00' if active else 'transparent'}; "
                "padding: 5px 9px; font-size: 14px; font-weight: 800; }"
            )
        for name, button in getattr(self, "floor_thumbnails", {}).items():
            button.setStyleSheet(
                f"QPushButton {{ background: #10141b; border: 2px solid {'#ff8a00' if name == floor_label else '#454b55'}; padding: 1px; }}"
            )

        floor_key = FLOOR_KEYS.get(floor_label, "Primer Piso")
        path = get_map_image_path(internal_map, floor_key)
        if path and os.path.isfile(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self.lbl_plan_img.setPixmap(pixmap.scaled(
                    max(360, self.lbl_plan_img.width()), max(260, self.lbl_plan_img.height()),
                    Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation,
                ))
                self.lbl_plan_img.setText("")
                return
        self.lbl_plan_img.setPixmap(QPixmap())
        self.lbl_plan_img.setText(f"Plano no disponible\n{internal_map} - {floor_label}\n\nProba otro piso o agrega el archivo a assets/maps.")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("R6 Tactical Assistant Hub")
    app.setWindowIcon(QIcon(os.path.join(ASSETS_DIR, "icono app.png")))
    register_fonts()
    window = R6Launcher()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
