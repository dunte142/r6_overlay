"""
Posiciones fijas de cámaras de seguridad por mapa/piso.
Datos estáticos, públicos y ya documentados (tipo r6maps) -- no se leen
del juego en vivo, se cargan una sola vez como referencia.

Coordenadas en porcentaje (0.0 a 1.0) relativas al ancho/alto de la imagen
del mapa, para que el overlay las pueda dibujar sobre cualquier resolución.
"""

MAPS = {
    "Consulado": {
        "Sotano": [
            {"x": 0.32, "y": 0.55, "label": "Garage"},
            {"x": 0.61, "y": 0.40, "label": "Pasillo"},
        ],
        "Primer Piso": [
            {"x": 0.28, "y": 0.12, "label": "Entrada A"},
            {"x": 0.75, "y": 0.20, "label": "Entrada B"},
            {"x": 0.50, "y": 0.70, "label": "Patio C"},
        ],
        # Sumá más pisos / mapas según lo que necesites para tu demo.
    },
}


def get_cameras(map_name: str, floor: str) -> list[dict]:
    return MAPS.get(map_name, {}).get(floor, [])


def list_floors(map_name: str) -> list[str]:
    return list(MAPS.get(map_name, {}).keys())
