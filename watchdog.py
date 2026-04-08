"""
watchdog.py — Vigila yolo8_tracking_people.py y lo reinicia si se detiene.

Uso normal (el Task Scheduler lo lanza automáticamente al iniciar sesión):
    d:\a2_centinela\python.exe watchdog.py

Para detener el sistema: cerrar esta ventana o Ctrl+C.
"""
import subprocess
import time
import sys
import os
import datetime

# ---------------------------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------------------------

SCRIPT        = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'yolo8_tracking_people.py')
PYTHON        = sys.executable          # apunta al python.exe del ambiente conda
STARTUP_DELAY = 30                      # segundos de espera al arrancar Windows (red + cámara)
RESTART_DELAY = 15                      # segundos de espera antes de reiniciar tras un fallo
LOG_FILE      = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'watchdog.log')


# ---------------------------------------------------------------------------
# UTILIDADES
# ---------------------------------------------------------------------------

def log(msg):
    ts   = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


# ---------------------------------------------------------------------------
# BUCLE PRINCIPAL
# ---------------------------------------------------------------------------

log("=" * 60)
log("Watchdog iniciado.")
log(f"Script vigilado : {SCRIPT}")
log(f"Python           : {PYTHON}")
log(f"Delay arranque   : {STARTUP_DELAY}s")
log(f"Delay reinicio   : {RESTART_DELAY}s")
log("=" * 60)

log(f"Esperando {STARTUP_DELAY}s para que la red y la cámara estén disponibles...")
try:
    time.sleep(STARTUP_DELAY)
except KeyboardInterrupt:
    log("Watchdog detenido por el usuario durante la espera inicial.")
    sys.exit(0)

while True:
    log("Lanzando proceso principal...")
    try:
        proc      = subprocess.Popen([PYTHON, SCRIPT])
        exit_code = proc.wait()
    except FileNotFoundError:
        log(f"ERROR: No se encontró el script '{SCRIPT}'.")
        exit_code = -1
    except KeyboardInterrupt:
        log("Watchdog detenido por el usuario.")
        break
    except Exception as e:
        log(f"ERROR inesperado al lanzar el proceso: {e}")
        exit_code = -1

    if exit_code == 0:
        # Salida limpia (ej. usuario cerró la ventana con 'q') — no reiniciar
        log("Proceso terminó limpiamente (código 0). Watchdog se detiene.")
        break

    log(f"Proceso terminó inesperadamente (código {exit_code}). "
        f"Reiniciando en {RESTART_DELAY}s...")

    try:
        time.sleep(RESTART_DELAY)
    except KeyboardInterrupt:
        log("Watchdog detenido por el usuario durante la espera.")
        break

log("Watchdog finalizado.")
