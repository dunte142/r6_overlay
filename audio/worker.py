"""Proceso aislado para captura WASAPI/loopback.

PyAudioWPatch accede al loopback WASAPI mediante PortAudio. Se ejecuta en un
proceso separado del proceso Qt para que un fallo nativo del backend de audio
no pueda cerrar el launcher ni el HUD. La salida stdout es un protocolo JSONL;
los mensajes de diagnóstico de direction.py se redirigen a stderr.
"""
from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
import traceback

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

_protocol_out = sys.stdout
sys.stdout = sys.stderr


def _send(message: dict) -> None:
    try:
        _protocol_out.write(json.dumps(message, ensure_ascii=False) + "\n")
        _protocol_out.flush()
    except Exception:
        # El proceso GUI puede cerrarse mientras WASAPI aún está activo.
        pass


def _ensure_pyaudiowpatch():
    """Importa PyAudioWPatch o intenta instalar su wheel para este Python.

    El worker usa exactamente sys.executable del proceso principal. Esto evita
    que el paquete quede instalado en otro Python cuando hay varias versiones
    (por ejemplo, el launcher de Microsoft Store y Python.org) en Windows.
    """
    module_name = "pyaudiowpatch"
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        if exc.name != module_name:
            raise

    _send({
        "type": "installing",
        "message": "PyAudioWPatch no está instalado en este Python; intentando instalar el wheel compatible.",
    })
    print(
        f"[audio-worker] Falta {module_name}; instalando PyAudioWPatch==0.2.12.9 "
        f"con {sys.executable}",
        file=sys.stderr,
        flush=True,
    )

    command = [
        sys.executable, "-m", "pip", "install",
        "--disable-pip-version-check", "--no-input", "--only-binary=:all:",
        "PyAudioWPatch==0.2.12.9",
    ]
    env = os.environ.copy()
    env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    env["PIP_NO_INPUT"] = "1"
    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            check=False,
            env=env,
        )
    except subprocess.TimeoutExpired:
        _send({"type": "unavailable", "message": "La instalación de PyAudioWPatch superó los 180 segundos. El HUD seguirá funcionando sin análisis de audio."})
        return None
    except Exception as exc:
        _send({"type": "unavailable", "message": f"No se pudo ejecutar pip para instalar PyAudioWPatch: {type(exc).__name__}: {exc}"})
        return None

    if result.stdout:
        for line in result.stdout.strip().splitlines()[-12:]:
            print(f"[audio-install] {line}", file=sys.stderr, flush=True)

    if result.returncode != 0:
        _send({
            "type": "unavailable",
            "message": f"pip no pudo instalar PyAudioWPatch (código {result.returncode}). Ejecutá: {sys.executable} -m pip install --only-binary=:all: PyAudioWPatch==0.2.12.9. El HUD seguirá funcionando sin audio.",
        })
        return None

    importlib.invalidate_caches()
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        _send({
            "type": "unavailable",
            "message": f"PyAudioWPatch se instaló pero no se pudo importar: {type(exc).__name__}: {exc}. El HUD seguirá funcionando sin audio.",
        })
        return None

    print("[audio-worker] PyAudioWPatch instalado y verificado.", file=sys.stderr, flush=True)
    return module


def main() -> int:
    try:
        # Autorreparación puntual: si se lanzó main.py sin pasar por iniciar.bat,
        # instala la dependencia en el mismo intérprete que ejecuta el HUD.
        audio_backend = _ensure_pyaudiowpatch()
        if audio_backend is None:
            return 0

        # Importar aquí mantiene PortAudio/WASAPI fuera del proceso Qt.
        from audio.direction import run_audio_loop

        def on_update(angle_deg, intensity, floor_hint, sound_type):
            _send({
                "type": "update",
                "angle": float(angle_deg),
                "intensity": float(intensity),
                "floor_hint": str(floor_hint),
                "sound_type": sound_type,
            })

        def on_error(message):
            _send({"type": "error", "message": str(message)})

        def on_ready():
            _send({"type": "ready"})

        run_audio_loop(on_update, on_error=on_error, on_ready=on_ready)
        _send({"type": "stopped", "reason": "El bucle de audio terminó."})
        return 0
    except BaseException:
        detail = traceback.format_exc()
        print("[audio-worker] Fallo no controlado:\n" + detail, file=sys.stderr, flush=True)
        _send({"type": "fatal", "message": detail})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
