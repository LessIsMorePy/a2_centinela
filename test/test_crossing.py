"""
test_crossing.py — Verifica la lógica de cruce horizontal y diagonal.
No requiere cámara ni dependencias externas más allá de numpy/opencv.
"""
import sys
sys.path.insert(0, '..')
import tracking_functions_people as tf


def test_crossed_line():
    """Línea horizontal — entrada de arriba hacia abajo."""
    line_y = 650

    assert tf.crossed_line(620, 670, line_y) == True,  "Debe detectar entrada"
    assert tf.crossed_line(660, 700, line_y) == False, "Ya estaba adentro"
    assert tf.crossed_line(670, 620, line_y) == False, "Salida no cuenta"
    assert tf.crossed_line(600, 640, line_y) == False, "Aún en la calle"
    assert tf.crossed_line(630, 650, line_y) == True,  "Cruce exacto sobre la línea"

    print("✅ test_crossed_line — PASÓ")


def test_crossed_line_diagonal():
    """Línea diagonal — entrada de derecha a izquierda (lateral)."""
    line_d = tf.get_crossing_line_diagonal()   # (1700, 1080) → (1430, 420)

    # Caso 1: viene de la calle lateral (exterior) y entra a la tienda
    assert tf.crossed_line_diagonal((1750, 600), (1550, 750), line_d) == True, \
        "Debe detectar entrada por la derecha"

    # Caso 2: ya estaba adentro moviéndose — no debe contar
    assert tf.crossed_line_diagonal((1300, 800), (1200, 850), line_d) == False, \
        "Ya estaba adentro, no debe detectar"

    # Caso 3: sale de la tienda hacia la calle — no cuenta como entrada
    assert tf.crossed_line_diagonal((1400, 700), (1750, 500), line_d) == False, \
        "Salida no debe contar como entrada"

    print("✅ test_crossed_line_diagonal — PASÓ")


def test_point_in_polygon():
    """Zona de interés — verifica puntos dentro y fuera del polígono."""
    poly = tf.get_zone_polygon()

    assert tf.point_in_polygon((960,  800), poly) == True,  "Centro-interior debe estar dentro"
    assert tf.point_in_polygon((100,  900), poly) == True,  "Izquierda-interior debe estar dentro"
    assert tf.point_in_polygon((960,  200), poly) == False, "Zona de calle debe estar fuera"

    print("✅ test_point_in_polygon — PASÓ")


if __name__ == '__main__':
    test_crossed_line()
    test_crossed_line_diagonal()
    test_point_in_polygon()
    print("\n✅ Todos los tests pasaron.")
