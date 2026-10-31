"""Proceso auxiliar para captura, OCR y detección visual.

Todo el código que carga MSS, NumPy, OpenCV o pytesseract vive aquí y no en el
proceso de PyQt6. Si una DLL nativa termina con STATUS_HEAP_CORRUPTION, Windows
solo finaliza este proceso y el HUD principal puede permanecer abierto.

Protocolo stdout: JSON Lines. Los logs de Python/librerías se redirigen a stderr.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import threading
import time
import traceback

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

_protocol_stdout = sys.stdout
sys.stdout = sys.stderr
_send_lock = threading.Lock()


def send(message: dict) -> None:
    try:
        payload = json.dumps(message, ensure_ascii=False, separators=(",", ":"))
        with _send_lock:
            _protocol_stdout.write(payload + "\n")
            _protocol_stdout.flush()
    except Exception as exc:
        print(f"[vision-worker] No se pudo enviar mensaje: {type(exc).__name__}: {exc}", flush=True)


def start_thread(name: str, target, *args, **kwargs) -> threading.Thread | None:
    def guarded_target():
        try:
            target(*args, **kwargs)
        except BaseException:
            print(f"[vision-worker] El detector {name} terminó por excepción:\n{traceback.format_exc()}", flush=True)

    try:
        thread = threading.Thread(name=name, target=guarded_target, daemon=True)
        thread.start()
        print(f"[vision-worker] {name} iniciado (daemon).", flush=True)
        return thread
    except Exception as exc:
        print(f"[vision-worker] No se pudo iniciar {name}: {type(exc).__name__}: {exc}", flush=True)
        return None


def main() -> int:
    try:
        print(f"[vision-worker] Python {sys.version.split()[0]} | {sys.executable}", flush=True)

        # Registrar el origen y las APIs visibles de MSS para diagnosticar
        # instalaciones duplicadas o módulos locales que sombreen el paquete.
        try:
            import mss
            print(
                f"[vision-worker] MSS module={getattr(mss, '__file__', '<sin ruta>')} | "
                f"MSS_class={callable(getattr(mss, 'MSS', None))} | "
                f"mss_factory={callable(getattr(mss, 'mss', None))}",
                flush=True,
            )
        except Exception as exc:
            print(f"[vision-worker] No se pudo inspeccionar MSS: {type(exc).__name__}: {exc}", flush=True)

        # Los imports nativos se producen exclusivamente en este proceso.
        from vision.minimap_reader import run_minimap_stream
        from vision.floor_ocr import run_floor_detection_loop, TESSERACT_AVAILABLE
        from vision.map_ocr import run_map_detection_loop
        from vision.team_ocr import run_team_detection_loop
        from vision.operator_icon_match import run_icon_watch_loop, MY_OPERATOR_ICON_REGION
        from vision.side_ocr import run_side_detection_loop

        try:
            import cv2
            cv2.setNumThreads(1)
            try:
                cv2.ocl.setUseOpenCL(False)
            except Exception:
                pass
            print(f"[vision-worker] OpenCV {cv2.__version__} limitado a 1 hilo; OpenCL OFF.", flush=True)
        except Exception as exc:
            print(f"[vision-worker] OpenCV no disponible: {type(exc).__name__}: {exc}", flush=True)

        try:
            import mss
            import numpy
            print(f"[vision-worker] MSS {getattr(mss, '__version__', 'desconocido')} | NumPy {numpy.__version__}", flush=True)
        except Exception as exc:
            print(f"[vision-worker] Captura sin dependencias completas: {type(exc).__name__}: {exc}", flush=True)

        def minimap_callback(frame):
            try:
                if frame is None or getattr(frame, "size", 0) == 0 or frame.ndim != 3:
                    return
                height, width = frame.shape[:2]
                if frame.shape[2] != 4:
                    return
                # La región del minimapa es pequeña. Raw BGRA evita cargar un
                # codificador de imagen adicional en el proceso principal.
                raw = frame.tobytes(order="C")
                send({
                    "type": "minimap_frame",
                    "width": int(width),
                    "height": int(height),
                    "data": base64.b64encode(raw).decode("ascii"),
                })
            except Exception as exc:
                print(f"[vision-worker] Error serializando minimapa: {type(exc).__name__}: {exc}", flush=True)

        send({"type": "ready"})
        start_thread("minimap-reader", run_minimap_stream, minimap_callback, interval_s=0.25)
        if TESSERACT_AVAILABLE:
            start_thread("floor-ocr", run_floor_detection_loop, lambda value: send({"type": "floor", "value": str(value)}))
        else:
            print("[vision-worker] Tesseract no disponible; piso manual mediante F2.", flush=True)
        start_thread("map-ocr", run_map_detection_loop, lambda value: send({"type": "map", "value": str(value)}))
        start_thread("team-ocr", run_team_detection_loop, lambda value: send({"type": "team", "value": list(value or [])}))
        start_thread("operator-icon-killfeed", run_icon_watch_loop, lambda value: send({"type": "enemy", "value": str(value)}))
        start_thread("operator-icon-self", run_icon_watch_loop,
                     lambda value: send({"type": "self_operator", "value": str(value)}),
                     region=MY_OPERATOR_ICON_REGION)
        start_thread("side-ocr", run_side_detection_loop, lambda value: send({"type": "side", "value": str(value)}))

        print("[vision-worker] Todos los detectores configurados; proceso auxiliar activo.", flush=True)
        while True:
            time.sleep(1.0)
    except BaseException:
        detail = traceback.format_exc()
        print("[vision-worker] Fallo fatal:\n" + detail, flush=True)
        send({"type": "fatal", "message": detail})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
