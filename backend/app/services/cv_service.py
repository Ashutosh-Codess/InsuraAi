"""
Vehicle damage assessment for motor claims.

Falls back to an OpenCV edge-density heuristic (more edge texture in a
photo usually means more visible damage) when no trained model is
present. If a trained model gets added later at models/damage_model.h5,
it's picked up automatically - see load_damage_model().
"""
import os

import cv2
import numpy as np

MODEL_PATH = os.getenv("DAMAGE_MODEL_PATH", "models/damage_model.h5")


def load_damage_model():
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        import tensorflow as tf

        return tf.keras.models.load_model(MODEL_PATH)
    except Exception:
        return None


def _edge_density(image: np.ndarray) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    ratio = np.count_nonzero(edges) / edges.size
    return min(ratio / 0.15, 1.0)


def assess_damage(image_path: str) -> dict:
    image = cv2.imread(image_path)
    if image is None:
        return {"damage_score": 0.0, "method": "none", "reason": "could not read image"}

    model = load_damage_model()
    if model is not None:
        resized = cv2.resize(image, (128, 128))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB).astype("float32") / 255.0
        score = float(model.predict(np.expand_dims(rgb, axis=0), verbose=0)[0][0])
        return {"damage_score": round(score, 2), "method": "trained_model"}

    score = _edge_density(image)
    return {"damage_score": round(score, 2), "method": "opencv_edge_heuristic"}
