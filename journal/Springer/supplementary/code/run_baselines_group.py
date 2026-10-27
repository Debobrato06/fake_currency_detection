"""
Frozen-feature baselines (1-NN, linear probe) on the GROUP-aware split
(train_ai.split_by_group: duplicate groups kept together, label-conflict groups dropped).
Reuses the cached features of run_baselines.py (frozen_feats.npz), so no network pass is needed.

    venv/Scripts/python journal/Springer/scripts/run_baselines_group.py

Writes journal/Springer/scripts/baselines_group.json.
"""
import json
import os
import sys

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)

import numpy as np
from sklearn.linear_model import LogisticRegression

from run_baselines import note_mean, scores
from train_ai import collect, split_by_group, split_by_note

HERE = os.path.dirname(__file__)


def main():
    items = collect(os.path.join(ROOT, "data", "jaaltaka"))
    cached = np.load(os.path.join(HERE, "frozen_feats.npz"))
    old = split_by_note(items, seed=42)
    feat = {}
    for k, v in old.items():
        for it, f in zip(v, cached[k]):
            feat[it[0]] = f
    with open(os.path.join(HERE, "duplicates.json")) as f:
        groups = json.load(f)["groups"]["all"]
    parts, _ = split_by_group(items, groups, seed=42)
    F = {k: np.stack([feat[it[0]] for it in v]) for k, v in parts.items()}
    ytr = np.array([i[1] for i in parts["train"]]); yte = np.array([i[1] for i in parts["test"]])

    res = {}
    res["knn1_per_photo"] = scores(yte, ytr[(F["test"] @ F["train"].T).argmax(1)].astype(float))
    tk, tm, tl = note_mean(parts["test"], F["test"])
    _, rm, rl = note_mean(parts["train"], F["train"])
    res["knn1_per_note"] = scores(tl, rl[(tm @ rm.T).argmax(1)].astype(float))

    clf = LogisticRegression(C=1.0, max_iter=3000, class_weight="balanced").fit(F["train"], ytr)
    pp = clf.predict_proba(F["test"])[:, 1]
    res["linear_probe_per_photo"] = scores(yte, pp)
    pn = np.array([pp[[j for j, i in enumerate(parts["test"]) if i[2] == k]].mean() for k in tk])
    res["linear_probe_per_note"] = scores(tl, pn)
    res["test_notes"] = len(tk)

    with open(os.path.join(HERE, "baselines_group.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
