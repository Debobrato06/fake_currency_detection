import cv2
import numpy as np
import pytesseract
from PIL import Image
import base64

# --- Safe AI Import Mechanism ---
AI_DISABLED = False
try:
    import torch
    import torch.nn.functional as F
    from model_arch import CurrencyForensicNet, get_anomaly_score
    
    # Initialize the AI Model (Forensic Intelligence)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = CurrencyForensicNet().to(device)
    model.eval() # Set to evaluation mode
except (ImportError, OSError, Exception) as e:
    AI_DISABLED = True
    print(f"Warning: AI core initialization failed ({type(e).__name__}). Falling back to CV-only mode.")
    print(f"Details: {e}")

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

def preprocess_for_ai(image):
    # Resize and normalize for Deep Learning Model
    img_resized = cv2.resize(image, (512, 512))
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    tensor = torch.from_numpy(img_rgb).permute(2, 0, 1).float() / 255.0
    return tensor.unsqueeze(0).to(device)

def analyze_currency_elite(image_bytes, strictness=12):
    """
    Elite Forensic Analysis: Hybrid CV + Deep Learning
    """
    global AI_DISABLED
    # 1. Decode & Load Image
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None: return None, "Invalid image"

    # 2. Deep Learning Anomaly Detection
    if not AI_DISABLED:
        try:
            with torch.no_grad():
                input_tensor = preprocess_for_ai(image)
                reconstructed, latent_space = model(input_tensor)
                
                # Calculate Anomaly Score (Reconstruction Error)
                anomaly_score = get_anomaly_score(input_tensor, reconstructed)
                
                # Simulate Attention Map
                attention_map = latent_space.mean(dim=1).squeeze().cpu().numpy()
                attention_map = (attention_map - attention_map.min()) / (attention_map.max() - attention_map.min() + 1e-8)
                attention_map = cv2.resize((attention_map * 255).astype(np.uint8), (512, 512))
                heatmap = cv2.applyColorMap(attention_map, cv2.COLORMAP_JET)
                recon_img = cv2.cvtColor((reconstructed.squeeze().permute(1,2,0).cpu().numpy() * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
                dl_score = max(0, 10 - (anomaly_score * 100))
        except Exception as e:
            AI_DISABLED = True
            print(f"AI Error: {e}")
            anomaly_score, dl_score = 0.0, 0.0
            heatmap = np.zeros((512, 512, 3), dtype=np.uint8)
            recon_img = np.zeros((512, 512, 3), dtype=np.uint8)
    else:
        anomaly_score, dl_score = 0.0, 0.0
        heatmap = np.zeros((512, 512, 3), dtype=np.uint8)
        recon_img = np.zeros((512, 512, 3), dtype=np.uint8)

    # 3. Structural CV Checks (Legacy Modules)
    line_img, line_count = detect_lines(image)
    face_img, face_count = detect_faces(image)
    ocr_text = run_ocr(image)

    # 4. Scoring Fusion
    # DL Score: Lower anomaly is better. Scale 0-10.
    
    cv_score = (4 if face_count > 0 else 0) + (4 if line_count > 5 else 0) + (2 if len(ocr_text) > 5 else 0)
    
    total_score = (dl_score * 0.6) + (cv_score * 1.0) # Weighted sum
    is_real = total_score >= (strictness / 2) # Normalizing threshold

    def to_base64(img):
        _, buffer = cv2.imencode('.jpg', img)
        return base64.b64encode(buffer).decode('utf-8')

    results = {
        "is_real": bool(is_real),
        "score": round(total_score, 1),
        "anomaly_score": round(anomaly_score, 4),
        "ai_confidence": round(dl_score * 10, 1),
        "ai_active": not AI_DISABLED,
        "features": [
            {"name": "Forensic Anomaly", "status": "OK" if dl_score > 5 else ("INITIALIZING" if AI_DISABLED else "HIGH"), "val": f"{round(anomaly_score, 4)}"},
            {"name": "Portrait Recognition", "status": "PASS" if face_count > 0 else "FAIL", "val": f"{face_count}"},
            {"name": "Structural Grid", "status": "PASS" if line_count > 5 else "FAIL", "val": f"{line_count}"}
        ],
        "visuals": {
            "original": to_base64(image),
            "ai_attention": to_base64(heatmap),
            "reconstruction": to_base64(recon_img),
            "cv_features": to_base64(line_img)
        }
    }

    return results, None
