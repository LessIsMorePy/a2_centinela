import threading
import winsound


def play_alert():
    """
    Reproduce un beep de alerta sin bloquear el hilo principal.
    Usa winsound en Windows (frecuencia 1000 Hz, duración 400 ms).
    Fallback a print si no está disponible (Linux / Docker).
    """
    def _play():
        try:
            # winsound.Beep(1000, 1000)
            winsound.PlaySound('bienvenido.wav', 0)
        except ImportError:
            # En entornos sin winsound (Linux/Docker), usar print como fallback
            print("\a[ALERTA] Persona detectada entrando a la tienda")

    t = threading.Thread(target=_play, daemon=True)
    t.start()
