"""
Hotkeys globales (F1-F6) vía la API nativa de Windows RegisterHotKey, en vez
de la librería 'keyboard'.

Primer intento (descartado): 'keyboard' instala un hook global de teclado
de bajo nivel (SetWindowsHookEx) que intercepta CADA tecla del sistema
entero -- produjo un crash nativo real (access violation de Windows) en la
máquina del usuario.

Segundo intento (TAMBIÉN descartado, por eso este archivo quedó así):
RegisterHotKey + un QAbstractNativeEventFilter que leía cada mensaje nativo
de Windows que le llegaba a Qt (vía wintypes.MSG.from_address(int(message)))
para filtrar el WM_HOTKEY. Esto también crasheó, en el mismo punto exacto
(al entrar al loop principal de Qt) -- muy probablemente porque esa lectura
de memoria cruda a partir de un puntero interno de Qt no es 100% segura en
esta versión de PyQt6/máquina, y se dispara en CADA mensaje nativo, no solo
en los hotkeys -- o sea, en el primerísimo mensaje que procesa Qt.

Enfoque actual: un hilo de Python APARTE, con su propio loop clásico de
Windows (RegisterHotKey + GetMessage), que nunca toca un puntero interno de
Qt ni un mensaje que Qt ya esté procesando -- es el mismo patrón que usan
audio/visión (que sí andan bien): corren en su hilo, y avisan al overlay
mandando una señal de Qt (thread-safe), nunca tocando widgets directamente
desde ese hilo.

RegisterHotKey exige que el registro y el GetMessage que lo recibe corran
en el MISMO hilo -- por eso ambos pasos están en la función que arranca
el hilo, no repartidos entre setup_hotkeys() (hilo principal) y el loop.

Solo funciona en Windows (es una API de Win32). En cualquier otro sistema,
HAS_WIN_HOTKEYS queda en False y quien use este módulo debe degradar solo
(ver main.py).
"""

import sys
import threading

HAS_WIN_HOTKEYS = sys.platform == "win32"

if HAS_WIN_HOTKEYS:
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32

    WM_HOTKEY = 0x0312
    MOD_NOREPEAT = 0x4000  # evita que se dispare en bucle mientras la tecla queda apretada

    # Códigos de tecla virtual de Windows para F1-F6 (son consecutivos).
    VK_F1 = 0x70
    VK_F2 = 0x71
    VK_F3 = 0x72
    VK_F4 = 0x73
    VK_F5 = 0x74
    VK_F6 = 0x75

    def run_hotkey_thread(bindings: list[tuple[int, callable]]):
        """
        bindings: lista de (código_virtual, callback). callback se llama
        (desde ESTE hilo, nunca el de Qt) cuando esa tecla se presiona --
        quien conecte esto debe mandar la señal correspondiente a Qt en vez
        de tocar un QWidget directamente acá (igual que audio/visión).

        Corre para siempre (loop de mensajes clásico de Windows). Pensado
        para lanzarse en un threading.Thread(daemon=True) -- si falla, avisa
        una vez y corta en vez de reintentar para siempre o tumbar el resto
        del programa.
        """
        callbacks_by_id = {}
        try:
            for i, (vk, callback) in enumerate(bindings, start=1):
                ok = user32.RegisterHotKey(None, i, MOD_NOREPEAT, vk)
                if not ok:
                    err = ctypes.get_last_error()
                    print(f"[win_hotkeys] No se pudo registrar la tecla "
                          f"(código virtual {hex(vk)}, error de Windows "
                          f"{err}) -- puede estar tomada por otro programa. "
                          f"Esa tecla en particular no va a funcionar; el "
                          f"resto del overlay sigue normal.")
                    continue
                callbacks_by_id[i] = callback

            print(f"[win_hotkeys] {len(callbacks_by_id)}/{len(bindings)} "
                  f"hotkeys registradas OK.", flush=True)

            if not callbacks_by_id:
                print("[win_hotkeys] Ninguna hotkey se pudo registrar -- "
                      "F1-F6 no van a funcionar. El resto del overlay sigue "
                      "normal.")
                return

            msg = wintypes.MSG()
            while True:
                # GetMessageW bloquea hasta el próximo mensaje -- no gasta
                # CPU en un loop ocupado, a diferencia de un polling propio.
                ret = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if ret == 0:  # WM_QUIT
                    break
                if ret == -1:  # error
                    err = ctypes.get_last_error()
                    print(f"[win_hotkeys] GetMessage devolvió error "
                          f"({err}) -- deteniendo el hilo de hotkeys. El "
                          f"resto del overlay sigue normal.")
                    break
                if msg.message == WM_HOTKEY:
                    callback = callbacks_by_id.get(msg.wParam)
                    # Diagnóstico: confirma que Windows SÍ entregó la tecla a
                    # este programa (si el usuario reporta que F1-F3 "no
                    # responden" y esta línea no aparece en el log, el
                    # problema es que el mensaje nunca llegó -- otro
                    # programa se la robó antes -- no un bug de este código).
                    print(f"[win_hotkeys] WM_HOTKEY recibido (id={msg.wParam})", flush=True)
                    if callback:
                        try:
                            callback()
                        except Exception as e:
                            print(f"[win_hotkeys] Error en callback de "
                                  f"hotkey: {type(e).__name__}: {e}")
        except Exception as e:
            print(f"[win_hotkeys] El hilo de hotkeys falló "
                  f"({type(e).__name__}: {e}) -- F1-F6 no van a funcionar. "
                  f"El resto del overlay sigue normal.")
        finally:
            for hotkey_id in list(callbacks_by_id.keys()):
                try:
                    user32.UnregisterHotKey(None, hotkey_id)
                except Exception:
                    pass

    def start_hotkey_thread(bindings: list[tuple[int, callable]]) -> threading.Thread:
        t = threading.Thread(target=run_hotkey_thread, args=(bindings,), daemon=True)
        t.start()
        return t
