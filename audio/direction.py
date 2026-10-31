"""
Captura el audio del sistema mediante el dispositivo loopback WASAPI de
PyAudioWPatch. Todo el acceso nativo se ejecuta en audio/worker.py, proceso
separado del proceso gráfico PyQt6: un fallo del backend nunca debe cerrar
la ventana del HUD.

El procesamiento de dirección/intensidad se realiza con NumPy después de
leer bloques estéreo del dispositivo de salida de Windows.
"""

import time
import traceback

import numpy as np


SAMPLE_RATE = 48000
# 4096 (antes 2048) -- el log mostró "data discontinuity in recording"
# (buffer de WASAPI desbordándose) de forma repetida. Doblar el tamaño del
# bloque (~85ms) da más margen antes de que el buffer
# se desborde, a cambio de un poquito más de latencia -- razonable para
# dirección de sonido (no hace falta reaccionar en milisegundos).
BLOCK_SIZE = 4096


def _open_default_wasapi_loopback(pyaudio):
    """Devuelve (manager, stream, sample_rate, channels, device_name)."""
    manager = pyaudio.PyAudio()
    try:
        device = manager.get_default_wasapi_loopback()
        channels = min(2, max(1, int(device.get("maxInputChannels", 0))))
        sample_rate = int(float(device.get("defaultSampleRate", SAMPLE_RATE)))
        if channels < 1:
            raise RuntimeError("El loopback WASAPI no ofrece canales de entrada.")
        stream = manager.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            input=True,
            input_device_index=int(device["index"]),
            frames_per_buffer=BLOCK_SIZE,
        )
        return manager, stream, sample_rate, channels, str(device.get("name", "WASAPI loopback"))
    except BaseException:
        manager.terminate()
        raise


def to_mono(stereo_block: np.ndarray) -> np.ndarray:
    """Reemplazo de librosa.to_mono para un bloque (n_samples, 2)."""
    return stereo_block.mean(axis=1).astype(np.float32)


def spectral_centroid(mono_block: np.ndarray, sr: int = SAMPLE_RATE) -> float:
    """Reemplazo de librosa.feature.spectral_centroid, con FFT de numpy puro.
    Devuelve la frecuencia (Hz) donde se concentra el "centro de masa" del
    espectro -- un proxy de qué tan "brillante" u "oscuro" es el sonido."""
    if mono_block.size == 0:
        return 0.0
    windowed = mono_block * np.hanning(len(mono_block))
    spectrum = np.abs(np.fft.rfft(windowed))
    freqs = np.fft.rfftfreq(len(mono_block), d=1.0 / sr)
    total = spectrum.sum()
    if total < 1e-9:
        return 0.0
    return float((freqs * spectrum).sum() / total)


def onset_strength(mono_block: np.ndarray) -> float:
    """Aproximación simple de librosa.onset.onset_strength: compara la
    energía de la primera mitad del bloque contra la segunda. Un salto
    brusco de energía (ej. un disparo empezando a mitad del bloque) da un
    valor alto. Es más tosco que el de librosa, pero no depende de
    ninguna librería con código nativo compilado."""
    if mono_block.size < 4:
        return 0.0
    mid = len(mono_block) // 2
    energy_a = np.sqrt(np.mean(mono_block[:mid] ** 2))
    energy_b = np.sqrt(np.mean(mono_block[mid:] ** 2))
    return float(max(0.0, energy_b - energy_a) * 50)  # escala ajustable


def estimate_direction(stereo_block: np.ndarray) -> tuple[float, float]:
    """
    stereo_block: array shape (n_samples, 2)
    Devuelve (angle_deg, intensity) donde:
      angle_deg: -90 (izquierda) a +90 (derecha), 0 = centro
      intensity: 0.0 a 1.0, proxy de volumen/cercanía
    """
    left = stereo_block[:, 0]
    right = stereo_block[:, 1]

    energy_l = np.sqrt(np.mean(left ** 2)) + 1e-9
    energy_r = np.sqrt(np.mean(right ** 2)) + 1e-9

    diff = (energy_r - energy_l) / (energy_r + energy_l)
    angle_deg = float(diff * 90)  # -90 a +90

    intensity = float(min(1.0, (energy_l + energy_r) / 2 * 8))  # escala ajustable

    return angle_deg, intensity


def estimate_floor_difference(mono_block: np.ndarray, sr: int = SAMPLE_RATE) -> str:
    """Estimación aproximada de 'mismo piso' vs 'otro piso' según brillo espectral."""
    if np.max(np.abs(mono_block)) < 1e-4:
        return "indeterminado"

    centroid = spectral_centroid(mono_block, sr)

    THRESHOLD_HZ = 1500.0  # a calibrar escuchando tus propios clips de R6
    return "mismo_nivel" if centroid >= THRESHOLD_HZ else "otro_nivel"


def classify_sound_placeholder(mono_block: np.ndarray, sr: int = SAMPLE_RATE) -> str | None:
    """Placeholder de clasificación por energía/centroide -- reemplazar por un
    modelo entrenado cuando tengas dataset propio."""
    rms = float(np.sqrt(np.mean(mono_block ** 2)))
    if rms < 0.01:
        return None

    centroid = spectral_centroid(mono_block, sr)
    onset = onset_strength(mono_block)

    if rms > 0.15 and onset > 5:
        return "explosion"
    if centroid > 3000 and onset > 3:
        return "disparo"
    if 800 < centroid < 3000:
        return "pasos"
    return None


def run_audio_loop(on_update, on_error=None, on_ready=None):
    """Lee audio loopback WASAPI y emite análisis; backend aislado por proceso."""
    manager = None
    stream = None
    try:
        import pyaudiowpatch as pyaudio
        manager, stream, sample_rate, channels, device_name = _open_default_wasapi_loopback(pyaudio)
        if on_ready:
            on_ready()
        print(
            f"[audio] Loopback WASAPI abierto con PyAudioWPatch sobre '{device_name}' "
            f"({sample_rate} Hz, {channels} canales). Escuchando...",
            flush=True,
        )

        while True:
            try:
                raw = stream.read(BLOCK_SIZE, exception_on_overflow=False)
                if not raw:
                    time.sleep(0.05)
                    continue
                samples = np.frombuffer(raw, dtype=np.int16)
                usable = (samples.size // channels) * channels
                if usable <= 0:
                    time.sleep(0.05)
                    continue
                block = samples[:usable].reshape(-1, channels).astype(np.float32) / 32768.0
                if channels == 1:
                    stereo = np.repeat(block, 2, axis=1)
                else:
                    stereo = block[:, :2]
                if stereo.size == 0:
                    continue

                angle_deg, intensity = estimate_direction(stereo)
                mono = to_mono(stereo)
                floor_hint = estimate_floor_difference(mono, sample_rate)
                sound_type = classify_sound_placeholder(mono, sample_rate)
                if on_update:
                    on_update(angle_deg, intensity, floor_hint, sound_type)
            except Exception as exc:
                print(
                    f"[audio] Error transitorio en lectura/procesado; se reintenta: "
                    f"{type(exc).__name__}: {exc}", flush=True,
                )
                time.sleep(0.15)
                continue

    except BaseException as exc:
        detail = traceback.format_exc()
        print("[audio] No se pudo mantener el loopback WASAPI:\n" + detail, flush=True)
        if on_error:
            on_error(f"{type(exc).__name__}: {exc}")
    finally:
        if stream is not None:
            try:
                stream.stop_stream()
            except Exception:
                pass
            try:
                stream.close()
            except Exception:
                pass
        if manager is not None:
            try:
                manager.terminate()
            except Exception:
                pass
