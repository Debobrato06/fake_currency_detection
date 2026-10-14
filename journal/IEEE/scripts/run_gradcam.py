"""
Save Grad-CAM overlays for a few held-out test notes (needs predictions.npz).

    venv/Scripts/python journal/IEEE/scripts/run_gradcam.py

Writes journal/IEEE/scripts/gradcam/<note>_<view>_{img,cam}.png and picks.txt.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)

import cv2
import numpy as np
import torch
from PIL import Image

from detector import _gradcam
from model_arch import IMG_SIZE, TakaAuthNet, eval_transform

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "gradcam")


def crop(path):
    """Same geometry as eval_transform: resize short side to 1.15*IMG_SIZE, centre crop."""
    im = Image.open(path).convert("RGB")
    s = int(IMG_SIZE * 1.15) / min(im.size)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.BILINEAR)
    l, t = (im.width - IMG_SIZE) // 2, (im.height - IMG_SIZE) // 2
    return np.array(im.crop((l, t, l + IMG_SIZE, t + IMG_SIZE)))


def main():
    os.makedirs(OUT, exist_ok=True)
    d = np.load(os.path.join(HERE, "predictions.npz"))
    ckpt = torch.load(os.path.join(ROOT, "models", "taka_authenticator.pth"), map_location="cpu", weights_only=False)
    model = TakaAuthNet(pretrained=False)
    model.load_state_dict(ckpt["state_dict"])
    model.eval()

    notes = sorted(set(d["notes"]))
    mean_p = {n: d["p"][d["notes"] == n].mean() for n in notes}
    label = {n: int(d["labels"][d["notes"] == n][0]) for n in notes}
    # confident correct genuine / counterfeit notes, and the worst misclassified note
    real_ok = max((n for n in notes if label[n] == 1), key=lambda n: mean_p[n])
    fake_ok = min((n for n in notes if label[n] == 0), key=lambda n: mean_p[n])
    wrong = [n for n in notes if (mean_p[n] >= 0.5) != (label[n] == 1)]
    wrong = max(wrong, key=lambda n: abs(mean_p[n] - label[n])) if wrong else None
    picks = [real_ok, fake_ok] + ([wrong] if wrong else [])

    tf = eval_transform()
    with open(os.path.join(OUT, "picks.txt"), "w") as f:
        for n in picks:
            idx = np.where(d["notes"] == n)[0]
            for i in idx[:6]:
                path = os.path.join(ROOT, str(d["paths"][i]))
                x = tf(Image.open(path).convert("RGB"))[None]
                p = float(d["p"][i])
                cam = _gradcam(model, x, int(p >= 0.5))
                img = crop(path)
                cam = cv2.resize(cam, (IMG_SIZE, IMG_SIZE))
                heat = cv2.applyColorMap((cam * 255).astype(np.uint8), cv2.COLORMAP_JET)
                over = cv2.addWeighted(cv2.cvtColor(img, cv2.COLOR_RGB2BGR), 0.55, heat, 0.45, 0)
                v = int(d["views"][i])
                cv2.imwrite(os.path.join(OUT, f"{n}_{v}_img.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
                cv2.imwrite(os.path.join(OUT, f"{n}_{v}_cam.png"), over)
                f.write(f"{n}\t{v}\t{label[n]}\t{p:.4f}\t{mean_p[n]:.4f}\n")
    print("picked", picks)


if __name__ == "__main__":
    main()
