"""
Re-run the trained model on the held-out JaalTaka test notes and save every
number the paper's figures need (journal/IEEE/scripts/predictions.npz).

    venv/Scripts/python journal/IEEE/scripts/run_inference.py

Uses the same per-note split (seed 42) and evaluation transform as train_ai.py,
so the per-photo / per-note metrics match models/metrics.json.
"""
import os
import sys
import time

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)

import numpy as np
import torch
from torch.utils.data import DataLoader

from model_arch import TakaAuthNet, eval_transform
from train_ai import NoteDataset, collect, split_by_note

OUT = os.path.join(os.path.dirname(__file__), "predictions.npz")


@torch.no_grad()
def run(model, items, mask=None):
    loader = DataLoader(NoteDataset(items, eval_transform(), mask), batch_size=32, num_workers=0)
    probs, embs = [], []
    for x, _ in loader:
        logits, emb = model(x, return_embedding=True)
        probs.append(torch.softmax(logits, 1)[:, 1])
        embs.append(emb)
    return torch.cat(probs).numpy(), torch.cat(embs).numpy()


def ood_ratio(emb, ood):
    mu, comps, var = ood["mean"].numpy(), ood["components"].numpy(), ood["var"].numpy()
    d = emb - mu
    z = d @ comps.T
    maha = (z ** 2 / var).sum(1)
    resid = ((d - z @ comps) ** 2).sum(1)
    return np.maximum(maha / ood["maha_thr"], resid / ood["resid_thr"])


def main():
    torch.set_num_threads(max(1, (os.cpu_count() or 2) // 2))
    ckpt = torch.load(os.path.join(ROOT, "models", "taka_authenticator.pth"), map_location="cpu", weights_only=False)
    model = TakaAuthNet(pretrained=False)
    model.load_state_dict(ckpt["state_dict"])
    model.eval()

    items = collect(os.path.join(ROOT, "data", "jaaltaka"))
    parts = split_by_note(items, seed=42)
    test, val = parts["test"], parts["val"]
    assert sorted({i[2] for i in test}) == ckpt["test_notes"], "split differs from the trained model"

    t0 = time.time()
    p, emb = run(model, test)
    print(f"test: {len(test)} photos in {time.time() - t0:.0f}s", flush=True)
    p_center, _ = run(model, test, "center_hidden")
    p_border, _ = run(model, test, "border_hidden")
    _, val_emb = run(model, val)

    # single-image latency (batch of 1, CPU), median of 30 runs
    x = eval_transform()(__import__("PIL.Image", fromlist=["Image"]).open(test[0][0]).convert("RGB"))[None]
    lat = []
    for _ in range(35):
        t = time.perf_counter(); model(x); lat.append(time.perf_counter() - t)

    n_params = sum(q.numel() for q in model.parameters())
    np.savez(
        OUT,
        paths=np.array([os.path.relpath(i[0], ROOT) for i in test]),
        labels=np.array([i[1] for i in test]),
        notes=np.array([i[2] for i in test]),
        views=np.array([i[3] for i in test]),
        p=p, p_center=p_center, p_border=p_border,
        ood_test=ood_ratio(emb, ckpt["ood"]), ood_val=ood_ratio(val_emb, ckpt["ood"]),
        latency_ms=np.array(lat[5:]) * 1000, n_params=n_params,
        counts=np.array([[len(v), len({i[2] for i in v}), sum(i[1] == 1 for i in v), sum(i[1] == 0 for i in v)]
                         for v in (parts["train"], parts["val"], parts["test"])]),
    )
    print("saved", OUT, "params", n_params, "latency ms", np.median(lat[5:]) * 1000)


if __name__ == "__main__":
    main()
