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
        from vision.operator_icon_match import (
            run_icon_watch_loop, run_enemy_roster_watch_loop, run_team_roster_watch_loop,
            MY_OPERATOR_ICON_REGION,
        )
        from vision.side_ocr import run_side_detection_loop
        from vision.phase_ocr import run_preparation_detection_loop

        try:
            import cv2
            import numpy as np
            cv2.setNumThreads(1)
            try:
                cv2.ocl.setUseOpenCL(False)
            except Exception:
                pass
            print(f"[vision-worker] OpenCV {cv2.__version__} limitado a 1 hilo; OpenCL OFF.", flush=True)
        except Exception as exc:
            print(f"[vision-worker] OpenCV no disponible: {type(exc).__name__}: {exc}", flush=True)
            cv2 = None
            np = None

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

        video_versions = {}
        video_lock = threading.Lock()

        def play_animation(filename: str, output_width: int, output_height: int, loop: bool = False):
            if cv2 is None or np is None:
                print("[vision-worker] No se puede reproducir video: OpenCV no está disponible.", flush=True)
                return
            if filename == "iana_gadget_loop.mp4":
                path = os.path.join(PROJECT_ROOT, "assets", "recursos", "videospj", "atacantes", "IANA.mp4")
            else:
                path = os.path.join(PROJECT_ROOT, "assets", "recursos", "ANIMACIONES", filename)
            with video_lock:
                version = video_versions.get(filename, 0) + 1
                video_versions[filename] = version

            def decode():
                capture = cv2.VideoCapture(path)
                if not capture.isOpened():
                    print(f"[vision-worker] No se pudo abrir la animación {filename}.", flush=True)
                    return
                fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
                width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
                total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
                if output_width > 0 and output_height > 0:
                    width, height = output_width, output_height
                elif width > 1920:
                    height = max(1, round(height * 1920 / width))
                    width = 1920
                frame_index = 0
                last_panel_rect = (0, 0, 0, 0)
                deadline = time.monotonic()
                try:
                    while True:
                        with video_lock:
                            if video_versions.get(filename) != version:
                                break
                        ok, frame = capture.read()
                        if not ok:
                            if loop and total > 0:
                                capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                                frame_index = 0
                                deadline = time.monotonic()
                                continue
                            break
                        if frame.shape[1] != width or frame.shape[0] != height:
                            frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
                        if loop:
                            crop_x = crop_y = 0
                            crop_h, crop_w = frame.shape[:2]
                            cropped = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
                            cropped[:, :, 3] = 255
                            bounds = None
                        else:
                            visible = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            visible = cv2.compare(visible, 12, cv2.CMP_GT)
                            bounds = cv2.findNonZero(visible)
                        panel_rect = last_panel_rect
                        if filename.startswith("Gadget "):
                            b, g, r = cv2.split(frame)
                            green = ((g > 80) & (g.astype(np.int16) > r.astype(np.int16) * 1.25)
                                     & (g.astype(np.int16) > b.astype(np.int16) * 1.25)).astype(np.uint8) * 255
                            contours, _ = cv2.findContours(green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                            candidates = []
                            for contour in contours:
                                px, py, pw, ph = cv2.boundingRect(contour)
                                # La etiqueta F4 va fuera del panel; el panel nace pegado al borde izquierdo.
                                if px < max(5, int(width * 0.10)):
                                    candidates.append((pw * ph, (px, py, pw, ph)))
                            if candidates:
                                panel_rect = max(candidates, key=lambda item: item[0])[1]
                                last_panel_rect = panel_rect
                        if loop:
                            pass
                        elif bounds is None:
                            crop_x = crop_y = 0
                            crop_w = crop_h = 1
                            cropped = np.zeros((1, 1, 4), dtype=np.uint8)
                        else:
                            crop_x, crop_y, crop_w, crop_h = cv2.boundingRect(bounds)
                            color_crop = frame[crop_y:crop_y + crop_h, crop_x:crop_x + crop_w]
                            cropped = cv2.cvtColor(color_crop, cv2.COLOR_BGR2BGRA)
                        # Los recursos usan negro transparente para el overlay.
                        if bounds is not None and not loop:
                            alpha = visible[crop_y:crop_y + crop_h, crop_x:crop_x + crop_w].copy()
                            if filename.startswith("Gadget "):
                                yy, xx = np.ogrid[crop_y:crop_y + crop_h, crop_x:crop_x + crop_w]
                                blue = color_crop[:, :, 0]
                                green_channel = color_crop[:, :, 1]
                                red = color_crop[:, :, 2]
                                # La tarjeta real reemplaza las etiquetas genéricas del clip.
                                header_text = ((xx < width * 0.18) & (yy < height * 0.25)
                                               & (blue > 150) & (green_channel > 150) & (red > 150)
                                               & (np.maximum.reduce((blue, green_channel, red))
                                                  - np.minimum.reduce((blue, green_channel, red)) < 65))
                                footer_text = ((xx > width * 0.48) & (yy > height * 0.70)
                                               & (red > 100) & (green_channel > 45)
                                               & (red.astype(np.int16) > green_channel.astype(np.int16) * 1.25)
                                               & (blue < 100))
                                alpha[header_text | footer_text] = 0
                            cropped[:, :, 3] = alpha
                        ok, encoded = cv2.imencode(".png", cropped, [cv2.IMWRITE_PNG_COMPRESSION, 1])
                        if ok:
                            send({"type": "video_frame", "name": filename,
                                  "width": crop_w, "height": crop_h,
                                  "x": crop_x, "y": crop_y,
                                  "canvas_width": width, "canvas_height": height,
                                  "panel": panel_rect,
                                  "index": frame_index, "total": total,
                                  "data": base64.b64encode(encoded).decode("ascii")})
                        frame_index += 1
                        deadline += 1.0 / max(1.0, fps)
                        wait = deadline - time.monotonic()
                        if wait > 0:
                            time.sleep(wait)
                except Exception as exc:
                    print(f"[vision-worker] Falló la animación {filename}: {type(exc).__name__}: {exc}", flush=True)
                finally:
                    capture.release()
                    with video_lock:
                        still_current = video_versions.get(filename) == version
                    if still_current and not loop:
                        send({"type": "video_finished", "name": filename})

            start_thread(f"video-{filename}", decode)

        def read_video_commands():
            for line in sys.stdin:
                try:
                    command = json.loads(line)
                    if command.get("type") == "play_video":
                        filename = os.path.basename(str(command.get("name", "")))
                        play_animation(
                            filename,
                            int(command.get("width", 0)), int(command.get("height", 0)),
                            bool(command.get("loop", False)) and filename == "iana_gadget_loop.mp4",
                        )
                    elif command.get("type") == "stop_video":
                        with video_lock:
                            name = os.path.basename(str(command.get("name", "")))
                            video_versions[name] = video_versions.get(name, 0) + 1
                except Exception as exc:
                    print(f"[vision-worker] Comando de video inválido: {type(exc).__name__}: {exc}", flush=True)

        start_thread("video-command-reader", read_video_commands)

        send({"type": "ready"})
        start_thread("minimap-reader", run_minimap_stream, minimap_callback, interval_s=0.25)
        if TESSERACT_AVAILABLE:
            start_thread("floor-ocr", run_floor_detection_loop, lambda value: send({"type": "floor", "value": str(value)}))
        else:
            print("[vision-worker] Tesseract no disponible; piso manual mediante F2.", flush=True)
        start_thread("map-ocr", run_map_detection_loop, lambda value: send({"type": "map", "value": str(value)}))
        # El roster superior es la fuente única de composición. El OCR de la
        # zona inferior puede confundir el chat con nombres de agentes, y el
        # killfeed no permite saber con seguridad a qué bando pertenece cada icono.
        start_thread("operator-icon-self", run_icon_watch_loop,
                     lambda value: send({"type": "self_operator", "value": str(value)}),
                     region=MY_OPERATOR_ICON_REGION, search=True, min_confidence=0.68)
        start_thread("operator-icons-enemy-roster", run_enemy_roster_watch_loop,
                     lambda value: send({"type": "enemy", "value": str(value)}))
        start_thread("operator-icons-team-roster", run_team_roster_watch_loop,
                     lambda value: send({"type": "team", "value": list(value or [])}))
        start_thread("side-ocr", run_side_detection_loop,
                     lambda value: send({"type": "side", "value": str(value)}))
        start_thread("preparation-phase-ocr", run_preparation_detection_loop,
                     lambda: send({"type": "round_start"}))

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
