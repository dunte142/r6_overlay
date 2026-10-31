"""Captura pasiva de pantalla, segura frente a transiciones de DirectX.

Cada hilo mantiene su instancia MSS y todas las llamadas a grab() quedan
serializadas con NATIVE_LOCK. Se aceptan las APIs públicas de MSS 10.2/11 y
los monitores antiguos tipo dict o nuevos tipo objeto. Además se validan los
frames para reintentar ante transiciones de DirectX.
"""
from __future__ import annotations

import threading
import time
from typing import Any

import mss
import numpy as np

from vision.native_lock import NATIVE_LOCK

_thread_local = threading.local()


def _create_mss_instance() -> Any:
    """Crea MSS usando cualquiera de las APIs públicas habituales.

    MSS 10/11 documentan `from mss import MSS`; algunas instalaciones o
    versiones exponen además la fábrica `mss.mss()`. No se asume que el
    atributo `MSS` exista dentro del módulo importado como `mss`.
    """
    try:
        from mss import MSS
        return MSS()
    except (ImportError, AttributeError):
        factory = getattr(mss, "mss", None)
        if callable(factory):
            return factory()
        cls = getattr(mss, "MSS", None)
        if callable(cls):
            return cls()
        try:
            from mss.windows import MSS as WindowsMSS
            return WindowsMSS()
        except Exception as exc:
            module_path = getattr(mss, "__file__", "<desconocido>")
            raise RuntimeError(
                "La instalación importada como 'mss' no expone MSS() ni mss(). "
                f"Módulo: {module_path}. Verificá que no exista un archivo local mss.py "
                "y reinstalá con `python -m pip install --force-reinstall mss==10.2.0`."
            ) from exc


def _get_thread_sct() -> Any:
    """Una instancia MSS por hilo, reutilizada entre capturas."""
    sct = getattr(_thread_local, "sct", None)
    if sct is None:
        with NATIVE_LOCK:
            sct = _create_mss_instance()
            _thread_local.sct = sct
    return sct


def _monitor_to_dict(monitor: Any) -> dict[str, int]:
    """Normaliza monitores dict (MSS antiguo) y modelos Monitor (MSS nuevo)."""
    result: dict[str, int] = {}
    for key in ("left", "top", "width", "height"):
        try:
            value = monitor[key]
        except (TypeError, KeyError, AttributeError):
            value = getattr(monitor, key, None)
        if value is None:
            raise RuntimeError(f"MSS no informó el campo '{key}' del monitor")
        result[key] = int(value)
    return result


def get_primary_monitor() -> dict[str, int]:
    """Devuelve el rectángulo del monitor principal, compatible con MSS 10/11."""
    with NATIVE_LOCK:
        sct = _get_thread_sct()
        primary = getattr(sct, "primary_monitor", None)
        if primary is None:
            monitors = sct.monitors
            if len(monitors) < 2:
                raise RuntimeError("mss no informó un monitor principal disponible")
            primary = monitors[1]
        return _monitor_to_dict(primary)


def _normalize_region(region: dict[str, Any], monitor: dict[str, int]) -> dict[str, int]:
    try:
        left = int(region.get("left", monitor["left"]))
        top = int(region.get("top", monitor["top"]))
        width = int(region.get("width", monitor["width"]))
        height = int(region.get("height", monitor["height"]))
    except (TypeError, ValueError) as exc:
        raise ValueError("La región de captura tiene coordenadas no válidas") from exc
    if width <= 0 or height <= 0:
        raise ValueError("La región de captura debe tener ancho y alto positivos")

    # Recorta regiones ligeramente fuera del monitor tras un cambio de
    # resolución. Un rectángulo completamente fuera de pantalla se reintenta
    # desde el loop, no se convierte en un array vacío.
    right = min(left + width, monitor["left"] + monitor["width"])
    bottom = min(top + height, monitor["top"] + monitor["height"])
    left = max(left, monitor["left"])
    top = max(top, monitor["top"])
    width, height = right - left, bottom - top
    if width <= 0 or height <= 0:
        raise RuntimeError("La región de captura quedó fuera del monitor activo")
    return {"left": left, "top": top, "width": width, "height": height}


def capture_region(region: dict | None = None) -> np.ndarray:
    """Devuelve un frame BGRA no vacío o genera una excepción recuperable."""
    with NATIVE_LOCK:
        sct = _get_thread_sct()
        if len(sct.monitors) < 2:
            raise RuntimeError("No se encontró el monitor principal")
        primary = getattr(sct, "primary_monitor", None)
        if primary is None:
            monitors = sct.monitors
            if len(monitors) < 2:
                raise RuntimeError("No se encontró el monitor principal")
            primary = monitors[1]
        monitor = _monitor_to_dict(primary)
        target = monitor if region is None else _normalize_region(region, monitor)
        shot = sct.grab(target)
        frame = np.asarray(shot, dtype=np.uint8)
        if frame.size == 0 or frame.ndim != 3 or frame.shape[0] < 1 or frame.shape[1] < 1:
            raise RuntimeError("Captura vacía durante una transición de pantalla/DirectX")
        # Copia para no exponer el buffer interno de ScreenShot al siguiente grab().
        return frame.copy()


def capture_hud_own_kit_region() -> np.ndarray:
    """Captura de compatibilidad para calibraciones antiguas (región 1080p)."""
    return capture_region({"top": 950, "left": 20, "width": 400, "height": 130})


def retry_delay(seconds: float = 0.25) -> None:
    """Pequeño backoff compartido por loops que sufren frames transitorios."""
    time.sleep(max(0.02, float(seconds)))
