"""
Frozen ImageNet EfficientNet-B0 features for every JaalTaka photo, used for
(1) baselines (1-NN and logistic-regression probe, no fine-tuning) and
(2) a near-duplicate / leakage analysis between test and training notes.

    venv/Scripts/python journal/Springer/scripts/run_baselines.py

Writes journal/Springer/scripts/baselines.json and frozen_feats.npz.
"""
import json
import os
import sys

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from torch.utils.data import DataLoader

from model_arch import TakaAuthNet, eval_transform
from train_ai import NoteDataset, collect, split_by_note

HERE = os.path.dirname(__file__)


@torch.no_grad()
def feats(model, items):
    out = []
    for x, _ in DataLoader(NoteDataset(items, eval_transform()), batch_size=32, num_workers=0):
        out.append(model.embed(x))
    return torch.nn.functional.normalize(torch.cat(out), dim=1).numpy()


def note_mean(items, f):
    keys = sorted({i[2] for i in items})
    pos = {k: [j for j, i in enumerate(items) if i[2] == k] for k in keys}
    m = np.stack([f[pos[k]].mean(0) for k in keys])
    m /= np.linalg.norm(m, axis=1, keepdims=True)
    lab = np.array([items[pos[k][0]][1] for k in keys])
    return keys, m, lab


def scores(y, s, thr=0.5):
    pr = s >= thr
    return {"accuracy": float(np.mean(pr == y)), "auc": float(roc_auc_score(y, s)),
            "fake_detection": float(np.mean(~pr[y == 0])), "genuine_acceptance": float(np.mean(pr[y == 1]))}


def main():
    torch.set_num_threads(max(1, (os.cpu_count() or 2) // 2))
    model = TakaAuthNet(pretrained=True).eval()  # ImageNet weights only, no fine-tuning
    parts = split_by_note(collect(os.path.join(ROOT, "data", "jaaltaka")), seed=42)
    F = {k: feats(model, v) for k, v in parts.items()}
    print("features done", flush=True)
    np.savez(os.path.join(HERE, "frozen_feats.npz"), **F)

    ytr = np.array([i[1] for i in parts["train"]]); yte = np.array([i[1] for i in parts["test"]])
    res = {}

    # baseline 1: 1-nearest-neighbour (cosine) on frozen features, per photo and per note
    sim = F["test"] @ F["train"].T
    nn1 = ytr[sim.argmax(1)].astype(float)
    res["knn1_per_photo"] = scores(yte, nn1)
    tk, tm, tl = note_mean(parts["test"], F["test"])
    rk, rm, rl = note_mean(parts["train"], F["train"])
    nsim = tm @ rm.T
    res["knn1_per_note"] = scores(tl, rl[nsim.argmax(1)].astype(float))

    # baseline 2: linear probe (logistic regression) on frozen features
    clf = LogisticRegression(C=1.0, max_iter=3000, class_weight="balanced").fit(F["train"], ytr)
    pp = clf.predict_proba(F["test"])[:, 1]
    res["linear_probe_per_photo"] = scores(yte, pp)
    pn = np.array([pp[[j for j, i in enumerate(parts["test"]) if i[2] == k]].mean() for k in tk])
    res["linear_probe_per_note"] = scores(tl, pn)

    # near-duplicate analysis: for each test note, highest cosine similarity to a training
    # note of the same class vs. of the other class, and to other test notes (reference)
    same = np.array([nsim[i, rl == tl[i]].max() for i in range(len(tk))])
    other = np.array([nsim[i, rl != tl[i]].max() for i in range(len(tk))])
    vk, vm, vl = note_mean(parts["val"], F["val"])
    res["near_duplicate"] = {
        "test_notes": tk, "label": tl.tolist(), "nn_same_class": same.tolist(), "nn_other_class": other.tolist(),
        "nn_train_index": [rk[np.where(rl == tl[i])[0][nsim[i, rl == tl[i]].argmax()]] for i in range(len(tk))],
    }
    for c, name in [(0, "fake"), (1, "real")]:
        m = tl == c
        res[f"nn_same_class_median_{name}"] = float(np.median(same[m]))
        res[f"nn_other_class_median_{name}"] = float(np.median(other[m]))
        for t in (0.95, 0.97, 0.98):
            res[f"frac_{name}_nn_above_{t}"] = float(np.mean(same[m] > t))
    with open(os.path.join(HERE, "baselines.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "near_duplicate"}, indent=1))


if __name__ == "__main__":
    main()
