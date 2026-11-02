"""Bando de cada operador para corregir el lado al reconocer al jugador."""

DEFENDERS = frozenset({
    "Noor", "Denari", "Skopos", "Sentry", "Tubarao", "Fenrir", "Solis", "Azami",
    "Thorn", "Thunderbird", "Aruni", "Melusi", "Oryx", "Wamai", "Goyo", "Warden",
    "Mozzie", "Kaid", "Clash", "Maestro", "Alibi", "Vigil", "Ela", "Lesion",
    "Mira", "Echo", "Caveira", "Valkyrie", "Frost", "Mute", "Smoke", "Castle",
    "Pulse", "Doc", "Rook", "Jager", "Tachanka", "Kapkan", "Bandit",
})

ATTACKERS = frozenset({
    "Solid Snake", "Rauora", "Striker", "Deimos", "Ram", "Brava", "Sens", "Osa",
    "Flores", "Zero", "Ace", "Kali", "Nokk", "Nomad", "Maverick", "Lion",
    "Finka", "Dokkaebi", "Zofia", "Ying", "Jackal", "Hibana", "Capitao",
    "Blackbeard", "Buck", "Sledge", "Thatcher", "Ash", "Thermite", "Montagne",
    "Twitch", "Blitz", "IQ", "Fuze", "Glaz", "Grim", "Amaru", "Iana", "Gridlock",
})


def get_operator_side(name: str) -> str | None:
    if name in DEFENDERS:
        return "Defensores"
    if name in ATTACKERS:
        return "Atacantes"
    return None
