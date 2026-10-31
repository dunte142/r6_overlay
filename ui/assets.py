"""
Rutas y constantes de los assets de diseño (íconos + tipografía Barlow
Condensed) provistos para el proyecto. Centralizado acá para no repetir
rutas por todo `overlay.py`.
"""

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_ROOT = os.path.join(PROJECT_ROOT, "assets")
FONTS_DIR = os.path.join(ASSETS_ROOT, "fonts")
UI_DIR = os.path.join(ASSETS_ROOT, "ui")
BADGES_DIR = os.path.join(UI_DIR, "badges")
MAPS_DIR = os.path.join(ASSETS_ROOT, "maps")

FONT_FILES = [
    "BarlowCondensed-Regular.ttf",
    "BarlowCondensed-Medium.ttf",
    "BarlowCondensed-SemiBold.ttf",
    "BarlowCondensed-Bold.ttf",
    "BarlowCondensed-ExtraBold.ttf",
    "BarlowCondensed-Black.ttf",
    "BarlowCondensed-Italic.ttf",
]

FONT_FAMILY = "Barlow Condensed"

# --- Íconos / paneles ya armados (PNG) ---
ICON = {
    "prep_header": os.path.join(UI_DIR, "Group 6.png"),          # "Fase de preparación / Coloca tus habilidades..."
    "gadget_card_example": os.path.join(UI_DIR, "Group 30.png"),  # tarjeta de gadget (ejemplo: Mute)
    "camera_legend": os.path.join(UI_DIR, "Group 68.png"),        # panel "REFERENCIAS" completo
    "detected_notice": os.path.join(UI_DIR, "Group 67.png"),      # notificación "Detectado" (check verde)
    "unknown_operator": os.path.join(UI_DIR, "Group 69.png"),     # tarjeta "?" para operador no identificado
    "match_button": os.path.join(UI_DIR, "Group 61.png"),         # control visual de partida actual
    "sound_button": os.path.join(UI_DIR, "Group 58.png"),         # control visual de sonido
    "settings_button": os.path.join(UI_DIR, "Group 60.png"),      # ajustes
    "armor_generic": os.path.join(UI_DIR, "armadura (1) 1.png"),
    "floor_sotano": os.path.join(UI_DIR, "SOTANO.png"),
    "floor_primer_piso": os.path.join(UI_DIR, "PRIMER PISO.png"),
    "floor_segundo_piso": os.path.join(UI_DIR, "SEGUNDO PISO.png"),
    "floor_tejado": os.path.join(UI_DIR, "TEJADO.png"),
    "label_mi_equipo_defensores": os.path.join(UI_DIR, "MI EQUIPO Defensores.png"),
    "label_mi_equipo_atacantes": os.path.join(UI_DIR, "MI EQUIPO Atacantes.png"),
    "label_equipo_rival_defensores": os.path.join(UI_DIR, "EQUIPO RIVAL Defensores.png"),
    "label_equipo_rival_atacantes": os.path.join(UI_DIR, "EQUIPO RIVAL Atacantes.png"),
    "tab_camaras": os.path.join(UI_DIR, "Group 59.png"),
    "tab_marcador": os.path.join(UI_DIR, "Group 58.png"),
    "tab_volver": os.path.join(UI_DIR, "Group 57.png"),
}

