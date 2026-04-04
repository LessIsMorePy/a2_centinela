import numpy as np
import cv2


# ---------------------------------------------------------------------------
# TRACKING
# ---------------------------------------------------------------------------

def tracking(model, frame, conf=0.5):
    return model.track(
        frame,
        persist=True,
        tracker='bytetrack.yaml',
        conf=conf,
        iou=0.5,
        classes=[0],
        verbose=False
    )


def get_person_detections(results):
    detections = []
    if not results or results[0].boxes is None or results[0].boxes.id is None:
        return detections

    boxes     = results[0].boxes.xyxy.cpu().numpy()
    track_ids = results[0].boxes.id.cpu().numpy()

    for box, track_id in zip(boxes, track_ids):
        x1, y1, x2, y2 = box
        base_x = (x1 + x2) / 2   # centro horizontal del bbox
        base_y = y2               # base del bbox (pies)
        detections.append((int(track_id), (base_x, base_y), (x1, y1, x2, y2)))

    return detections


# ---------------------------------------------------------------------------
# ZONA DE INTERÉS Y LÍNEAS DE CRUCE
# ---------------------------------------------------------------------------

def get_zone_polygon():
    """
    Polígono que cubre el interior completo de la tienda (1920×1080).
    El borde superior sigue la perspectiva del umbral de entrada.
    Ajustar con calibrate_zones.py si es necesario.
    """
    return np.array([
        [0,    500],   # umbral izquierdo (entrada fondo)
        [0,    1080],  # esquina inferior izquierda
        [1800, 1080],  # esquina inferior derecha
        [1400, 420],   # umbral derecho (entrada lateral, más alta por perspectiva)
    ], dtype=np.int32)


def get_crossing_line():
    """
    Línea horizontal — detecta personas que entran de arriba hacia abajo
    (entrada del fondo / calle trasera).
    Condición: prev_Y < line_Y <= curr_Y
    """
    return (0, 750), (1920, 700)


def get_crossing_line_diagonal():
    """
    Línea diagonal — detecta personas que entran de derecha a izquierda
    (entrada lateral derecha / escalones).

    Definida de abajo hacia arriba para que el lado exterior (calle/escalones)
    quede con producto vectorial positivo y el interior negativo:
      - exterior (calle derecha) → cross > 0
      - interior (tienda)        → cross < 0

    Ajustar X si la detección llega tarde o genera falsos positivos.
    """
    return (1650, 1080), (1280, 420)


# ---------------------------------------------------------------------------
# LÓGICA DE CRUCE
# ---------------------------------------------------------------------------

def crossed_line(prev_y, curr_y, line_y):
    """
    Cruce horizontal: persona baja de arriba hacia abajo.
    Condición: prev_Y < line_Y <= curr_Y
    """
    return prev_y < line_y <= curr_y


def _side_of_line(point, p1, p2):
    """
    Producto vectorial 2D. Determina de qué lado de la línea p1→p2 está el punto.
      > 0  →  exterior (calle/escalones en la línea diagonal)
      < 0  →  interior (tienda)
      = 0  →  sobre la línea
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return dx * (point[1] - p1[1]) - dy * (point[0] - p1[0])


def crossed_line_diagonal(prev_point, curr_point, line):
    """
    Cruce diagonal: persona viene de la derecha hacia el interior.
    Válido cuando pasa del lado exterior (cross > 0) al interior (cross <= 0).
    """
    p1, p2 = line
    prev_side = _side_of_line(prev_point, p1, p2)
    curr_side = _side_of_line(curr_point, p1, p2)
    return prev_side > 0 and curr_side <= 0


def point_in_polygon(point, polygon):
    """Retorna True si el punto está dentro o sobre el borde del polígono."""
    return cv2.pointPolygonTest(polygon, (float(point[0]), float(point[1])), False) >= 0


# ---------------------------------------------------------------------------
# DIBUJO
# ---------------------------------------------------------------------------

def draw_zone(frame, polygon, line_h, line_d):
    """Dibuja el polígono y las dos líneas de cruce sobre el frame."""
    cv2.polylines(frame, [polygon], isClosed=True, color=(0, 120, 255), thickness=2)

    # Línea horizontal (amarillo)
    cv2.line(frame, line_h[0], line_h[1], (0, 255, 255), 2)
    cv2.circle(frame, line_h[0], 5, (0, 255, 255), -1)
    cv2.circle(frame, line_h[1], 5, (0, 255, 255), -1)

    # Línea diagonal (verde)
    cv2.line(frame, line_d[0], line_d[1], (0, 255, 0), 2)
    cv2.circle(frame, line_d[0], 5, (0, 255, 0), -1)
    cv2.circle(frame, line_d[1], 5, (0, 255, 0), -1)
