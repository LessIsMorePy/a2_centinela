from ultralytics import YOLO
import cv2
import time
import tracking_functions_people as tf
import admin
import alert

# ---------------------------------------------------------------------------
# MODELO Y CAPTURA
# ---------------------------------------------------------------------------

model = YOLO('yolov8n.pt')

cap = cv2.VideoCapture(
    f'rtsp://{admin.user}:{admin.pwd}@{admin.ip_a2_fv}/stream1',
    cv2.CAP_FFMPEG
)
# cap = cv2.VideoCapture('D:/Python/Código/arcos/people_detection/test_video/document_5003745291929651025.mp4')

if not cap.isOpened():
    exit()

cap.set(cv2.CAP_PROP_FPS, 14.25)

# ---------------------------------------------------------------------------
# ZONA, LÍNEAS Y ESTADO
# ---------------------------------------------------------------------------

polygon  = tf.get_zone_polygon()
line_h   = tf.get_crossing_line()           # horizontal  — entrada fondo
line_d   = tf.get_crossing_line_diagonal()  # diagonal    — entrada lateral
line_y   = line_h[0][1]

CROP_Y         = 300    # recorte superior — excluye el cielo y reduce carga CPU
ALERT_COOLDOWN = 3.0    # segundos mínimos entre alertas

detections      = []
frame_count     = 0
prev_positions  = {}    # {track_id: (rx, ry)}
entered_ids     = set() # IDs que ya dispararon alerta
last_alert_time = 0

# ---------------------------------------------------------------------------
# BUCLE PRINCIPAL
# ---------------------------------------------------------------------------

while cap.isOpened():
    ret, frame = cap.read()
    if not ret or cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if frame_count % 3 == 0:
        crop       = frame[CROP_Y:, :]
        detections = tf.get_person_detections(tf.tracking(model, crop))

    tf.draw_zone(frame, polygon, line_h, line_d)

    for track_id, (base_x, base_y), (bx1, by1, bx2, by2) in detections:

        # Traducir coordenadas del crop al frame completo
        rx  = int(base_x)
        ry  = int(base_y) + CROP_Y
        rx1, ry1 = int(bx1), int(by1) + CROP_Y
        rx2, ry2 = int(bx2), int(by2) + CROP_Y

        inside = tf.point_in_polygon((rx, ry), polygon)
        color  = (0, 255, 0) if inside else (100, 100, 100)

        cv2.rectangle(frame, (rx1, ry1), (rx2, ry2), color, 2)
        cv2.putText(frame, f"ID:{track_id}", (rx1, ry1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv2.circle(frame, (rx, ry), 4, (255, 255, 255), -1)

        if inside and track_id not in entered_ids:
            prev = prev_positions.get(track_id)
            if prev:
                entrada_detectada = (
                    tf.crossed_line(prev[1], ry, line_y)
                    or
                    tf.crossed_line_diagonal((prev[0], prev[1]), (rx, ry), line_d)
                )
                if entrada_detectada:
                    now = time.time()
                    entered_ids.add(track_id)
                    print(f"[ENTRADA] ID:{track_id} — {time.strftime('%H:%M:%S')}")
                    if now - last_alert_time >= ALERT_COOLDOWN:
                        alert.play_alert()
                        last_alert_time = now

        prev_positions[track_id] = (rx, ry)

    # h, w = frame.shape[:2]
    # cv2.imshow('Monitor Arcos', cv2.resize(frame, (int(w * 0.4), int(h * 0.4))))
    frame_count += 1

cap.release()
cv2.destroyAllWindows()
