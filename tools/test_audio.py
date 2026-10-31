"""
Prueba SOLO el audio direccional, sin el overlay ni el juego. Corré esto
primero si "el sonido no funciona" -- te dice exactamente qué está
fallando (dispositivo no encontrado, loopback no soportado, etc.) en vez
de fallar en silencio dentro del programa completo.

Uso:
    python -m tools.test_audio

Reproducí algo de audio con tu PC (música, un video) mientras corre --
deberías ver números cambiando en la consola. Ctrl+C para cortar.
"""

import sys
import time

from audio.direction import run_audio_loop


def main():
    print("Buscando dispositivo de audio de salida y abriendo loopback...\n")

    last_print = 0

    def on_ready():
        print("✔ Loopback abierto correctamente. Reproducí algo de audio ahora.\n")
        print(f"{'ángulo':>8} {'intensidad':>11} {'piso':>14} {'sonido':>10}")
        print("-" * 50)

    def on_update(angle_deg, intensity, floor_hint, sound_type):
        nonlocal last_print
        now = time.time()
        if now - last_print < 0.2:  # no spamear la consola
            return
        last_print = now
        bar = "#" * int(intensity * 20)
        print(f"{angle_deg:8.1f} {intensity:11.2f} {floor_hint:>14} {str(sound_type):>10}  {bar}")

    def on_error(msg):
        print("\n✘ ERROR:\n")
        print(msg)
        print("\nSi el mensaje menciona dispositivos disponibles, fijate si "
              "tu salida de audio real está en esa lista con otro nombre.")
        sys.exit(1)

    run_audio_loop(on_update, on_error=on_error, on_ready=on_ready)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCortado por el usuario.")
