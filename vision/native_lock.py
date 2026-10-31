"""Serialización global de operaciones que cruzan a librerías nativas.

OpenCV, mss y Tesseract comparten recursos nativos en varios detectores. El
bloqueo es reentrante porque una detección puede agrupar captura + procesado
bajo una misma sección crítica y capture_region() también protege su propia
llamada a mss.
"""
import threading

NATIVE_LOCK = threading.RLock()
