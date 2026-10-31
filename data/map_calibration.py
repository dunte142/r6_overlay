"""
Planos por mapa/piso (assets/maps/).

NOTA IMPORTANTE: los campos "src_points"/"dst_points" (calibración
genérica) YA NO SE USAN. Se pensaron para ubicar al jugador sobre el plano,
pero se comprobó con una grabación real que el minimapa del juego está
centrado en el jugador y rota con su mirada, así que la flecha azul siempre
cae en el mismo punto y una homografía fija no puede ubicarte. El panel de
F2 ahora muestra el minimapa real ampliado + este plano como referencia.
Se conservan por si más adelante se implementa localización por
registro de imagen (ver README).
"""

import os

# Este módulo se importa también desde la GUI para resolver rutas de planos.
# Por eso NO carga NumPy/OpenCV al importar: esas DLL quedan confinadas en
# vision/worker.py. Las funciones de homografía legacy los importan de forma
# perezosa únicamente si alguien solicita expresamente una transformación.
from vision.native_lock import NATIVE_LOCK

CV2_AVAILABLE = None


def _load_cv_modules():
    global CV2_AVAILABLE
    try:
        import cv2
        import numpy as np
        try:
            cv2.setNumThreads(1)
            cv2.ocl.setUseOpenCL(False)
        except Exception:
            pass
        CV2_AVAILABLE = True
        return cv2, np
    except Exception:
        CV2_AVAILABLE = False
        return None, None

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "maps")

