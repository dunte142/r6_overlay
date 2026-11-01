"""Hub táctico de escritorio para R6 Overlay.

Todas las rutas parten de este archivo, por lo que el proyecto puede moverse
completo de carpeta o ejecutarse desde un acceso directo de Windows.
"""
from __future__ import annotations

import os
import re
import sys

from PyQt6.QtCore import Qt, QTimer, QSize, QObject, QEvent
from PyQt6.QtGui import QPixmap, QPainter, QColor, QLinearGradient, QBrush, QIcon, QCursor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QGridLayout, QStackedWidget,
    QFrame, QMessageBox, QDialog, QSizePolicy, QSpacerItem, QInputDialog, QBoxLayout, QLayout, QStackedLayout,
    QTextBrowser,
)

from data.gadgets import OPERATOR_INFO
from data.map_calibration import ALL_MAPS, get_map_image_path
from ui.assets import register_fonts, OPERATOR_PORTRAITS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ASSETS_UI = os.path.join(ASSETS_DIR, "ui")
BADGES_DIR = os.path.join(ASSETS_UI, "badges")
RECURSOS_DIR = os.path.join(ASSETS_DIR, "recursos")
MAP_PHOTOS_DIR = os.path.join(RECURSOS_DIR, "mapas_hud", "MAPAS", "fotos")
MAP_REFERENCES_IMAGE = os.path.join(RECURSOS_DIR, "mapas_hud", "referencias.png")
NAV_HIGHLIGHT_IMAGE = os.path.join(RECURSOS_DIR, "resaltar.png")
SEARCH_ICON_IMAGE = os.path.join(ASSETS_DIR, "lupa.png")
SETTINGS_ICON_IMAGE = os.path.join(ASSETS_DIR, "tuerca.png")
INFO_BACKGROUND = os.path.join(RECURSOS_DIR, "TEXTURA FONDO APP.png")

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

MAP_PHOTO_PREFIXES = {
    "Bank": ("BANCO",), "Border": ("FRONTERA",), "Chalet": ("CHALET",),
    "Clubhouse": ("CLUB",), "Coastline": ("LITORAL",), "Consulado": ("CONSULADO",),
    "Emerald Plains": ("PRADERA ESMERALDA", "PRADERAS ESMERALDA"),
    "Favela": ("FAVELA",), "Fortress": ("FORTALEZA",), "Kafe Dostoyevsky": ("KAFE",),
    "Kanal": ("KANAL",), "Lair": ("GUARIDA",), "Nighthaven Labs": ("LABORATORIO",),
    "Oregon": ("OREGON",), "Outback": ("OUTBACK",), "Skyscraper": ("RASCACIELOS",),
    "Stadium Alpha": ("ESTADIO ALFA",), "Stadium Bravo": ("ESTADIO BRAVO", "ESATDIO BRAVO"),
    "Theme Park": ("PARQUE DE ATRACCIONES",), "Villa": ("VILLA",),
    "Calypso Casino": ("CASINO",), "Hereford Base": ("HEREFORD",), "House": ("CASA",),
    "Presidential Plane": ("AVION",), "Tower": ("TORRE",), "Yacht": ("YATE",),
}

MAP_PHOTO_COVERS = {
    "Bank": "BANCO.png", "Border": "FRONTERA.png", "Chalet": "CHALET.png",
    "Clubhouse": "CLUB.png", "Coastline": "LITORAL.png", "Consulado": "CONSULADO 1.png",
    "Emerald Plains": "PRADERA ESMERALDA.png", "Favela": "FAVELA 1.png",
    "Fortress": "FORTALEZA.png", "Kafe Dostoyevsky": "KAFE.png", "Kanal": "KANAL.png",
    "Lair": "GUARIDA.png", "Nighthaven Labs": "LABORATORIO.png", "Oregon": "OREGON.png",
    "Outback": "OUTBACK.png", "Skyscraper": "RASCACIELOS.png", "Stadium Alpha": "ESTADIO ALFA.png",
    "Stadium Bravo": "ESTADIO BRAVO.png", "Theme Park": "PARQUE DE ATRACCIONES.png",
    "Villa": "VILLA.png", "Calypso Casino": "CASINO CALYPSO.png", "Hereford Base": "HEREFORD.png",
    "House": "CASA.png", "Presidential Plane": "AVION PRESIDENCIAL.png",
    "Tower": "TORRE.png", "Yacht": "YATE.png",
}

