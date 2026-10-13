"""
Taka banknote authentication: genuine vs counterfeit.

Pipeline for each uploaded photo
  1. Trained EfficientNet-B0 classifier (train_ai.py, JaalTaka dataset) -> P(real)
     with light test-time augmentation (centre crop + full frame).
  2. Out-of-distribution gate: if the photo does not look like the Tk 500 / Tk 1000
     notes the model was trained on, no verdict is given (instead of guessing).
  3. Grad-CAM heatmap showing which regions drove the decision.
Several photos of the same note (e.g. front, back, against light) can be passed;
their probabilities are averaged, which is more reliable than a single photo.
"""
import base64
import os
import threading

import cv2
import numpy as np
from PIL import Image

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "taka_authenticator.pth")
SUPPORTED_NOTES = "Tk 500 and Tk 1000"
# Out-of-distribution limit: 1.0 = the 99.5th percentile of validation photos. Calibrated on the
# held-out test notes (0.3% of genuine-dataset photos rejected) and on other denominations
# (about 95% rejected).
OOD_LIMIT = 1.0
# Blank / featureless images (Laplacian variance at 512x512). Lowest value seen on test photos: 56.
MIN_TEXTURE = 30.0

_lock = threading.Lock()
_bundle = None  # (model, ckpt, device, transforms)
_load_error = None


def load_model():
    """Load the trained model once. Returns (bundle, error_message)."""
    global _bundle, _load_error
    with _lock:
        if _bundle is not None or _load_error is not None:
            return _bundle, _load_error
        if not os.path.exists(MODEL_PATH):
            _load_error = ("Trained model not found (models/taka_authenticator.pth). "
                           "Run: python download_dataset.py  then  python train_ai.py")
            return None, _load_error
        try:
            import torch
            from torchvision import transforms
            from model_arch import MEAN, STD, TakaAuthNet

            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            ckpt = torch.load(MODEL_PATH, map_location="cpu", weights_only=False)
            model = TakaAuthNet(pretrained=False)
            model.load_state_dict(ckpt["state_dict"])
            model.to(device).eval()
            size = ckpt["img_size"]
            norm = [transforms.ToTensor(), transforms.Normalize(MEAN, STD)]
            tfs = [
                transforms.Compose([transforms.Resize(int(size * 1.15)), transforms.CenterCrop(size)] + norm),
                transforms.Compose([transforms.Resize((size, size))] + norm),
            ]
            _bundle = (model, ckpt, device, tfs)
        except Exception as e:  # torch missing, corrupt file, ...
            _load_error = f"Could not load AI model: {type(e).__name__}: {e}"
        return _bundle, _load_error


def model_info():
    bundle, err = load_model()
    if err:
        return {"ready": False, "error": err}
    return {"ready": True, "metrics": bundle[1].get("metrics", {}), "supported_notes": SUPPORTED_NOTES}


def _ood_scores(emb, ood):
    mu, comps, var = ood["mean"].numpy(), ood["components"].numpy(), ood["var"].numpy()
    d = emb - mu
    z = d @ comps.T
    maha = float((z ** 2 / var).sum())
    resid = float(((d - z @ comps) ** 2).sum())
    return maha, resid


def _gradcam(model, x, target):
    import torch
    x = x.clone().requires_grad_(False)
    feats = model.features(x)
    feats.retain_grad()
    logits = model.head(torch.flatten(model.pool(feats), 1))
    model.zero_grad()
    logits[0, target].backward()
    w = feats.grad.mean(dim=(2, 3), keepdim=True)
    cam = torch.relu((w * feats).sum(1)).squeeze(0).detach().cpu().numpy()
    return cam / (cam.max() + 1e-8)


