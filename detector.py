import cv2
import numpy as np
import pytesseract
from PIL import Image
import time

def detect_lines(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=50, maxLineGap=10)
    line_img = image.copy()
    count = 0
    if lines is not None:
        count = len(lines)
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(line_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return line_img, count

def detect_faces(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    face_img = image.copy()
    for (x, y, w, h) in faces:
        cv2.rectangle(face_img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    return face_img, len(faces)

def run_ocr(image):
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        text = pytesseract.image_to_string(thresh)
        return text.strip()
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""

def analyze_currency(image_bytes, threshold=8):
    # Decode image
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        return None, "Invalid image format"

    # Preprocessing
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Analyses
    line_img, line_count = detect_lines(image)
    face_img, face_count = detect_faces(image)
    ocr_text = run_ocr(image)
    
    # Results Calculation
    score = 0
    feature_list = []
    
    if face_count > 0: 
        score += 4
        feature_list.append({"name": "Portrait Recognition", "status": "PASS", "val": f"{face_count} detected"})
    else:
        feature_list.append({"name": "Portrait Recognition", "status": "FAIL", "val": "None"})
        
    if line_count > 5: 
        score += 4
        feature_list.append({"name": "Structural Patterns", "status": "PASS", "val": f"{line_count} lines"})
    else:
        feature_list.append({"name": "Structural Patterns", "status": "FAIL", "val": f"{line_count} lines"})
        
    if len(ocr_text) > 5: 
        score += 4
        feature_list.append({"name": "Print Authenticity", "status": "PASS", "val": "Verified"})
    else:
        feature_list.append({"name": "Print Authenticity", "status": "FAIL", "val": "Inconclusive"})

    is_real = score >= threshold
    confidence = (score / 12) * 100

    # Convert images to base64 for frontend
    def to_base64(img):
        _, buffer = cv2.imencode('.jpg', img)
        import base64
        return base64.b64encode(buffer).decode('utf-8')

    results = {
        "is_real": bool(is_real),
        "score": score,
        "confidence": confidence,
        "features": feature_list,
        "ocr_text": ocr_text,
        "visuals": {
            "original": to_base64(image),
            "edges": to_base64(cv2.Canny(gray, 100, 200)),
            "hough": to_base64(line_img),
            "faces": to_base64(face_img)
        }
    }
    
    return results, None
