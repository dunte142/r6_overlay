"""
Busca el binario de Tesseract OCR y lo configura para pytesseract si no
está en el PATH de Windows.

Por qué esto hace falta: pytesseract (la librería de Python, la que se
instala con pip) NO incluye el programa de Tesseract -- es solo un
"control remoto" que le pide a Windows que ejecute el comando "tesseract"
por su nombre, confiando en que esté en el PATH. El instalador oficial de
Tesseract para Windows (UB-Mannheim) NO agrega la carpeta al PATH a menos
que se tilde esa opción durante la instalación -- fácil de pasar por alto,
y el resultado es "lo instalé pero el programa dice que no lo encuentra"
(exactamente lo que pasó: se instaló en C:\\Program Files\\Tesseract-OCR
pero TesseractNotFoundError siguió apareciendo).

En vez de mandar al usuario a pelearse con el PATH de Windows otra vez
(ya tuvo bastante con el alias de python.exe de la Microsoft Store), esto
busca el binario en las carpetas donde el instalador oficial lo pone por
defecto y, si lo encuentra ahí, le pasa la ruta completa a pytesseract
directamente -- sin tocar ninguna variable de entorno del sistema.
"""

import os
import shutil

_COMMON_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]

_configured = False
_available = False


def configure_tesseract() -> bool:
    """Devuelve True si Tesseract quedó accesible (ya estaba en el PATH, o
    se encontró en una ubicación default y se configuró), False si no se
    encontró en ningún lado conocido. Solo hace el trabajo real la primera
    vez que se llama -- las siguientes devuelven el resultado ya calculado,
    porque esto se llama desde varios módulos (floor_ocr, map_ocr, team_ocr)."""
    global _configured, _available
    if _configured:
        return _available
    _configured = True

    if shutil.which("tesseract"):
        _available = True
        return True

    try:
        import pytesseract
    except ImportError:
        _available = False
        return False

    for path in _COMMON_PATHS:
        if os.path.isfile(path):
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"[tesseract_setup] Tesseract no estaba en el PATH de Windows "
                  f"-- se encontró la instalación en '{path}' y se usa esa ruta "
                  f"directamente (no hace falta tocar el PATH).", flush=True)
            _available = True
            return True

    print("[tesseract_setup] No se encontró el binario de Tesseract OCR ni en "
          "el PATH ni en las ubicaciones default. Si lo instalaste en una "
          "carpeta distinta a 'C:\\Program Files\\Tesseract-OCR', agregá esa "
          "ruta a vision/tesseract_setup.py (_COMMON_PATHS) o a tu PATH.", flush=True)
    _available = False
    return False