def _to_b64(img_bgr, max_side=900):
    h, w = img_bgr.shape[:2]
    s = min(1.0, max_side / max(h, w))
    if s < 1:
        img_bgr = cv2.resize(img_bgr, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    _, buf = cv2.imencode(".jpg", img_bgr, [cv2.IMWRITE_JPEG_QUALITY, 88])
    return base64.b64encode(buf).decode("utf-8")


def _edge_map(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(cv2.Canny(gray, 80, 180), cv2.COLOR_GRAY2BGR)


def analyze_image(image_bytes):
    """Analyse one photo. Returns (result_dict, error_message)."""
    import torch

    bundle, err = load_model()
    if err:
        return None, err
    model, ckpt, device, tfs = bundle

    img_bgr = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    if img_bgr is None:
        return None, "Invalid or unsupported image file"
    pil = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))

    batch = torch.stack([tf(pil) for tf in tfs]).to(device)
    with torch.no_grad():
        logits, emb = model(batch, return_embedding=True)
        p_real = float(torch.softmax(logits, 1)[:, 1].mean())
    maha, resid = _ood_scores(emb[0].cpu().numpy(), ckpt["ood"])
    ood = ckpt["ood"]
    # <= 1.0: looks like the banknote photos the model was trained on
    ood_ratio = max(maha / ood["maha_thr"], resid / ood["resid_thr"])
    gray = cv2.cvtColor(cv2.resize(img_bgr, (512, 512)), cv2.COLOR_BGR2GRAY)
    texture = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    in_dist = ood_ratio <= OOD_LIMIT and texture >= MIN_TEXTURE

    # Grad-CAM on the centre-crop view, projected back onto the full photo
    with torch.enable_grad():
        cam = _gradcam(model, batch[:1], int(p_real >= 0.5))
    h, w = img_bgr.shape[:2]
    side = min(h, w) / 1.15
    y0, x0 = int((h - side) / 2), int((w - side) / 2)
    cam_full = np.zeros((h, w), np.float32)
    cam_full[y0:y0 + int(side), x0:x0 + int(side)] = cv2.resize(cam, (int(side), int(side)))
    heat = cv2.applyColorMap((cam_full * 255).astype(np.uint8), cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(img_bgr, 0.55, heat, 0.45, 0)

    return {
        "real_probability": p_real,
        "in_distribution": bool(in_dist),
        "ood_ratio": round(float(ood_ratio), 2),
        "visuals": {
            "original": _to_b64(img_bgr),
            "gradcam": _to_b64(overlay),
            "heatmap": _to_b64(heat),  # pure heatmap layer, same size as original (UI blends it)
            "edges": _to_b64(_edge_map(img_bgr)),
        },
    }, None


def analyze_currency(images, threshold=0.7):
    """
    Analyse one or more photos of the SAME banknote.

    images    : bytes or list of bytes
    threshold : minimum P(real) to call the note GENUINE. Below 0.5 -> COUNTERFEIT,
                between 0.5 and threshold -> UNCERTAIN (check manually).
    Returns (result_dict, error_message).
    """
    if isinstance(images, (bytes, bytearray)):
        images = [images]
    per_image = []
    for b in images:
        r, err = analyze_image(b)
        if err:
            return None, err
        per_image.append(r)
    return summarize(per_image, threshold), None


def summarize(per_image, threshold=0.7):
    """Combine per-photo results (from analyze_image) into one verdict."""
    usable = [r for r in per_image if r["in_distribution"]]
    if not usable:
        verdict, p_real = "NOT_SUPPORTED", None
    else:
        p_real = float(np.mean([r["real_probability"] for r in usable]))
        verdict = "GENUINE" if p_real >= threshold else ("COUNTERFEIT" if p_real < 0.5 else "UNCERTAIN")

    messages = {
        "GENUINE": "The note looks genuine.",
        "COUNTERFEIT": "The note looks COUNTERFEIT. Do not accept it; verify at a bank.",
        "UNCERTAIN": "The model is not sure. Check watermark, security thread and raised print by hand, or add more photos.",
        "NOT_SUPPORTED": f"This photo does not look like a {SUPPORTED_NOTES} note the model was trained on. "
                         "Upload a clear, close photo of a Tk 500 or Tk 1000 note.",
    }
    if p_real is None:
        confidence = None
    else:
        confidence = round(100 * (p_real if p_real >= 0.5 else 1 - p_real), 1)

    return {
        "verdict": verdict,
        "is_real": verdict == "GENUINE",
        "real_probability": None if p_real is None else round(p_real, 4),
        "confidence": confidence,
        "message": messages[verdict],
        "threshold": threshold,
        "photos_used": len(usable),
        "photos_total": len(per_image),
        "supported_notes": SUPPORTED_NOTES,
        "per_image": [{
            "real_probability": round(r["real_probability"], 4),
            "in_distribution": r["in_distribution"],
            "ood_ratio": r["ood_ratio"],
            "visuals": r["visuals"],
        } for r in per_image],
    }