MAP_DETAIL_PHOTOS = {
    "Bank": "BANCO 5.png", "Chalet": "CHALET 2.png", "Clubhouse": "CLUB 2.png",
    "Consulado": "CONSULADO 3.png", "Emerald Plains": "PRADERA ESMERALDA (2).png",
    "Favela": "FAVELA 3.png", "Fortress": "FORTALEZA 2.png", "Border": "FRONTERA 54.png",
    "Hereford Base": "hereford 3.png", "Kafe Dostoyevsky": "KAFE 3.png", "Kanal": "KANAL 2.png",
    "Nighthaven Labs": "LABORATORIO 2.png", "Coastline": "LITORAL.png", "Oregon": "OREGON 2.png",
    "Outback": "OUTBACK 4.png", "Theme Park": "PARQUE DE ATRACCIONES 4.png",
    "Skyscraper": "RASCACIELOS.png", "Tower": "TORRE 3.png", "Villa": "villa.png",
    "Yacht": "YATE.png", "House": "CASA 2.png", "Presidential Plane": "AVION PRESIDENCIAL 2.png",
    "Stadium Alpha": "ESTADIO ALFA.png", "Stadium Bravo": "ESATDIO BRAVO 2.png",
    "Calypso Casino": "CASINO 3.png",
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

# Los nombres impresos en cada PNG determinan la correspondencia con el operador.
DEFENDER_HOME_ICONS = {
    "Noor": 1493, "Denari": 1494, "Skopos": 1495, "Sentry": 1496,
    "Tubarao": 1497, "Fenrir": 1498, "Solis": 1499, "Azami": 1500,
    "Thorn": 1501, "Thunderbird": 1502, "Maestro": 1503, "Clash": 1504,
    "Kaid": 1505, "Mozzie": 1506, "Warden": 1507, "Goyo": 1508,
    "Wamai": 1509, "Oryx": 1510, "Melusi": 1511, "Aruni": 1512,
    "Alibi": 1513, "Vigil": 1514, "Ela": 1515, "Lesion": 1516,
    "Mira": 1572, "Echo": 1573, "Caveira": 1574, "Valkyrie": 1575,
    "Frost": 1576, "Mute": 1577, "Bandit": 1578, "Kapkan": 1579,
    "Tachanka": 1580, "Jager": 1581, "Rook": 1582, "Doc": 1583,
    "Pulse": 1584, "Castle": 1585, "Smoke": 1586,
}

DEFENDER_HOME_ORDER = [
    "Noor", "Denari", "Skopos", "Sentry", "Tubarao", "Fenrir", "Solis", "Azami",
    "Thorn", "Thunderbird", "Aruni", "Melusi", "Oryx", "Wamai", "Goyo", "Warden",
    "Mozzie", "Kaid", "Clash", "Maestro", "Alibi", "Vigil", "Ela", "Lesion",
    "Mira", "Echo", "Caveira", "Valkyrie", "Frost", "Mute", "Smoke", "Castle",
    "Pulse", "Doc", "Rook", "Jager", "Tachanka", "Kapkan", "Bandit",
]
ATTACKER_HOME_ORDER = [
    "Solid Snake", "Rauora", "Striker", "Deimos", "Ram", "Brava", "Sens", "Osa",
    "Flores", "Zero", "Ace", "Kali", "Nokk", "Nomad", "Maverick", "Lion",
    "Finka", "Dokkaebi", "Zofia", "Ying", "Jackal", "Hibana", "Capitao",
    "Blackbeard", "Buck", "Sledge", "Thatcher", "Ash", "Thermite", "Montagne",
    "Twitch", "Blitz", "IQ", "Fuze", "Glaz", "Grim", "Amaru", "Iana", "Gridlock",
]

MAP_DESCRIPTIONS = {
    "Calypso Casino": "Ubicado en el centro de Las Vegas, Casino Calypso rinde homenaje al legado de Rainbow Six: Vegas. Este mapa competitivo incluye elementos destructibles, rutas verticales para drones y una cámara en el sótano.",
    "Chalet": "Un tiroteo en un chalet de esquí en los Alpes franceses. En esta zona contrastan el ambiente cálido y acogedor de los interiores con el frío y la poca visibilidad del exterior.",
    "Bank": "Se ha llamado al equipo Rainbow para hacer una redada a un importante banco. El mapa propone un avance para los atacantes mientras se abren camino por áreas cada vez más fortificadas del edificio.",
    "Kafe Dostoyevsky": "Este lujoso café en el centro de Moscú es la cumbre de la ostentación y el glamour, un territorio de intervención natural para las fuerzas Spetsnaz. La destrucción de sus decoraciones clásicas será clave.",
    "Border": "El equipo Rainbow ayudará a las fuerzas locales a recuperar el control de la frontera. La combinación de edificios nuevos y antiguos, junto con caminos amplios, hace de este uno de los mapas más destructibles y abiertos.",
    "Hereford Base": "Aquí es donde los agentes del SAS aprenden su oficio, en un laberinto de blancos de madera, bolsas de arena, alambre de púas y otros obstáculos. Es uno de los ejemplos más arquetípicos del juego de asedio.",
    "Coastline": "El equipo Rainbow debe proteger la costa de Ibiza, España. Recorre las ruinas de las Baleares y sus bares para neutralizar el peligro. Prepárate para un flujo envolvente de combate y momentos de caos.",
    "Consulado": "Un lugar fortificado de alto riesgo y seguridad; este mapa ilustra un asalto a un consulado francés en Costa de Marfil.",
    "Clubhouse": "Este mapa ilustra un asalto a un club de una pandilla de motoristas. Con un bar completo, mesas de juego y muebles de piel, ofrece múltiples posibilidades tácticas en interiores y exteriores.",
    "Oregon": "Oregon representa un asalto a un complejo fortificado de paramilitares. Su estilo rústico y ecléctico cubre un terreno amplio que exige adaptar las tácticas para despejarlo y mantenerlo.",
    "Emerald Plains": "Conoce las onduladas montañas del norte de Irlanda en el club de campo y hacienda privada Praderas Esmeralda. Sus dos plantas contrastan una planta inferior moderna con el estilo clásico de una casa señorial.",
    "Favela": "El equipo Rainbow ha sido llamado para recuperar el control de la Favela. El mapa permite destruir fachadas exteriores y combina calles coloridas y angostas con puntos de observación elevados.",
    "Fortress": "Este enorme mapa diurno presenta una alcazaba de ladrillos de adobe y una arquitectura única del sur de Marruecos. La entrada principal recibe a los visitantes con dos torres y un arco monumental.",
    "Kanal": "Kanal tiene lugar en el área industrial de Hamburgo, Alemania. Sus edificios están conectados por puentes sobre los canales y ofrecen numerosos puntos elevados y rutas estratégicas.",
    "Lair": "La Guarida es un mapa competitivo de tres pisos con múltiples puntos de entrada y oportunidades de demolición. La verticalidad es clave: prepárate para flanqueos y ataques sorpresa.",
    "Nighthaven Labs": "Los laboratorios de Nighthaven presentan muchos puntos de entrada e incursión, donde es difícil mantener una posición por mucho tiempo. Vigila los flanqueos en el cuartel general y el laboratorio de I+D.",
    "Outback": "Ubicado en el corazón rojo de Australia, este mapa rinde homenaje a las estaciones de servicio polvorientas, los moteles de carreteras olvidadas y sus locales llenos de trabajadores y platos especiales.",
    "Skyscraper": "El equipo Rainbow debe neutralizar una guerra Yakuza en las calles de Nagoya, Japón. En la cima del Skyscraper explorarás la arquitectura japonesa de una peligrosa mansión, entre modernidad y tradición.",
    "Stadium Alpha": "MODO DE JUEGO: BOMBA. En el centro de la arena hay una casa de entrenamiento de combate compuesta por elementos de otros mapas. La versión rediseñada incorpora Coastline y Border, superficies destructibles señalizadas y cristales blindados.",
    "Stadium Bravo": "MODO DE JUEGO: BOMBA. En el centro de la arena hay una casa de entrenamiento de combate compuesta por elementos de otros mapas. La versión rediseñada incorpora Coastline y Border, superficies destructibles señalizadas y cristales blindados.",
    "Theme Park": "El equipo Rainbow debe asaltar un parque temático abandonado en las costas de Hong Kong. Prepárate para un perímetro complicado, colorido y ecléctico, lleno de enfrentamientos dinámicos.",
    "Villa": "El territorio pertenece a los Vinciguerra, una peligrosa familia criminal conocida por el contrabando. Sus miembros huyeron antes de la redada, dejando la villa desordenada e información vital por obtener.",
    "Close Quarter": "Entorno compacto de combate cercano; consulta los pisos disponibles y revisa el plano antes de elegir una ruta.",
    "House": "Este escenario familiar tiene lugar en una casa suburbana típica. Es un buen ejemplo de destrucción vertical y rejugabilidad, y muestra claramente el estilo clásico del juego de asedio.",
    "Presidential Plane": "El avión presidencial ofrece una experiencia de asedio exótica y única. Es claustrofóbico, tenso y restringido, con oportunidades de penetración y líneas de visión limitadas.",
    "Tower": "Escala la nevada torre Mok Myeok para liderar una misión de rescate en Seúl, Corea del Sur. La torre de comunicaciones y observación ofrece puntos verticales y nuevas tácticas multinivel.",
    "Yacht": "En la bahía de Baffin, un lujoso yate chocó contra un iceberg y sufrió una ruptura en el casco. El equipo Rainbow debe asegurar la embarcación varada, con un submarino no identificado cerca.",
}


MAP_DESCRIPTIONS.update({
    "Clubhouse": "Este mapa ilustra un asalto a un club de una pandilla de motoristas. Con un bar completo, mesas de juego y muebles de piel, este diseño mixto en interiores y exteriores ofrece una amplia gama de posibilidades tácticas, tanto para el atacante como para el defensor.",
    "Favela": "El equipo Rainbow ha sido llamado para llevar la paz y recuperar el control de la Favela. Este mapa permite destruir fachadas exteriores y combina calles coloridas y angostas con puntos de observación elevados, lo que lo convierte en el mapa más destructible hasta la fecha.",
    "Fortress": "Este enorme mapa diurno presenta una alcazaba de ladrillos de adobe y una arquitectura única del sur de Marruecos. La imponente entrada principal recibe a los visitantes con dos torres y la frase Kasbah Sehkra Mania escrita en el arco.",
    "Lair": "La Guarida es un mapa competitivo que, con sus tres pisos, múltiples puntos de entrada y oportunidades de demolición, hace de la verticalidad un punto clave. Prepárate para flanqueos en el Pasillo de la Armería o sorprende a tus enemigos infiltrándote en la sala R6.",
    "Nighthaven Labs": "Los Laboratorios de Nighthaven son un mapa competitivo con muchos puntos de entrada e incursión, donde es complicado mantener una posición por mucho tiempo. Prepárate para flanqueos en el cuartel general o sorprende a tus enemigos irrumpiendo en el laboratorio de I+D.",
    "Coastline": "El equipo Rainbow ha sido llamado para salvaguardar la costa de Ibiza, España. Recorre las ruinas de las Baleares y sus bares para neutralizar el peligro. Prepárate para un flujo envolvente de combate, aderezado con momentos de caos, mientras exploras un paraíso que acabó mal.",
    "Outback": "Ubicado en el corazón rojo de Australia, este mapa es un homenaje a las estaciones de servicio polvorientas y a los moteles de carreteras olvidadas, así como a sus sitios llenos de trabajadores locales y platillos especiales que no encontrarás en ningún otro lugar.",
    "Theme Park": "Se ha llamado al equipo Rainbow para hacer una redada en un parque temático abandonado en las costas de Hong Kong. Lidera una redada letal en este complicado perímetro. Prepárate para descubrir un mapa colorido y ecléctico, lleno de enfrentamientos dinámicos y de ritmo rápido.",
    "Emerald Plains": "Conoce las onduladas montañas del norte de Irlanda en el club de campo y hacienda privada Praderas Esmeralda. Las dos plantas contrastan una moderna planta inferior con el estilo clásico de una casa señorial. Este contraste enfatiza los puntos de referencia para la comunicación y la orientación.",
    "Tower": "Escala la nevada torre Mok Myeok para liderar una misión de rescate en Seúl, Corea del Sur. La moderna torre de comunicaciones y observación ofrece puntos verticales ventajosos, una vista aérea de la ciudad y nuevas tácticas multinivel.",
    "Villa": "El territorio pertenece a los Vinciguerra, una peligrosa familia criminal conocida por el contrabando. Ahora capturamos la villa en una instantánea: están quemando documentos y transportando sus bienes antes de la redada. Se enteraron de la operación Para Bellum y huyeron, dejando información vital por obtener.",
    "Stadium Alpha": "MODO DE JUEGO: BOMBA. En el centro de la arena hay una casa de entrenamiento de combate (kill house), compuesta por elementos de otros mapas. La versión rediseñada incorpora Coastline y Border. Sus superficies destructibles están señalizadas y los cristales blindados permiten observar al otro equipo de forma segura.",
    "Stadium Bravo": "MODO DE JUEGO: BOMBA. En el centro de la arena hay una casa de entrenamiento de combate (kill house), compuesta por elementos de otros mapas. La versión rediseñada incorpora Coastline y Border. Sus superficies destructibles están señalizadas y los cristales blindados permiten observar al otro equipo de forma segura.",
})

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
        if hasattr(self, "nav_group"):
            self.nav_group.setFixedWidth(max(440, (self.width() - 32) // 2))
        if hasattr(self, "stack"):
            QTimer.singleShot(0, self._sync_global_scroll_document)
        if (hasattr(self, "news_stack") and self.stack.currentIndex() == 0
                and self.news_stack.currentIndex() == 1):
            QTimer.singleShot(0, self._resize_first_news_detail)
        if (hasattr(self, "agents_stack") and self.stack.currentIndex() == 1
                and self.agents_stack.currentIndex() == 1):
            QTimer.singleShot(0, self._resize_operator_detail)
        if (hasattr(self, "maps_stack") and self.stack.currentIndex() == 2
                and self.maps_stack.currentIndex() == 1):
            if getattr(self, "current_map_photo", None):
                QTimer.singleShot(0, lambda: self._show_map_detail_image(self.current_map_photo, fill=True))
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

        nav_group = QWidget()
        nav_group.setFixedWidth(max(440, (self.width() - 32) // 2))
        self.nav_group = nav_group
        nav_group_layout = QVBoxLayout(nav_group)
        nav_group_layout.setContentsMargins(0, 0, 0, 0)
        nav_group_layout.setSpacing(0)
        tabs_row = QHBoxLayout()
        tabs_row.setContentsMargins(0, 0, 0, 0)
        tabs_row.setSpacing(0)

        self.btn_tab_noticias = QPushButton("NOTICIAS")
        self.btn_tab_agentes = QPushButton("AGENTES")
        self.btn_tab_mapas = QPushButton("MAPAS")
        self.nav_btns = [self.btn_tab_noticias, self.btn_tab_agentes, self.btn_tab_mapas]
        self.nav_indicators = []
        for index, button in enumerate(self.nav_btns):
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            tab_layout.setContentsMargins(0, 0, 0, 0)
            tab_layout.setSpacing(0)
            indicator = QLabel()
            indicator.setFixedSize(132, 9)
            indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
            indicator.setStyleSheet("background: transparent;")
            button.setFixedSize(132, 48)
            button.clicked.connect(lambda _checked=False, i=index: self._on_tab_click(i))
            tab_layout.addWidget(indicator, 0, Qt.AlignmentFlag.AlignHCenter)
            tab_layout.addWidget(button)
            tabs_row.addWidget(tab)
            self.nav_indicators.append(indicator)
        tabs_row.addStretch(1)
        search = QPushButton()
        search.setToolTip("Buscar en el catálogo")
        search.setFixedSize(44, 44)
        search.setIcon(QIcon(SEARCH_ICON_IMAGE))
        search.setIconSize(QSize(44, 36))
        search.setStyleSheet("QPushButton { background: transparent; border: none; padding: 0; }")
        search.clicked.connect(self._focus_current_search)
        tabs_row.addWidget(search)
        nav_group_layout.addLayout(tabs_row)

        underline = QFrame()
        underline.setFixedHeight(2)
        underline.setStyleSheet(f"background: {ORANGE}; border: none;")
        nav_group_layout.addWidget(underline)
        row.addWidget(nav_group)
        row.addStretch(1)

        shell_layout.addLayout(row)
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
        if index == 0 and hasattr(self, "news_stack"):
            self.news_stack.setCurrentIndex(0)
            self.news_detail_page.setMinimumHeight(0)
            self.news_detail_page.setMaximumHeight(16777215)
        elif index == 1 and hasattr(self, "agents_stack"):
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
            indicator = self.nav_indicators[i]
            if i == index:
                pixmap = QPixmap(NAV_HIGHLIGHT_IMAGE) if os.path.isfile(NAV_HIGHLIGHT_IMAGE) else QPixmap()
                indicator.setPixmap(pixmap.scaled(
                    132, 9, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation,
                ) if not pixmap.isNull() else QPixmap())
                button.setStyleSheet(f"QPushButton {{ background: transparent; border: none; color: #ffffff; font-size: 24px; font-weight: 900; padding: 2px 6px; border-radius: 0; }}")
            else:
                indicator.clear()
                button.setStyleSheet(f"QPushButton {{ background: transparent; border: none; color: {MUTED}; font-size: 24px; font-weight: 800; padding: 2px 6px; }} QPushButton:hover {{ color: {GREEN}; }}")

    def _init_landing_section(self):
        reference_width = max(900, self.width())
        self.news_stack = QStackedWidget()
        self.news_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        page = InfoBackground()
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
            tile = QPushButton() if index == 0 else QFrame()
            tile.setFixedHeight(tile_height)
            tile.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            if index == 0:
                tile.setCursor(Qt.CursorShape.PointingHandCursor)
            if index in (0, 1, 2, 3):
                tile.setStyleSheet(
                    "QPushButton { background: transparent; border: none; padding: 0; text-align: left; } "
                    "QPushButton:hover { background: rgba(255, 255, 255, 12); }"
                    if index == 0 else "QFrame { background: transparent; border: none; }"
                )
                tile_layout = QHBoxLayout(tile)
                tile_layout.setContentsMargins(0, 0, 0, 0)
                tile_layout.setSpacing(12)

                article_image = QLabel()
                article_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
                image_width = max(150, min(round(tile_height * 1.45), round(reference_width * 0.14)))
                image_height = max(100, tile_height - 16)
                article_image.setFixedSize(image_width, image_height)
                image_path = os.path.join(
                    RECURSOS_DIR, "noticias",
                    "-R6S-_Y11S3.2_Mid-Season_Designer-s_Notes_-_MIDSEASON_DESIGNER_NOTES_Y11S3_960x540.png"
                    if index == 0 else "Y11S3_PATCHNOTES_MIDSEASON_960x540.png"
                    if index == 1 else "R6S_DOKT7_Keyart_16_9_4K_Final.png"
                    if index == 2 else "R6S_Y11S3_Wasteland_Drops_BadgeAndSkin_960.png",
                )
                pixmap = QPixmap(image_path) if os.path.isfile(image_path) else QPixmap()
                if not pixmap.isNull():
                    article_image.setPixmap(pixmap.scaled(
                        image_width, image_height,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    ))
                article_image.setStyleSheet("background: transparent;")
                article_image.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
                tile_layout.addWidget(article_image, 0, Qt.AlignmentFlag.AlignVCenter)

                article_copy = QVBoxLayout()
                article_copy.setContentsMargins(0, 0, 0, 0)
                article_copy.setSpacing(4)
                if index == 0:
                    date_text = "15/10/2026"
                    title_text = "NOTAS SOBRE EL DISEÑO: ACTUALIZACIÓN A MITAD DE TEMPORADA DEL Y11S3"
                    summary_text = "En la última edición de nuestras Notas sobre el diseño vamos a adentrarnos en los cambios de equilibrio que presentamos en la actualización a mitad de temporada del Y11S3."
                elif index == 1:
                    date_text = "13/10/2026"
                    title_text = "Y11S3.2 PATCH NOTES"
                    summary_text = "Ve los próximos cambios del Rainbow Six Siege con la llegada de la versión Y11S3.2."
                elif index == 2:
                    date_text = "14/10/2026"
                    title_text = "¡DOKTOR'S CURSE VUELVE HASTA EL 2 DE NOVIEMBRE!"
                    summary_text = "Doktor's Curse vuelve del 15 de octubre al 2 de noviembre. Elige un bando en el emblemático modo del escondite y enfréntate al caos que acecha dentro del laboratorio perverso del Doktor."
                else:
                    date_text = "23/9/2026"
                    title_text = "¡TWITCH DROP E INSIGNIA NUEVOS, DISPONIBLES DURANTE EL EVENTO WASTELAND CIRCUIT!"
                    summary_text = "¡Preparaos, pilotos de drones! Desbloquead estas recompensas exclusivas en Twitch para conmemorar el primer evento de carreras de drones de Siege. Aquí está toda la información necesaria para reclamar el botín antes de que la polvareda se asiente."
                date_label = label(date_text, color="#FFFFFF", size=11)
                title_label = label(title_text, color="#B8E833", size=17, bold=True, wrap=True)
                summary_label = label(summary_text, color="#FFFFFF", size=13, wrap=True)
                for text_label in (date_label, title_label, summary_label):
                    text_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
                article_copy.addWidget(date_label)
                article_copy.addWidget(title_label)
                article_copy.addWidget(summary_label)
                article_copy.addStretch(1)
                tile_layout.addLayout(article_copy, 1)
                if index == 0:
                    tile.clicked.connect(self._show_first_news_detail)
            else:
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
        self.news_stack.addWidget(page)

        self.news_detail_page = InfoBackground()
        self.news_detail_page.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        detail_layout = QHBoxLayout(self.news_detail_page)
        detail_layout.setContentsMargins(20, 16, 20, 16)
        detail_layout.setSpacing(28)
        self.news_detail_image = QLabel()
        self.news_detail_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.news_detail_image.setStyleSheet("background: transparent;")
        self.news_detail_image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.news_detail_text = QTextBrowser()
        self.news_detail_text.setOpenExternalLinks(False)
        self.news_detail_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.news_detail_text.setStyleSheet(
            "QTextBrowser { background: transparent; border: none; color: #FFFFFF; "
            "font-family: 'Barlow Condensed', 'Segoe UI', sans-serif; font-size: 18px; }"
        )
        detail_layout.addWidget(self.news_detail_image, 4)
        detail_layout.addWidget(self.news_detail_text, 6)
        self.news_stack.addWidget(self.news_detail_page)
        self.stack.addWidget(self.news_stack)

    def _show_first_news_detail(self):
        self.hero_banner.hide()
        self.compact_header.show()
        self.top_panel_host.layout().activate()
        self.root_layout.activate()
        self._resize_first_news_detail()
        self.news_detail_text.setHtml("""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
body { color: #FFFFFF; font-family: 'Barlow Condensed', 'Segoe UI', sans-serif; font-size: 18px; }
h1 { color: #FF8707; font-size: 30px; font-weight: 700; margin: 0 0 18px 0; }
h2 { color: #FFFFFF; font-size: 22px; font-weight: 500; margin: 18px 0 8px 0; }
h3 { color: #FFFFFF; font-size: 21px; font-weight: 600; margin: 14px 0 3px 0; }
p { color: #FFFFFF; font-size: 18px; margin: 0 0 12px 0; }
ul { color: #FFFFFF; font-size: 18px; margin: 2px 0 12px 0; padding-left: 24px; }
li { margin-bottom: 5px; }
</style></head><body>
<h1>AJUSTES DE EQUILIBRIO DE AGENTES</h1>
<h2>SEGUIMIENTO DEL LANZAMIENTO</h2>
<h3>NOOR</h3>
<p>La habilidad de Noor se quedaba corta en distintos aspectos, así que va a recibir algunos cambios de seguimiento para aumentar sus capacidades de contrarrestar con escudos y su supervivencia. El disparalanzas Horus recibirá varias mejoras para que su habilidad sea más proactiva y dura contra los agentes con escudos antibalas cuando cometen errores de posicionamiento, pero también más gratificante para el riesgo que asume Noor mientras lleva equipado el lanzador.</p>
<h3>DISPARALANZAS HORUS</h3>
<ul>
<li>Se reduce el tiempo de perforación de escudos antibalas, superficies débiles y superficies sólidas (superficies no destruibles) a 1,5 s (antes 2 s).</li>
<li>La resistencia de rotura de guardia de los impactos de proyectil contra los agentes con escudos antibalas aumenta al 100 % (antes 30 %).</li>
<li>Se reduce el tiempo de las animaciones rápidas al equipar el disparalanzas Horus a 0,4 s (antes 0,9 s).</li>
<li>Aumenta el daño de impacto de la lanza Horus contra los agentes a 80 (antes 50).</li>
<li>Se actualiza la caja de golpe de la lanza Horus para mejorar la precisión y la estabilidad.</li>
<li>La lanza Horus inflige daño a los agentes con escudo antibalas que están haciendo la animación para quitárselo.</li>
</ul>
<h2>CAMBIOS IMPORTANTES</h2>
<h3>TACHANKA</h3>
<p>El lanzador Shumikha de Tachanka depende de los proyectiles que rebotan para soltar fuego. Aunque esto le permite ejercer presión sin exponerse al fuego enemigo, llega a ser difícil de controlar en las situaciones que requieren precisión. Además, el retraso que provoca la mecánica de rebote reduce la capacidad de respuesta, algo elemental en los enfrentamientos rápidos donde las diferencias más pequeñas de tiempos determinan el resultado de la ronda.</p>
<p>Por tanto, queremos reducir la habilidad necesaria de uso eficaz del dispositivo para así mejorar la utilidad y la capacidad de respuesta del lanzador Shumikha. Al mismo tiempo, se ofrecerá a los jugadores mayor control y adaptabilidad en función de la situación.</p>
<p>Al introducir un modo que se activa con los impactos, Tachanka responderá con mayor eficacia en los momentos precisos o en los que el tiempo es un factor importante. Esto mejorará la fiabilidad cuando se atacan posiciones concretas o se reacciona al movimiento rival. Del mismo modo, conservar el rebote preserva su capacidad de establecer un bloqueo a capas y un control del espacio de forma indirecta. La elección entre los 2 modos permite una mejor adaptabilidad y permite que los jugadores elijan el método más apropiado en función de la situación.</p>
<h3>LANZADOR SHUMIKHA</h3>
<ul><li>Se ha añadido un modo de disparo para activar las granadas incendiarias tras impactar.</li></ul>
<h3>SOLID SNAKE</h3>
<p>El radar de Solid Snake permite muchas maniobras en diferentes situaciones, por lo que puede ejercer presión sin correr demasiados riesgos.</p>
<p>Queremos reducir ligeramente las capacidades generales de Snake para fomentar un uso deliberado y una priorización más clara de los objetivos.</p>
<h3>RADAR SOLITON MK. III</h3>
<ul><li>Cargas del modo de precisión: se reducen a 3 (antes 4).</li></ul>
<h3>VALKYRIE</h3>
<p>Queremos mejorar la capacidad de Valkyrie de instalar y aprovechar sus cámaras con mayor eficacia para mejorar su capacidad de crear líneas de visión sin aumentar su potencia en general.</p>
<p>Se ha añadido el arma Glaive-12 para que pueda crear líneas de visión más rápido y desde más lejos.</p>
<h3>EQUIPAMIENTO</h3>
<ul><li>Armas secundarias: se ha añadido el arma Glaive-12.</li></ul>
<h2>CAMBIOS DE PERFECCIONAMIENTO</h2>
<p>Se trata de pequeños ajustes que no buscan alterar la potencia en general o la versatilidad de los agentes. En su lugar, se centran en pulir detalles de la jugabilidad, mejorar la homogeneidad y reforzar la optimización de la experiencia sin cambiar el metajuego. Buscamos mantener un flujo constante de estas mejoras paralelamente a las actualizaciones importantes para que el juego evolucione y mejore a un ritmo constante.</p>
<h3>CAPITÃO</h3>
<p>Queremos mejorar la capacidad de respuesta y la fiabilidad de los proyectiles de fuego de Capitão, de tal forma que nos aseguremos de que ejerzan presión más rápido una vez instalados.</p>
<h3>PROYECTIL DE FUEGO</h3>
<ul><li>Expansión: se reduce el retraso entre expansiones a 0,9 s (antes 1).</li></ul>
<h3>CLASH</h3>
<p>El táser solo funciona a potencia máxima cuando los enemigos se acercan a Clash, mientras que su impacto continúa siendo bastante bajo cuando huyen. Esta distinción hace hincapié en el contraataque direccional y fomenta que los jugadores adapten su posicionamiento durante los enfrentamientos. Al aumentar la ralentización cuando los enemigos se van, fortalecemos la capacidad de Clash de mantener la presión y controlar el espacio cuando los enemigos intentan retirarse.</p>
<h3>TÁSER</h3>
<ul><li>Ralentización: aumenta la fuerza cuando los enemigos se alejan al 10 % (antes 5 %).</li></ul>
<h3>OSA</h3>
<p>Este cambio permite que Osa coloque su escudo en una mayor variedad de situaciones, lo que mejora la flexibilidad y reduce la fricción al preparar las posiciones.</p>
<h3>ESCUDO TRANSPARENTE TALON-8</h3>
<ul><li>Se han reducido las restricciones de colocación.</li></ul>
<h3>FUEGO</h3>
<p>Queremos aumentar la letalidad y afianzar la amenaza y la nitidez de los peligros de fuego en el juego. De esta forma, colocarse o cruzar estas zonas acarreará consecuencias más inmediatas.</p>
<ul><li>Daño: aumenta a 14 PS (antes 12).</li></ul>
<h3>AGENTES IMPLICADOS</h3>
<ul><li>Capitão</li><li>Dokkaebi</li><li>Goyo</li><li>Noor</li><li>Tachanka</li><li>Gasoductos</li></ul>
<h3>ALAMBRE DE ESPINO</h3>
<p>Este cambio consolida que el alambre de espino contrarresta bien a los BU-GI, lo que ofrece a los defensores una herramienta adicional para detener su avance. Los defensores se ven recompensados por colocar bien el dispositivo, mientras que los jugadores de Ram se ven motivados a preparar los caminos de la instalación con mayor cuidado y a responder a las configuraciones defensivas.</p>
<ul><li>Los BU-GI se quedan enredados en el alambre de espino, lo que provoca que se detengan y se autodestruyan.</li></ul>
</body></html>""")
        self.news_detail_text.verticalScrollBar().setValue(0)
        self.news_stack.setCurrentIndex(1)
        self._sync_global_scroll_document()
        self.global_scroll.verticalScrollBar().setValue(0)

    def _resize_first_news_detail(self):
        if not hasattr(self, "news_detail_page"):
            return
        nav_height = self.root_layout.itemAt(1).sizeHint().height() if self.root_layout.count() > 1 else 60
        viewport_height = self.global_scroll.viewport().height()
        detail_height = max(420, viewport_height - self.compact_header.height() - nav_height - 42)
        self.news_detail_page.setFixedHeight(detail_height)
        image_path = os.path.join(
            RECURSOS_DIR, "noticias",
            "-R6S-_Y11S3.2_Mid-Season_Designer-s_Notes_-_MIDSEASON_DESIGNER_NOTES_Y11S3_960x540.png",
        )
        self.news_detail_pixmap = QPixmap(image_path) if os.path.isfile(image_path) else QPixmap()
        if not self.news_detail_pixmap.isNull():
            image_width = max(220, round((self.width() - 96) * 0.40))
            image_height = max(240, detail_height - 32)
            # La referencia llena toda la columna y recorta los laterales del
            # arte; mantener la proporción completa lo dejaba centrado y bajo.
            cover = self.news_detail_pixmap.scaled(
                image_width, image_height,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            crop_x = max(0, (cover.width() - image_width) // 2)
            crop_y = max(0, (cover.height() - image_height) // 2)
            self.news_detail_image.setPixmap(cover.copy(crop_x, crop_y, image_width, image_height))
        if self.news_stack.currentIndex() == 1:
            QTimer.singleShot(0, self._sync_global_scroll_document)

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
            group = DEFENDER_HOME_ICONS.get(name)
            path = os.path.join(RECURSOS_DIR, "defensores_home", f"Group {group}.png") if group else None
            pixmap = QPixmap(path) if path and os.path.isfile(path) else QPixmap()
            if not pixmap.isNull():
                target = QSize(round(size * 0.82), size)
                pixmap = pixmap.scaled(target, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                image = QLabel()
                image.setPixmap(pixmap)
                image.setAlignment(Qt.AlignmentFlag.AlignCenter)
                image.setFixedSize(target.width() + 4, target.height() + 4)
                return image
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
        order = DEFENDER_HOME_ORDER if is_defender else ATTACKER_HOME_ORDER
        operators = [name for name in order if name in OPERATOR_INFO and (not term or term in name.casefold())]
        columns = max(2, min(10, (self.width() - 70) // 136))
        for idx, name in enumerate(operators):
            info = OPERATOR_INFO[name]
            button = QPushButton()
            button.setFixedSize(126, 154)
            hover_color = "#76B4FF" if is_defender else "#ff5058"
            button.setStyleSheet(f"QPushButton {{ background: transparent; border: 1px solid transparent; padding: 0; }} QPushButton:hover {{ background: transparent; border: 1px solid {hover_color}; }}")
            cl = QVBoxLayout(button)
            cl.setContentsMargins(1, 1, 1, 1)
            cl.setSpacing(0)
            cl.addWidget(self._operator_icon(name, 146), alignment=Qt.AlignmentFlag.AlignHCenter)
            button.clicked.connect(lambda _checked=False, n=name, d=info, defender=is_defender: self._display_agent_details(n, d, defender))
            self.agent_grid_layout.addWidget(button, idx // columns, idx % columns)
        rows = (len(operators) + columns - 1) // columns
        self.agent_grid_layout.setRowStretch(rows, 0)
        card_height = 154
        grid_spacing = 10
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
            shade = QWidget()
            shade.setStyleSheet("background: rgba(5, 8, 12, 72);")
            shade.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            tile_layout.addWidget(shade)
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
        self.map_view_layout.setContentsMargins(0, 12, 0, 0)
        self.map_view_layout.setSpacing(10)
        self.map_detail_page.setMinimumHeight(480)
        self.maps_stack.addWidget(self.map_detail_page)
        self.stack.addWidget(self.maps_stack)

    def _map_cover_pixmap(self, internal_name: str, size: QSize) -> QPixmap:
        photo_paths = self._map_photo_paths(internal_name)
        cover_name = MAP_PHOTO_COVERS.get(internal_name)
        cover_path = next(
            (path for path in photo_paths if os.path.basename(path).casefold() == (cover_name or "").casefold()),
            photo_paths[0] if photo_paths else None,
        )
        source = QPixmap(cover_path) if cover_path else QPixmap()
        if source.isNull():
            source = QPixmap()
        if source.isNull():
            preview_path = self._find_map_preview(internal_name)
            source = QPixmap(preview_path) if preview_path else QPixmap()
        if source.isNull():
            return QPixmap()
        scaled = source.scaled(size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        x = max(0, (scaled.width() - size.width()) // 2)
        y = max(0, (scaled.height() - size.height()) // 2)
        return scaled.copy(x, y, min(size.width(), scaled.width()), min(size.height(), scaled.height()))

    def _map_photo_paths(self, internal_name: str) -> list[str]:
        prefixes = MAP_PHOTO_PREFIXES.get(internal_name, ())
        if not prefixes or not os.path.isdir(MAP_PHOTOS_DIR):
            return []
        normalized_prefixes = tuple("".join(ch for ch in prefix.casefold() if ch.isalnum()) for prefix in prefixes)
        matches = []
        for filename in os.listdir(MAP_PHOTOS_DIR):
            if not filename.casefold().endswith(".png"):
                continue
            stem = os.path.splitext(filename)[0]
            normalized_stem = "".join(ch for ch in stem.casefold() if ch.isalnum())
            if any(normalized_stem.startswith(prefix) for prefix in normalized_prefixes):
                matches.append(os.path.join(MAP_PHOTOS_DIR, filename))

        def photo_order(path: str):
            stem = os.path.splitext(os.path.basename(path))[0]
            normalized_stem = "".join(ch for ch in stem.casefold() if ch.isalnum())
            is_base = normalized_stem in normalized_prefixes
            number = re.search(r"(\d+)(?:\D*)$", stem)
            return (0 if is_base else 1, int(number.group(1)) if number else 999, stem.casefold())

        return sorted(matches, key=photo_order)

    def _map_photo_for_detail(self, internal_map: str, photo_paths: list[str]) -> str | None:
        preferred = MAP_DETAIL_PHOTOS.get(internal_map) or MAP_PHOTO_COVERS.get(internal_map)
        if preferred:
            for path in photo_paths:
                if os.path.basename(path).casefold() == preferred.casefold():
                    return path
        return photo_paths[0] if photo_paths else None

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
        self.map_photo_paths = self._map_photo_paths(internal_map)
        self.current_map_photo = self._map_photo_for_detail(internal_map, self.map_photo_paths)
        self.floor_buttons: dict[str, QPushButton] = {}
        self.floor_thumbnails: dict[str, QPushButton] = {}

        header = QHBoxLayout()
        header.addStretch(1)
        for floor_label in FLOOR_LABELS:
            button = QPushButton(FLOOR_KEYS.get(floor_label, floor_label).upper())
            button.setFlat(True)
            button.setStyleSheet("QPushButton { background: transparent; color: white; border: none; border-bottom: 2px solid transparent; padding: 7px 15px; font-size: 27px; font-weight: 700; } QPushButton:hover { color: #a3e600; }")
            button.clicked.connect(lambda _checked=False, m=internal_map, fl=floor_label: self._update_map_floor_image(m, fl))
            self.floor_buttons[floor_label] = button
            header.addWidget(button)
        self.map_view_layout.addLayout(header)

        body = QHBoxLayout()
        body.setSpacing(10)
        left = QVBoxLayout()
        left.setSpacing(8)
        self.lbl_plan_img = QLabel("Plano no disponible")
        self.lbl_plan_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_plan_img.setMinimumSize(500, 350)
        self.lbl_plan_img.setMaximumSize(740, 510)
        self.lbl_plan_img.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.lbl_plan_img.setStyleSheet("background: rgba(8, 10, 14, 210); border: 1px solid #333945; color: #8b95a7; padding: 4px;")
        left.addWidget(self.lbl_plan_img, 1)

        self.map_gallery_layout = QHBoxLayout()
        self.map_gallery_layout.setSpacing(10)
        if self.map_photo_paths:
            self._refresh_map_photo_thumbnails()
        else:
            for floor_label in FLOOR_LABELS:
                floor_key = FLOOR_KEYS.get(floor_label, "Primer Piso")
                path = get_map_image_path(internal_map, floor_key)
                if not path or not os.path.isfile(path):
                    continue
                thumb = QPushButton()
                thumb.setFixedSize(138, 80)
                thumb.setStyleSheet("QPushButton { background: #10141b; border: 1px solid #454b55; padding: 2px; } QPushButton:hover { border: 2px solid #a3e600; }")
                thumb_layout = QVBoxLayout(thumb)
                thumb_layout.setContentsMargins(2, 2, 2, 2)
                preview = QLabel()
                preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
                pix = QPixmap(path)
                if not pix.isNull():
                    preview.setPixmap(pix.scaled(130, 72, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                thumb_layout.addWidget(preview)
                thumb.clicked.connect(lambda _checked=False, m=internal_map, fl=floor_label: self._update_map_floor_image(m, fl))
                self.floor_thumbnails[floor_label] = thumb
                self.map_gallery_layout.addWidget(thumb)
            self.map_gallery_layout.addStretch(1)
        left.addLayout(self.map_gallery_layout)
        body.addLayout(left, 4)

        right = QHBoxLayout()
        right.setSpacing(8)
        description_text = MAP_DESCRIPTIONS.get(internal_map, "Mapa competitivo de Rainbow Six Siege.")
        if internal_map == "Calypso Casino":
            description_text = (
                "Ubicado en el centro de Las Vegas, Casino Calypso rinde homenaje al legado de Rainbow Six: Vegas. "
                "Este mapa, hecho para el apartado competitivo, incluye una jugabilidad unica, con elementos "
                "destructibles y puntos de referencia emblematicos del casino. Baja haciendo rapel desde la grua "
                "de la azotea, recaba informacion por los conductos de dron verticales y usa demoliciones hasta "
                "llegar a la camara del sotano."
            )
        description = label(description_text, color="#eceef1", size=27, wrap=True)
        description.setMinimumWidth(340)
        description.setMaximumWidth(500)
        right.addWidget(description, 3, Qt.AlignmentFlag.AlignTop)

        reference_art = QPixmap(MAP_REFERENCES_IMAGE) if os.path.isfile(MAP_REFERENCES_IMAGE) else QPixmap()
        references = QLabel()
        references.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if not reference_art.isNull():
            references.setPixmap(reference_art.scaled(
                300, 392, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation,
            ))
        references.setFixedSize(300, 392)
        right.addWidget(references, 2, Qt.AlignmentFlag.AlignTop)
        body.addLayout(right, 5)
        self.map_view_layout.addLayout(body, 1)

        separator = QFrame()
        separator.setFixedHeight(2)
        separator.setStyleSheet("background: #78b800; border: none;")
        self.map_view_layout.addWidget(separator)
        title_row = QHBoxLayout()
        title_row.addStretch(1)
        title_row.addWidget(label(display_name.upper(), color=ORANGE, size=46, bold=True))
        self.map_view_layout.addLayout(title_row)
        self.map_detail_page.setMinimumHeight(660)
        self.current_floor_label = "PRIMER PISO"
        self._sync_map_floor_buttons(self.current_floor_label)
        if self.current_map_photo:
            self._show_map_detail_image(self.current_map_photo, fill=True)
        else:
            self._update_map_floor_image(internal_map, self.current_floor_label)
        self.maps_stack.setCurrentIndex(1)
        self._sync_global_scroll_document()
        if self.current_map_photo:
            QTimer.singleShot(0, lambda p=self.current_map_photo: self._show_map_detail_image(p, fill=True))
        else:
            QTimer.singleShot(0, lambda m=internal_map, f=self.current_floor_label: self._update_map_floor_image(m, f))

    def _show_map_detail_image(self, path: str, *, fill: bool = False):
        if not hasattr(self, "lbl_plan_img") or not path:
            return
        pixmap = QPixmap(path)
        if pixmap.isNull():
            return
        width = max(360, self.lbl_plan_img.width() - 10)
        height = max(260, self.lbl_plan_img.height() - 10)
        mode = (Qt.AspectRatioMode.KeepAspectRatioByExpanding if fill
                else Qt.AspectRatioMode.KeepAspectRatio)
        pixmap = pixmap.scaled(width, height, mode, Qt.TransformationMode.SmoothTransformation)
        if fill:
            x = max(0, (pixmap.width() - width) // 2)
            y = max(0, (pixmap.height() - height) // 2)
            pixmap = pixmap.copy(x, y, width, height)
        self.lbl_plan_img.setPixmap(pixmap)
        self.lbl_plan_img.setText("")

    def _show_map_photo(self, path: str):
        self.current_map_photo = path
        self._show_map_detail_image(path, fill=True)
        self._refresh_map_photo_thumbnails()

    def _refresh_map_photo_thumbnails(self):
        if not hasattr(self, "map_gallery_layout"):
            return
        clear_layout(self.map_gallery_layout)
        for path in self.map_photo_paths:
            if path == self.current_map_photo:
                continue
            thumb = QPushButton()
            thumb.setFixedSize(138, 80)
            thumb.setStyleSheet(
                f"QPushButton {{ background: #10141b; border: 1px solid {BORDER}; padding: 2px; }} "
                f"QPushButton:hover {{ border: 2px solid {ORANGE}; }}"
            )
            thumb_layout = QVBoxLayout(thumb)
            thumb_layout.setContentsMargins(2, 2, 2, 2)
            preview = QLabel()
            preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                preview.setPixmap(pixmap.scaled(
                    130, 72, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation,
                ))
            preview.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            thumb_layout.addWidget(preview)
            thumb.clicked.connect(lambda _checked=False, p=path: self._show_map_photo(p))
            self.map_gallery_layout.addWidget(thumb)
        self.map_gallery_layout.addStretch(1)

    def _sync_map_floor_buttons(self, floor_label: str):
        for name, button in getattr(self, "floor_buttons", {}).items():
            active = name == floor_label
            button.setStyleSheet(
                f"QPushButton {{ background: transparent; color: {'#a3e600' if active else 'white'}; "
                f"border: none; border-bottom: 2px solid {'#ff8a00' if active else 'transparent'}; "
                "padding: 7px 15px; font-size: 27px; font-weight: 800; }"
            )

    def _update_map_floor_image(self, internal_map: str, floor_label: str):
        if not hasattr(self, "floor_buttons") or not hasattr(self, "lbl_plan_img"):
            return
        self.current_info_map = internal_map
        self.current_floor_label = floor_label
        self.current_map_photo = None
        if self.map_photo_paths:
            self._refresh_map_photo_thumbnails()
        self._sync_map_floor_buttons(floor_label)
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
