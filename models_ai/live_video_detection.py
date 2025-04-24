import cv2
import requests
from ultralytics import YOLO
import time

# Configuración del modelo y API
MODEL_PATH = 'runs/detect/train13/weights/best.pt'
API_URL = 'http://127.0.0.1:8000/detection/visual/create/'  # O el endpoint que uses
API_TOKEN = 'TU_TOKEN_AQUI'  # 👈 Pega tu token aquí

# Cargar modelo entrenado
model = YOLO(MODEL_PATH)

# Abrir webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ No se pudo abrir la cámara.")
    exit()

print("🎥 Cámara iniciada. Presiona 'q' para salir.")

# Control de tiempo para evitar enviar muchas alertas
last_sent_time = 0
send_interval = 5  # segundos entre envíos

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ No se pudo capturar el frame.")
        break

    # Detección
    results = model(frame)
    annotated_frame = results[0].plot()

    # Mostrar ventana con resultados
    cv2.imshow("🧠 Detección en tiempo real", annotated_frame)

    # Revisar si hay detecciones de interés
    alert_detected = False
    detections_data = []

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]
            conf = float(box.conf[0])
            if label in ["person-on-scooter", "person-on-scooter-side-view"] and conf > 0.6:
                alert_detected = True
                print(f"⚠️ Alerta: {label} detectado con {conf:.2f} de confianza")
                # Guardamos datos para enviar a la API
                detections_data.append({
                    "label": label,
                    "confidence": round(conf, 2),
                    "bbox": box.xyxy[0].tolist()
                })

    # Enviar a la API si se detectó algo y ha pasado suficiente tiempo
    current_time = time.time()
    if alert_detected and (current_time - last_sent_time > send_interval):
        try:
            response = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {API_TOKEN}"
                },
                json={
                    "detections": detections_data,
                    "source": "cam_live"  # Puedes agregar más campos personalizados
                }
            )
            if response.status_code == 201:
                print("✅ Alerta enviada correctamente al backend.")
            else:
                print(f"⚠️ Error al enviar alerta: {response.status_code} - {response.text}")
            last_sent_time = current_time
        except Exception as e:
            print(f"❌ Error al conectarse al API: {e}")

    # Salir con tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cerrar recursos
cap.release()
cv2.destroyAllWindows()
