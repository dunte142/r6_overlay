"""
Detector visual para la fase de drones: reconoce en el feed de pantalla
elementos categorizables que el juego YA muestra (silueta de operador
detectado por el drone, ícono de gadget, trampa, refuerzo).

IMPORTANTE (ver conversación): esto SOLO funciona bien si entrenás tu propio
modelo con capturas tuyas del juego, porque no existe un dataset público de
iconos de R6. Esto es la parte de mayor trabajo real del proyecto:

  1. Jugá partidas grabando tu pantalla (OBS) durante fases de droneo.
  2. Extraé frames donde aparecen los iconos de detección.
  3. Etiquetalos (ej. con labelImg o Roboflow) por categoría:
     "operador", "gadget", "trampa", "refuerzo".
  4. Entrená un YOLOv8 chico (nano/small) con ese dataset:
       from ultralytics import YOLO
       model = YOLO("yolov8n.pt")
       model.train(data="tu_dataset.yaml", epochs=50, imgsz=640)
  5. Reemplazá MODEL_PATH abajo por el .pt resultante.

Este archivo deja el pipeline listo para enchufar ese modelo una vez entrenado.
"""

import numpy as np

MODEL_PATH = "models/r6_drone_detector.pt"  # tu modelo entrenado, una vez que exista

CLASS_NAMES = ["operador", "gadget", "trampa", "refuerzo"]


class DroneDetector:
    def __init__(self, model_path: str = MODEL_PATH, confidence: float = 0.5):
        self.confidence = confidence
        self.model = None
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
        except Exception as e:
            print(f"[DroneDetector] Modelo no cargado ({e}). "
                  f"Corriendo en modo stub -- no va a detectar nada real "
                  f"hasta que entrenes y coloques tu modelo en {model_path}.")

    def detect(self, frame_bgra: np.ndarray) -> list[dict]:
        """
        Devuelve una lista de detecciones: [{"category": str, "label": str, "confidence": float}, ...]
        """
        if self.model is None:
            return []  # stub: sin modelo entrenado, no inventa detecciones

        frame_bgr = frame_bgra[:, :, :3]
        results = self.model.predict(frame_bgr, verbose=False, conf=self.confidence)

        findings = []
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                category = CLASS_NAMES[cls_id] if cls_id < len(CLASS_NAMES) else "desconocido"
                findings.append({
                    "category": category,
                    "label": self.model.names.get(cls_id, "objeto"),
                    "confidence": float(box.conf[0]),
                })
        return findings
