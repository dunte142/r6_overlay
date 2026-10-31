"""
Herramienta de calibración manual. Correr con el juego abierto y el minimapa
visible en pantalla:

    python -m tools.calibrate_minimap

Te muestra 3 ventanas:
  1. La región completa capturada (para ajustar MINIMAP_REGION en minimap_reader.py)
  2. La máscara de color (para ajustar el rango HSV si no detecta bien el triángulo)
  3. El resultado con el centro/ángulo detectado dibujado encima

Presioná 'q' para salir.
"""

import cv2
import numpy as np

from vision.minimap_reader import (
    capture_minimap,
    find_player_marker,
    MINIMAP_REGION,
    PLAYER_MARKER_HSV_LOW,
    PLAYER_MARKER_HSV_HIGH,
)


def main():
    print(f"Región actual: {MINIMAP_REGION}")
    print("Ajustá MINIMAP_REGION en vision/minimap_reader.py si el recorte")
    print("no coincide con el minimapa del juego (ventana 1).")
    print("Presioná 'q' en cualquier ventana para salir.\n")

    while True:
        frame = capture_minimap(MINIMAP_REGION)
        bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, PLAYER_MARKER_HSV_LOW, PLAYER_MARKER_HSV_HIGH)

        result = find_player_marker(frame)
        overlay = bgr.copy()
        if result:
            x_norm, y_norm, angle = result
            h, w = bgr.shape[:2]
            cx, cy = int(x_norm * w), int(y_norm * h)
            cv2.circle(overlay, (cx, cy), 5, (0, 0, 255), -1)
            cv2.putText(overlay, f"{angle:.0f} deg", (cx + 10, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        else:
            cv2.putText(overlay, "SIN DETECCION", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        cv2.imshow("1 - Region capturada", bgr)
        cv2.imshow("2 - Mascara de color", mask)
        cv2.imshow("3 - Deteccion", overlay)

        if cv2.waitKey(50) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