CALIBRATIONS = {
    ("Bank", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "bank_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Bank", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "bank_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Bank", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "bank_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Bank", "Tejado"): {
        "map_image": os.path.join(ASSETS_DIR, "bank_tejado.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Border", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "border_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Border", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "border_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Border", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "border_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Calypso Casino", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "calypso_casino_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Calypso Casino", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "calypso_casino_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Calypso Casino", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "calypso_casino_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Calypso Casino", "Tejado"): {
        "map_image": os.path.join(ASSETS_DIR, "calypso_casino_tejado.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Chalet", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "chalet_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Chalet", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "chalet_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Chalet", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "chalet_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Chalet", "Tejado"): {
        "map_image": os.path.join(ASSETS_DIR, "chalet_tejado.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Close Quarter", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "close_quarter_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Close Quarter", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "close_quarter_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Clubhouse", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "clubhouse_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Clubhouse", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "clubhouse_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Clubhouse", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "clubhouse_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Clubhouse", "Tejado"): {
        "map_image": os.path.join(ASSETS_DIR, "clubhouse_tejado.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Coastline", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "coastline_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Coastline", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "coastline_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Coastline", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "coastline_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Consulado", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "consulado_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Consulado", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "consulado_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Consulado", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "consulado_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Consulado", "Tejado"): {
        "map_image": os.path.join(ASSETS_DIR, "consulado_tejado.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Emerald Plains", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "emerald_plains_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Emerald Plains", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "emerald_plains_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Emerald Plains", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "emerald_plains_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Favela", "Piso Extra"): {
        "map_image": os.path.join(ASSETS_DIR, "favela_piso_extra.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Favela", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "favela_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Favela", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "favela_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Favela", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "favela_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Favela", "Tejado"): {
        "map_image": os.path.join(ASSETS_DIR, "favela_tejado.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Fortress", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "fortress_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Fortress", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "fortress_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Fortress", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "fortress_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Hereford Base", "Piso Extra"): {
        "map_image": os.path.join(ASSETS_DIR, "hereford_base_piso_extra.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Hereford Base", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "hereford_base_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Hereford Base", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "hereford_base_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Hereford Base", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "hereford_base_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Hereford Base", "Tejado"): {
        "map_image": os.path.join(ASSETS_DIR, "hereford_base_tejado.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("House", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "house_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("House", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "house_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("House", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "house_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("House", "Tejado"): {
        "map_image": os.path.join(ASSETS_DIR, "house_tejado.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Kafe Dostoyevsky", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "kafe_dostoyevsky_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Kafe Dostoyevsky", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "kafe_dostoyevsky_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Kafe Dostoyevsky", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "kafe_dostoyevsky_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Kafe Dostoyevsky", "Tejado"): {
        "map_image": os.path.join(ASSETS_DIR, "kafe_dostoyevsky_tejado.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Kanal", "Piso Extra"): {
        "map_image": os.path.join(ASSETS_DIR, "kanal_piso_extra.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Kanal", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "kanal_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Kanal", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "kanal_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Kanal", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "kanal_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Kanal", "Tejado"): {
        "map_image": os.path.join(ASSETS_DIR, "kanal_tejado.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Lair", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "lair_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Lair", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "lair_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Lair", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "lair_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Lair", "Tejado"): {
        "map_image": os.path.join(ASSETS_DIR, "lair_tejado.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Nighthaven Labs", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "nighthaven_labs_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Nighthaven Labs", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "nighthaven_labs_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Nighthaven Labs", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "nighthaven_labs_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Nighthaven Labs", "Tejado"): {
        "map_image": os.path.join(ASSETS_DIR, "nighthaven_labs_tejado.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Oregon", "Piso Extra"): {
        "map_image": os.path.join(ASSETS_DIR, "oregon_piso_extra.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Oregon", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "oregon_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Oregon", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "oregon_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Oregon", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "oregon_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Oregon", "Tejado"): {
        "map_image": os.path.join(ASSETS_DIR, "oregon_tejado.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Outback", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "outback_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Outback", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "outback_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Outback", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "outback_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Presidential Plane", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "presidential_plane_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Presidential Plane", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "presidential_plane_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Presidential Plane", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "presidential_plane_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Presidential Plane", "Tejado"): {
        "map_image": os.path.join(ASSETS_DIR, "presidential_plane_tejado.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Skyscraper", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "skyscraper_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Skyscraper", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "skyscraper_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Skyscraper", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "skyscraper_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Stadium Alpha", "Piso Extra"): {
        "map_image": os.path.join(ASSETS_DIR, "stadium_alpha_piso_extra.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Stadium Alpha", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "stadium_alpha_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Stadium Alpha", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "stadium_alpha_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Stadium Alpha", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "stadium_alpha_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Stadium Alpha", "Tejado"): {
        "map_image": os.path.join(ASSETS_DIR, "stadium_alpha_tejado.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Stadium Bravo", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "stadium_bravo_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Stadium Bravo", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "stadium_bravo_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Stadium Bravo", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "stadium_bravo_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Stadium Bravo", "Tejado"): {
        "map_image": os.path.join(ASSETS_DIR, "stadium_bravo_tejado.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Theme Park", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "theme_park_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Theme Park", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "theme_park_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Theme Park", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "theme_park_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Tower", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "tower_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Tower", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "tower_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Tower", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "tower_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Tower", "Tejado"): {
        "map_image": os.path.join(ASSETS_DIR, "tower_tejado.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Villa", "Piso Extra"): {
        "map_image": os.path.join(ASSETS_DIR, "villa_piso_extra.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Villa", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "villa_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Villa", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "villa_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Villa", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "villa_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Villa", "Tejado"): {
        "map_image": os.path.join(ASSETS_DIR, "villa_tejado.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Yacht", "Piso Extra"): {
        "map_image": os.path.join(ASSETS_DIR, "yacht_piso_extra.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Yacht", "Primer Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "yacht_primer_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Yacht", "Segundo Piso"): {
        "map_image": os.path.join(ASSETS_DIR, "yacht_segundo_piso.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Yacht", "Sotano"): {
        "map_image": os.path.join(ASSETS_DIR, "yacht_sotano.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
    ("Yacht", "Tejado"): {
        "map_image": os.path.join(ASSETS_DIR, "yacht_tejado.jpg"),
        # Calibración GENÉRICA (no verificada en vivo) -- ver nota arriba.
        "src_points": [(0.05, 0.05), (0.95, 0.05), (0.95, 0.95), (0.05, 0.95)],
        "dst_points": [(70, 39), (1330, 39), (1330, 748), (70, 748)],
    },
}

RANKED_MAP_POOL = [
    "Bank", "Border", "Chalet", "Clubhouse", "Coastline", "Consulado",
    "Emerald Plains", "Favela", "Fortress", "Kafe Dostoyevsky", "Kanal",
    "Lair", "Nighthaven Labs", "Oregon", "Outback", "Skyscraper",
    "Stadium Alpha", "Stadium Bravo", "Theme Park", "Villa",
]

ALL_MAPS = RANKED_MAP_POOL + [
    "Calypso Casino", "Close Quarter", "Hereford Base", "House",
    "Presidential Plane", "Tower", "Yacht",
]


def is_calibrated(map_name: str, floor: str) -> bool:
    """True si hay puntos de calibración cargados (genéricos o reales --
    no distingue entre ambos, ver el comentario en cada entrada)."""
    cal = CALIBRATIONS.get((map_name, floor))
    return bool(cal and cal.get("src_points") and cal.get("dst_points"))


def has_image(map_name: str, floor: str) -> bool:
    return (map_name, floor) in CALIBRATIONS


def list_calibrated_maps() -> list[str]:
    """Mapas con al menos un piso calibrado (genérico o real) -- lo que
    usa F4 para ciclar."""
    return sorted({name for (name, floor) in CALIBRATIONS.keys() if is_calibrated(name, floor)})


def list_maps_with_images() -> list[str]:
    return sorted({name for (name, _floor) in CALIBRATIONS.keys()})


def get_homography(map_name: str, floor: str):
    cv2, np = _load_cv_modules()
    if cv2 is None or np is None:
        return None
    cal = CALIBRATIONS.get((map_name, floor))
    if not cal or not cal.get("src_points") or not cal.get("dst_points"):
        return None
    src = np.array(cal["src_points"], dtype=np.float32)
    dst = np.array(cal["dst_points"], dtype=np.float32)
    with NATIVE_LOCK:
        H, _ = cv2.findHomography(src, dst)
    return H


def get_map_image_path(map_name: str, floor: str) -> str | None:
    cal = CALIBRATIONS.get((map_name, floor))
    return cal["map_image"] if cal else None


def transform_point(map_name: str, floor: str, x_norm: float, y_norm: float) -> tuple[float, float] | None:
    """Convierte una posición normalizada (0-1) del minimapa nativo a
    coordenadas en píxeles sobre tu imagen de mapa calibrada. Devuelve
    None si ese mapa/piso todavía no tiene ninguna calibración cargada."""
    H = get_homography(map_name, floor)
    if H is None:
        return None
    cv2, np = _load_cv_modules()
    if cv2 is None or np is None:
        return None
    pt = np.array([[[x_norm, y_norm]]], dtype=np.float32)
    with NATIVE_LOCK:
        transformed = cv2.perspectiveTransform(pt, H)
    return float(transformed[0][0][0]), float(transformed[0][0][1])