# Composiciones transparentes por operador (retrato + gadget + consejo).
# Los nombres de archivo son exportaciones del diseño original; centralizarlos
# acá permite que el overlay sea portable y evita adivinar rutas durante el render.
OPERATOR_PORTRAITS = {
    # Defensores
    "Bandit": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 983.png"),
    "Noor": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1323.png"),
    "Denari": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1324.png"),
    "Skopos": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1325.png"),
    "Sentry": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1326.png"),
    "Tubarao": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1327.png"),
    "Fenrir": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1328.png"),
    "Solis": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1329.png"),
    "Azami": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1330.png"),
    "Warden": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1331.png"),
    "Goyo": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1332.png"),
    "Wamai": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1333.png"),
    "Oryx": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1334.png"),
    "Melusi": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1335.png"),
    "Aruni": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1336.png"),
    "Thunderbird": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1337.png"),
    "Thorn": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1338.png"),
    "Mozzie": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1339.png"),
    "Kaid": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1340.png"),
    "Clash": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1341.png"),
    "Maestro": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1342.png"),
    "Alibi": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1343.png"),
    "Vigil": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1344.png"),
    "Ela": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1345.png"),
    "Lesion": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1346.png"),
    "Smoke": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1347.png"),
    "Mute": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1348.png"),
    "Frost": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1349.png"),
    "Valkyrie": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1350.png"),
    "Caveira": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1351.png"),
    "Echo": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1352.png"),
    "Mira": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1353.png"),
    "Castle": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1354.png"),
    "Pulse": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1355.png"),
    "Doc": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1356.png"),
    "Rook": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1357.png"),
    "Jager": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1358.png"),
    "Tachanka": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1359.png"),
    "Kapkan": os.path.join(UI_DIR, "operator_portraits", "defenders", "Group 1360.png"),
    # Atacantes
    "Nokk": os.path.join(UI_DIR, "operator_portraits", "attackers", "Frame 2.png"),
    "Kali": os.path.join(UI_DIR, "operator_portraits", "attackers", "Frame 3.png"),
    "Grim": os.path.join(UI_DIR, "operator_portraits", "attackers", "Frame 4.png"),
    "Solid Snake": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1361.png"),
    "Rauora": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1362.png"),
    "Striker": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1363.png"),
    "Deimos": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1364.png"),
    "Ram": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1365.png"),
    "Brava": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1366.png"),
    "Sens": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1367.png"),
    "Osa": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1368.png"),
    "Lion": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1369.png"),
    "Maverick": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1370.png"),
    "Nomad": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1371.png"),
    "Ace": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1372.png"),
    "Zero": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1373.png"),
    "Flores": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1374.png"),
    "Finka": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1375.png"),
    "Dokkaebi": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1376.png"),
    "Zofia": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1377.png"),
    "Ying": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1378.png"),
    "Jackal": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1379.png"),
    "Hibana": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1380.png"),
    "Capitao": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1381.png"),
    "Blackbeard": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1382.png"),
    "Twitch": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1383.png"),
    "Montagne": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1384.png"),
    "Thermite": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1385.png"),
    "Ash": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1386.png"),
    "Thatcher": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1387.png"),
    "Sledge": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1388.png"),
    "Buck": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1389.png"),
    "Blitz": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1390.png"),
    "IQ": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1391.png"),
    "Fuze": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1392.png"),
    "Glaz": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1393.png"),
    "Amaru": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1394.png"),
    "Gridlock": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1395.png"),
    "Iana": os.path.join(UI_DIR, "operator_portraits", "attackers", "Group 1396.png"),
}

FLOOR_ICONS = {
    "Sotano": ICON["floor_sotano"],
    "Primer Piso": ICON["floor_primer_piso"],
    "Segundo Piso": ICON["floor_segundo_piso"],
    "Tejado": ICON["floor_tejado"],
}

# --- Paleta (tomada del moodboard: "Táctico Diegético Sutil") ---
COLOR_ORANGE = (255, 140, 0)
COLOR_ORANGE_TEXT = (255, 165, 60)
COLOR_LIME = (120, 184, 0)      # verde lima de "Coloca tus habilidades..." y fondo de REFERENCIAS
COLOR_BLUE = (94, 140, 255)      # "MI EQUIPO" / nombres propios
COLOR_RED = (255, 90, 90)        # "EQUIPO RIVAL"
COLOR_GREY_PANEL = (60, 60, 60)  # fondo gris del header de prep
COLOR_TEXT_LIGHT = (230, 230, 230)


def register_fonts():
    """Registra las variantes de Barlow Condensed en Qt. Llamar una sola vez
    al arrancar la app, antes de crear cualquier QFont con esta familia."""
    from PyQt6.QtGui import QFontDatabase
    for filename in FONT_FILES:
        path = os.path.join(FONTS_DIR, filename)
        if os.path.exists(path):
            QFontDatabase.addApplicationFont(path)
