"""Assets de tarjetas de gadget para la capa ligera del overlay."""

import os
import unicodedata


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GADGET_ASSETS_ROOT = os.path.join(PROJECT_ROOT, "assets", "recursos")

DEFENDER_GADGET_CARDS = {
    "Mute": "Group 1074.png",
    "Noor": "Group 1075.png",
    "Denari": "Group 1076.png",
    "Skopos": "Group 1077.png",
    "Sentry": "Group 1078.png",
    "Tubarao": "Group 1079.png",
    "Fenrir": "Group 1080.png",
    "Azami": "Group 1081.png",
    "Thorn": "Group 1082.png",
    "Oryx": "Group 1083.png",
    "Thunderbird": "Group 1084.png",
    "Wamai": "Group 1085.png",
    "Aruni": "Group 1086.png",
    "Goyo": "Group 1087.png",
    "Melusi": "Group 1088.png",
    "Warden": "Group 1089.png",
    "Mozzie": "Group 1090.png",
    "Kaid": "Group 1092.png",
    "Vigil": "Group 1093.png",
    "Clash": "Group 1094.png",
    "Ela": "Group 1095.png",
    "Maestro": "Group 1096.png",
    "Lesion": "Group 1097.png",
    "Mira": "Group 1098.png",
    "Frost": "Group 1099.png",
    "Echo": "Group 1100.png",
    "Smoke": "Group 1101.png",
    "Caveira": "Group 1102.png",
    "Castle": "Group 1103.png",
    "Valkyrie": "Group 1104.png",
    "Pulse": "Group 1105.png",
    "Doc": "Group 1106.png",
    "Kapkan": "Group 1107.png",
    "Rook": "Group 1108.png",
    "Bandit": "Group 1109.png",
    "Tachanka": "Group 1112.png",
    "Solis": "Group 1292.png",
    "Jager": "Group 1587.png",
    "Alibi": "Group 1588.png",
}

ATTACKER_GADGET_CARDS = {
    "Solid Snake": "Group 1114.png",
    "Flores": "Group 1115.png",
    "Finka": "Group 1116.png",
    "Buck": "Group 1117.png",
    "Ram": "Group 1119.png",
    "Nokk": "Group 1120.png",
    "Jackal": "Group 1121.png",
    "Thermite": "Group 1122.png",
    "Grim": "Group 1123.png",
    "Rauora": "Group 1124.png",
    "Zero": "Group 1125.png",
    "Dokkaebi": "Group 1126.png",
    "Sledge": "Group 1127.png",
    "IQ": "Group 1128.png",
    "Brava": "Group 1129.png",
    "Nomad": "Group 1130.png",
    "Hibana": "Group 1131.png",
    "Montagne": "Group 1132.png",
    "Amaru": "Group 1133.png",
    "Ace": "Group 1135.png",
    "Zofia": "Group 1136.png",
    "Thatcher": "Group 1137.png",
    "Fuze": "Group 1138.png",
    "Sens": "Group 1139.png",
    "Maverick": "Group 1140.png",
    "Capitao": "Group 1141.png",
    "Twitch": "Group 1142.png",
    "Gridlock": "Group 1143.png",
    "Kali": "Group 1145.png",
    "Lion": "Group 1146.png",
    "Blackbeard": "Group 1147.png",
    "Glaz": "Group 1148.png",
    "Osa": "Group 1149.png",
    "Ying": "Group 1150.png",
    "Blitz": "Group 1151.png",
    "Iana": "Group 1152.png",
    "Striker": "Group 1589.png",
    "Deimos": "Group 1590.png",
}


def _normalize(name: str) -> str:
    value = unicodedata.normalize("NFKD", name or "")
    return "".join(ch.lower() for ch in value if ch.isalnum())


def get_gadget_card_path(operator_name: str, side: str) -> str | None:
    cards = DEFENDER_GADGET_CARDS if side == "Defensores" else ATTACKER_GADGET_CARDS
    normalized = _normalize(operator_name)
    filename = next((file for name, file in cards.items() if _normalize(name) == normalized), None)
    if not filename:
        return None
    folder = "Gadget_defensores" if side == "Defensores" else "Gadget_atacantes"
    path = os.path.join(GADGET_ASSETS_ROOT, folder, filename)
    return path if os.path.isfile(path) else None
