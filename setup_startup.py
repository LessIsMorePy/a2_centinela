"""
setup_startup.py — Registra el watchdog en el Task Scheduler de Windows.

REQUISITO: Ejecutar UNA SOLA VEZ como Administrador:
    Clic derecho sobre este archivo → "Ejecutar con Python" como Administrador
    o desde una terminal con privilegios elevados:
        d:\a2_centinela\python.exe setup_startup.py

Para eliminar la tarea más adelante:
    d:\a2_centinela\python.exe setup_startup.py --remove
"""
import subprocess
import sys
import os

# ---------------------------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------------------------

TASK_NAME   = 'Centinela_Arcos'
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
WATCHDOG    = os.path.join(SCRIPT_DIR, 'watchdog.py')
PYTHON_EXE  = sys.executable       # d:\a2_centinela\python.exe
LOGON_DELAY = '0:30'               # 30 s de espera tras el inicio de sesión
                                   # (da tiempo a que la red y la cámara levanten)


# ---------------------------------------------------------------------------
# REGISTRO / ELIMINACIÓN
# ---------------------------------------------------------------------------

def register():
    cmd = [
        'schtasks', '/Create', '/F',
        '/TN', TASK_NAME,
        '/TR', f'"{PYTHON_EXE}" "{WATCHDOG}"',
        '/SC', 'ONLOGON',           # se ejecuta al iniciar sesión
        '/DELAY', LOGON_DELAY,
        '/RL', 'HIGHEST',           # privilegios elevados
        '/IT',                      # permite interacción con el escritorio (ventana visible)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅  Tarea '{TASK_NAME}' registrada correctamente.")
        print(f"    Python  : {PYTHON_EXE}")
        print(f"    Script  : {WATCHDOG}")
        print(f"    Trigger : Al iniciar sesión (con 30 s de retardo)")
        print()
        print("El sistema se iniciará automáticamente la próxima vez que arranque Windows.")
    else:
        print(f"❌  Error al registrar la tarea:\n{result.stderr}")
        print("    Asegúrate de ejecutar este script como Administrador.")


def remove():
    cmd = ['schtasks', '/Delete', '/F', '/TN', TASK_NAME]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅  Tarea '{TASK_NAME}' eliminada del Task Scheduler.")
    else:
        print(f"❌  No se pudo eliminar la tarea:\n{result.stderr}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    if '--remove' in sys.argv:
        remove()
    else:
        register()
