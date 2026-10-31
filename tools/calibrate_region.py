"""
Calibra por clicks las regiones que el resto del proyecto captura de tu
pantalla (el minimapa nativo, el indicador de piso), en vez de tener que
adivinar porcentajes a mano.

Uso, con el juego abierto y visible (Alt+Tab a este script sin cerrar R6):

    python -m tools.calibrate_region minimap
    python -m tools.calibrate_region floor
    python -m tools.calibrate_region map_name
    python -m tools.calibrate_region team_sidebar
    python -m tools.calibrate_region killfeed
    python -m tools.calibrate_region my_operator
    python -m tools.calibrate_region side

Toma una captura de TODA tu pantalla, la muestra en una ventana, y
clickeás 2 puntos: la esquina superior izquierda y la esquina inferior
derecha de la región que querés capturar (el minimapa completo, o el
recuadro del indicador de piso). Te imprime el bloque de código listo
para pegar.
"""

import sys

import cv2
import numpy as np
import mss


REGION_INFO = {
    "minimap": {
        "instructions": "Clickeá la esquina SUP-IZQ y después INF-DER del minimapa nativo completo.",
        "target_file": "vision/minimap_reader.py",
        "target_var": "MINIMAP_REGION_FRACTIONS",
    },
    "floor": {
        "instructions": "Clickeá la esquina SUP-IZQ y después INF-DER del recuadro donde aparece el indicador de piso (ej. 'P1 Sala de estar').",
        "target_file": "vision/floor_ocr.py",
        "target_var": "FLOOR_INDICATOR_FRACTIONS",
    },
    "map_name": {
        "instructions": "Con la pantalla de selección/baneo de mapa O la carga de partida visible, clickeá SUP-IZQ y después INF-DER del recuadro donde aparece el NOMBRE del mapa.",
        "target_file": "vision/map_ocr.py",
        "target_var": "MAP_NAME_REGION_FRACTIONS",
    },
    "team_sidebar": {
        "instructions": "Con la fase de preparación visible, clickeá SUP-IZQ y después INF-DER de la franja que lista a los 5 integrantes de tu equipo con su operador elegido.",
        "target_file": "vision/team_ocr.py",
        "target_var": "TEAM_SIDEBAR_REGION_FRACTIONS",
    },
    "killfeed": {
        "instructions": "Con un killfeed visible en pantalla (apenas elimines a alguien o te eliminen), clickeá SUP-IZQ y después INF-DER SOLO del icono cuadrado del operador en la linea mas reciente -- no el texto, no toda la franja.",
        "target_file": "vision/operator_icon_match.py",
        "target_var": "KILLFEED_ICON_REGION_FRACTIONS",
    },
    "my_operator": {
        "instructions": "En juego (no en la fase de preparación), clickeá SUP-IZQ y después INF-DER SOLO del ícono de habilidad resaltado/más blanco en tu barra de HUD -- el que identifica a TU operador, no el resto de la barra.",
        "target_file": "vision/operator_icon_match.py",
        "target_var": "MY_OPERATOR_ICON_REGION_FRACTIONS",
    },
    "side": {
        "instructions": "Al terminar una ronda, cuando aparezca solo el panel 'MI EQUIPO Defensores/Atacantes', clickeá SUP-IZQ y después INF-DER SOLO del texto 'Defensores'/'Atacantes' de TU equipo (el de la izquierda -- nunca el de 'EQUIPO RIVAL').",
        "target_file": "vision/side_ocr.py",
        "target_var": "SIDE_REGION_FRACTIONS",
    },
}


def _capture_full_screen() -> tuple[np.ndarray, dict]:
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        frame = np.array(sct.grab(monitor))
    return frame, monitor


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in REGION_INFO:
        print(__doc__)
        sys.exit(1)

    key = sys.argv[1]
    info = REGION_INFO[key]

    print(info["instructions"])
    print("'q' para cancelar.\n")

    frame, monitor = _capture_full_screen()
    bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    # Downscale para que la ventana entre en pantalla si tenés un monitor grande
    display_scale = min(1.0, 1400 / bgr.shape[1])
    display = cv2.resize(bgr, None, fx=display_scale, fy=display_scale)

    points = []
    window = "Click esquina SUP-IZQ, despues INF-DER -- 'q' cancela"

    def on_click(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 2:
            # Reconvertimos a coordenadas de la captura original (sin escalar)
            real_x, real_y = int(x / display_scale), int(y / display_scale)
            points.append((real_x, real_y))
            cv2.circle(display, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow(window, display)

    cv2.imshow(window, display)
    cv2.setMouseCallback(window, on_click)

    while len(points) < 2:
        if cv2.waitKey(50) & 0xFF == ord('q'):
            sys.exit("Cancelado.")
    cv2.waitKey(300)
    cv2.destroyAllWindows()

    (x1, y1), (x2, y2) = points
    left, top = min(x1, x2), min(y1, y2)
    width, height = abs(x2 - x1), abs(y2 - y1)

    frac_left = left / monitor["width"]
    frac_top = top / monitor["height"]
    frac_width = width / monitor["width"]
    frac_height = height / monitor["height"]

    print("\n" + "=" * 60)
    print(f"Pegá esto en {info['target_file']}, reemplazando {info['target_var']}:")
    print("=" * 60)
    print(f'''
{info["target_var"]} = {{
    "left": {frac_left:.4f}, "top": {frac_top:.4f},
    "width": {frac_width:.4f}, "height": {frac_height:.4f},
}}''')
    print("=" * 60)


if __name__ == "__main__":
    main()
