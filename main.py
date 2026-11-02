"""Punto de entrada del HUD. Las librerías nativas de visión/audio viven
fuera del proceso Qt para que un fallo de una DLL no cierre la interfaz.

El proceso principal contiene solo PyQt6, estado y señales. Los procesos
auxiliares envían mensajes JSON Lines y nunca manipulan widgets directamente.
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import threading
import time
import traceback
import faulthandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for _env_name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_env_name] = "1"

try:
    _faulthandler_log = open(os.path.join(BASE_DIR, "faulthandler_dump.txt"), "a", buffering=1, encoding="utf-8")
    faulthandler.enable(file=_faulthandler_log, all_threads=True)
except Exception:
    _faulthandler_log = None

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, Qt, QTimer
from PyQt6.QtWidgets import QApplication

from ui.overlay import Overlay
from data.map_calibration import list_maps_with_images
from data.operator_roles import get_operator_side


class MatchState:
    """Estado de ronda modificado exclusivamente desde el hilo Qt."""
    def __init__(self):
        maps = list_maps_with_images()
        self.current_map = "Consulado" if "Consulado" in maps else (maps[0] if maps else "Consulado")
        self.current_floor = "Primer Piso"

    def cycle_map(self, overlay: Overlay):
        maps = list_maps_with_images()
        if not maps:
            return
        try:
            idx = maps.index(self.current_map)
            self.current_map = maps[(idx + 1) % len(maps)]
        except ValueError:
            self.current_map = maps[0]
        overlay.show_ephemeral_notice(f"Mapa: {self.current_map}", duration_ms=1500)
        if overlay.state.map_panel_visible:
            overlay._set_current_map(self.current_map, self.current_floor)
            overlay.update()


match_state = MatchState()


class Bridge(QObject):
    """Todas las actualizaciones hacia Qt pasan por estas señales."""
    sound_update = pyqtSignal(float, float, str, object)
    sound_error = pyqtSignal(str)
    sound_ready = pyqtSignal()
    minimap_frame = pyqtSignal(object)
    floor_changed = pyqtSignal(str)
    map_detected = pyqtSignal(str)
    team_detected = pyqtSignal(object)
    enemy_icon_seen = pyqtSignal(str)
    my_operator_seen = pyqtSignal(str)
    side_detected = pyqtSignal(str)
    hotkey_pressed = pyqtSignal(str)


class UiDispatcher(QObject):
    """Slots del hilo GUI; ningún proceso/hilo auxiliar toca widgets."""
    def __init__(self, overlay: Overlay, bridge: Bridge):
        super().__init__(overlay)
        self.overlay = overlay
        bridge.sound_update.connect(self.on_sound_update, Qt.ConnectionType.QueuedConnection)
        bridge.sound_error.connect(self.on_sound_error, Qt.ConnectionType.QueuedConnection)
        bridge.sound_ready.connect(self.on_sound_ready, Qt.ConnectionType.QueuedConnection)
        bridge.minimap_frame.connect(self.on_minimap_frame, Qt.ConnectionType.QueuedConnection)
        bridge.floor_changed.connect(self.on_floor_changed, Qt.ConnectionType.QueuedConnection)
        bridge.map_detected.connect(self.on_map_detected, Qt.ConnectionType.QueuedConnection)
        bridge.team_detected.connect(self.on_team_detected, Qt.ConnectionType.QueuedConnection)
        bridge.enemy_icon_seen.connect(self.on_enemy_icon_seen, Qt.ConnectionType.QueuedConnection)
        bridge.my_operator_seen.connect(self.on_my_operator_seen, Qt.ConnectionType.QueuedConnection)
        bridge.side_detected.connect(self.on_side_detected, Qt.ConnectionType.QueuedConnection)
        bridge.hotkey_pressed.connect(self.on_hotkey_pressed, Qt.ConnectionType.QueuedConnection)

    @pyqtSlot(float, float, str, object)
    def on_sound_update(self, angle: float, intensity: float, floor_hint: str, sound_type: object):
        try:
            self.overlay.update_sound_direction(angle, intensity)
        except Exception as exc:
            print(f"[main] Error actualizando audio en GUI: {type(exc).__name__}: {exc}", flush=True)

    @pyqtSlot(str)
    def on_sound_error(self, message: str):
        print(f"[audio] {message}", flush=True)
        try:
            self.overlay.show_ephemeral_notice(f"Audio: {message.splitlines()[0][:80]}", duration_ms=4000)
        except Exception as exc:
            print(f"[main] Error presentando fallo de audio: {exc}", flush=True)

    @pyqtSlot()
    def on_sound_ready(self):
        print("[audio] Proceso aislado de audio listo.", flush=True)

    @pyqtSlot(object)
    def on_minimap_frame(self, payload):
        try:
            raw, width, height = payload
            self.overlay.update_minimap_frame(raw, width=width, height=height)
        except Exception as exc:
            print(f"[main] Error actualizando minimapa: {type(exc).__name__}: {exc}", flush=True)

    @pyqtSlot(str)
    def on_floor_changed(self, floor_name: str):
        match_state.current_floor = floor_name
        try:
            if self.overlay.state.map_panel_visible:
                self.overlay._set_current_map(match_state.current_map, floor_name)
                self.overlay.update()
        except Exception as exc:
            print(f"[main] Error actualizando piso: {type(exc).__name__}: {exc}", flush=True)

    @pyqtSlot(str)
    def on_map_detected(self, map_name: str):
        match_state.current_map = map_name
        try:
            self.overlay.show_ephemeral_notice(f"Mapa detectado: {map_name}", duration_ms=2500)
            if self.overlay.state.map_panel_visible:
                self.overlay._set_current_map(map_name, match_state.current_floor)
                self.overlay.update()
        except Exception as exc:
            print(f"[main] Error actualizando mapa: {type(exc).__name__}: {exc}", flush=True)

    @pyqtSlot(object)
    def on_team_detected(self, operators):
        try:
            own = self.overlay.state.my_kit
            current = list(self.overlay.state.teammates)
            incoming = list(operators or [])
            # La fila del HUD aporta el roster de ronda; el OCR de preparación
            # puede completar nombres que aún no hayan sido leídos por icono.
            merged = list(dict.fromkeys(current + incoming))
            if own:
                merged = [name for name in merged if name.casefold() != own.casefold()]
            self.overlay.set_teammates(merged[:4])
            if incoming:
                self.overlay.show_ephemeral_notice("Equipo detectado", duration_ms=2000)
        except Exception as exc:
            print(f"[main] Error actualizando equipo: {type(exc).__name__}: {exc}", flush=True)

    @pyqtSlot(str)
    def on_enemy_icon_seen(self, operator_name: str):
        try:
            self.overlay.register_enemy_kit(operator_name, operator_name)
            self.overlay.show_ephemeral_notice(f"Detectado: {operator_name}", duration_ms=2500)
        except Exception as exc:
            print(f"[main] Error actualizando icono enemigo: {type(exc).__name__}: {exc}", flush=True)

    @pyqtSlot(str)
    def on_my_operator_seen(self, operator_name: str):
        try:
            self.overlay.set_my_kit(operator_name)
            self.overlay.set_teammates([
                name for name in self.overlay.state.teammates
                if name.casefold() != operator_name.casefold()
            ])
            side = get_operator_side(operator_name)
            if side:
                self.overlay.state.my_side = side
            self.overlay.show_ephemeral_notice(f"Tu operador: {operator_name}", duration_ms=2000)
        except Exception as exc:
            print(f"[main] Error actualizando operador propio: {type(exc).__name__}: {exc}", flush=True)

    @pyqtSlot(str)
    def on_side_detected(self, side: str):
        try:
            self.overlay.state.my_side = side
            self.overlay.show_ephemeral_notice(f"Tu lado: {side}", duration_ms=1500)
        except Exception as exc:
            print(f"[main] Error actualizando bando: {type(exc).__name__}: {exc}", flush=True)

    @pyqtSlot(str)
    def on_hotkey_pressed(self, key: str):
        try:
            self._dispatch_hotkey(key)
        except Exception as exc:
            print(f"[hotkeys] Error ejecutando {key}: {type(exc).__name__}: {exc}", flush=True)

    def _dispatch_hotkey(self, key: str):
        if key == "F1":
            self.overlay.toggle_tactical_hud()


def _reader_thread(name: str, target):
    try:
        thread = threading.Thread(name=name, target=target, daemon=True)
        thread.start()
        return thread
    except Exception as exc:
        print(f"[{name}] No se pudo iniciar lector: {type(exc).__name__}: {exc}", flush=True)
        return None


def start_audio_process(bridge: Bridge):
    worker_script = os.path.join(BASE_DIR, "audio", "worker.py")
    return _start_json_worker("audio", worker_script, bridge, audio_protocol=True)


def start_vision_process(bridge: Bridge):
    worker_script = os.path.join(BASE_DIR, "vision", "worker.py")
    return _start_json_worker("vision", worker_script, bridge, audio_protocol=False)


def _start_json_worker(label: str, script: str, bridge: Bridge, *, audio_protocol: bool):
    if not os.path.isfile(script):
        print(f"[{label}] No existe el proceso auxiliar: {script}", flush=True)
        return None, None

    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
    try:
        process = subprocess.Popen(
            [sys.executable, script],
            cwd=BASE_DIR,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=None,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            creationflags=creationflags,
        )
    except Exception as exc:
        print(f"[{label}] No se pudo iniciar el proceso auxiliar: {type(exc).__name__}: {exc}", flush=True)
        if audio_protocol:
            bridge.sound_error.emit(f"No se pudo iniciar audio: {exc}")
        return None, None

    print(f"[{label}] Proceso auxiliar iniciado (PID {process.pid}).", flush=True)

    def relay_messages():
        try:
            assert process.stdout is not None
            for line in process.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    message = json.loads(line)
                except json.JSONDecodeError:
                    print(f"[{label}-worker] Mensaje no válido: {line[:180]}", flush=True)
                    continue

                kind = message.get("type")
                if audio_protocol:
                    if kind == "installing":
                        print(f"[{label}] {message.get('message', 'Preparando backend de audio')} ", flush=True)
                    elif kind == "ready":
                        bridge.sound_ready.emit()
                    elif kind == "update":
                        bridge.sound_update.emit(
                            float(message.get("angle", 0.0)),
                            float(message.get("intensity", 0.0)),
                            str(message.get("floor_hint", "indeterminado")),
                            message.get("sound_type"),
                        )
                    elif kind in ("error", "fatal", "unavailable"):
                        detail = str(message.get("message", "Error de audio"))
                        print(f"[{label}-worker] {kind}: {detail}", flush=True)
                        bridge.sound_error.emit(detail.splitlines()[0][:160])
                    elif kind == "stopped":
                        print(f"[{label}-worker] {message.get('reason', 'Detenido')}", flush=True)
                    continue

                if kind == "ready":
                    print("[vision] Proceso auxiliar de captura/OCR listo.", flush=True)
                elif kind == "minimap_frame":
                    try:
                        raw = base64.b64decode(message.get("data", ""), validate=True)
                        width = int(message.get("width", 0))
                        height = int(message.get("height", 0))
                        if width > 0 and height > 0 and len(raw) == width * height * 4:
                            bridge.minimap_frame.emit((raw, width, height))
                    except Exception as exc:
                        print(f"[vision] Frame de minimapa inválido: {type(exc).__name__}: {exc}", flush=True)
                elif kind == "floor":
                    bridge.floor_changed.emit(str(message.get("value", "")))
                elif kind == "map":
                    bridge.map_detected.emit(str(message.get("value", "")))
                elif kind == "team":
                    bridge.team_detected.emit(message.get("value", []))
                elif kind == "enemy":
                    bridge.enemy_icon_seen.emit(str(message.get("value", "")))
                elif kind == "self_operator":
                    bridge.my_operator_seen.emit(str(message.get("value", "")))
                elif kind == "side":
                    bridge.side_detected.emit(str(message.get("value", "")))
                elif kind == "fatal":
                    print(f"[vision-worker] Fallo fatal: {message.get('message', '')}", flush=True)
        except Exception as exc:
            print(f"[{label}] Error leyendo mensajes: {type(exc).__name__}: {exc}", flush=True)
        finally:
            try:
                code = process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                code = process.poll()
            if code not in (0, None):
                unsigned = int(code) & 0xFFFFFFFF
                detail = f"Proceso {label} finalizó con código {code} (0x{unsigned:08X}). La interfaz Qt sigue activa."
                print(f"[{label}] {detail}", flush=True)
                if audio_protocol:
                    bridge.sound_error.emit(detail)
            else:
                print(f"[{label}] Proceso auxiliar finalizado.", flush=True)

    reader = _reader_thread(f"{label}-process-reader", relay_messages)
    return process, reader


def _stop_process(process, label: str):
    if process is None or process.poll() is not None:
        return
    try:
        process.terminate()
        process.wait(timeout=2.0)
    except Exception:
        try:
            process.kill()
        except Exception:
            pass


def setup_hotkeys(bridge: Bridge):
    from ui.win_hotkeys import HAS_WIN_HOTKEYS
    labels = ["F1", "insert"]
    if HAS_WIN_HOTKEYS:
        from ui.win_hotkeys import start_hotkey_thread, VK_F1, VK_INSERT
        vk_codes = [VK_F1, VK_INSERT]
        bindings = [(vk, (lambda: bridge.hotkey_pressed.emit("F1"))) for vk in vk_codes]
        start_hotkey_thread(bindings)
        return
    try:
        import keyboard
        for key in labels:
            keyboard.add_hotkey(key, lambda: bridge.hotkey_pressed.emit("F1"))
    except Exception as exc:
        print(f"[hotkeys] No se pudieron registrar hotkeys globales: {type(exc).__name__}: {exc}", flush=True)


def main():
    print(f"[startup] Python {sys.version.split()[0]} | {sys.executable}", flush=True)
    print(f"[startup] PID={os.getpid()} | proceso Qt sin OpenCV/MSS/pytesseract", flush=True)

    app = QApplication(sys.argv)
    app.setApplicationName("R6 Tactical Overlay")
    overlay = Overlay()
    bridge = Bridge()
    dispatcher = UiDispatcher(overlay, bridge)
    app._r6_bridge = bridge
    app._r6_dispatcher = dispatcher

    try:
        setup_hotkeys(bridge)
    except Exception as exc:
        print(f"[hotkeys] Error de inicialización: {type(exc).__name__}: {exc}", flush=True)

    # El HUD táctico arranca oculto; la capa ligera de sonido ya queda activa.

    audio_process, audio_reader = start_audio_process(bridge)
    vision_process, vision_reader = start_vision_process(bridge)
    app._r6_audio_process = audio_process
    app._r6_audio_reader = audio_reader
    app._r6_vision_process = vision_process
    app._r6_vision_reader = vision_reader

    # Si el worker de visión tropieza con una DLL nativa, reiniciamos el
    # subsistema de detección de forma limitada. La interfaz no se reinicia.
    restart_state = {"count": 0, "next_at": time.monotonic() + 6.0}
    restart_timer = QTimer(app)
    restart_timer.setInterval(2000)

    def check_vision_worker():
        current = app._r6_vision_process
        if current is None or current.poll() is None:
            return
        if restart_state["count"] >= 3 or time.monotonic() < restart_state["next_at"]:
            return
        code = current.returncode
        unsigned = int(code or 0) & 0xFFFFFFFF
        restart_state["count"] += 1
        restart_state["next_at"] = time.monotonic() + min(30.0, 5.0 * restart_state["count"])
        print(f"[vision] Worker detenido (0x{unsigned:08X}); reinicio {restart_state['count']}/3.", flush=True)
        new_process, new_reader = start_vision_process(bridge)
        app._r6_vision_process = new_process
        app._r6_vision_reader = new_reader

    restart_timer.timeout.connect(check_vision_worker)
    restart_timer.start()
    app._r6_vision_restart_timer = restart_timer

    app.aboutToQuit.connect(lambda: _stop_process(audio_process, "audio"))
    app.aboutToQuit.connect(lambda: _stop_process(app._r6_vision_process, "vision"))
    return app.exec()


if __name__ == "__main__":
    try:
        if hasattr(__import__("multiprocessing"), "freeze_support"):
            __import__("multiprocessing").freeze_support()
        sys.exit(main())
    except Exception:
        print("[main] Error fatal no capturado:\n" + traceback.format_exc(), flush=True)
        raise
