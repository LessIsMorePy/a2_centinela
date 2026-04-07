import threading
import random
import winsound
import os

# ---------------------------------------------------------------------------
# Archivos de audio disponibles (misma carpeta que este script)
# ---------------------------------------------------------------------------

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_SOUNDS = [
    'bienvenido.wav',
    'hola2.wav',
    'hola3.wav',
    'hola4.wav',
    'hola5.wav',
    'hola6.wav',
    'hola7.wav',
]

_last_sound = None   # evita repetir el mismo audio dos veces seguidas


def play_alert():
    """
    Reproduce un audio de bienvenida distinto en cada llamada.
    Nunca repite el mismo archivo dos veces consecutivas.
    No bloquea el hilo principal.
    """
    def _play():
        global _last_sound

        pool = [s for s in _SOUNDS if s != _last_sound]
        chosen = random.choice(pool)
        _last_sound = chosen

        path = os.path.join(_BASE_DIR, chosen)
        try:
            winsound.PlaySound(path, winsound.SND_FILENAME)
        except Exception as e:
            print(f"\a[ALERTA] Sin audio ({e})")

    threading.Thread(target=_play, daemon=True).start()
