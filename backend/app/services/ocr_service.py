"""
Document processing for claim/KYC uploads.

Note: the tech stack only lists OpenCV + TensorFlow for vision, no OCR
engine like Tesseract. So this doesn't do full text extraction - it does
what OpenCV can actually do on its own: check whether an uploaded document
image is even readable (blur/brightness check) before it goes further in
the pipeline. Full text extraction would need an OCR engine added to the
stack, which isn't in the doc.
"""
import cv2
import numpy as np

BLUR_THRESHOLD = 100.0


def check_document_quality(image_path: str) -> dict:
    image = cv2.imread(image_path)
    if image is None:
        return {"readable": False, "reason": "file could not be opened as an image"}

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    brightness = np.mean(gray)

    issues = []
    if blur_score < BLUR_THRESHOLD:
        issues.append("image too blurry")
    if brightness < 40:
        issues.append("image too dark")
    if brightness > 220:
        issues.append("image overexposed")

    return {
        "readable": len(issues) == 0,
        "blur_score": round(float(blur_score), 1),
        "brightness": round(float(brightness), 1),
        "issues": issues,
    }
