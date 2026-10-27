"""
Re-score the trained model and the frozen-feature baselines on the
duplicate-free part of the test set (needs predictions.npz, frozen_feats.npz,
duplicates.json).

    venv/Scripts/python journal/Springer/scripts/analyze_leakage.py

A test note is "clean" when no other note of its duplicate group (pixel NCC > 0.98,
see find_duplicates.py) is in the training or validation split.
Writes scripts/leakage.json.
"""
import json
import math
import os
import sys

import numpy as np
from sklearn.linear_model import LogisticRegression

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
from train_ai import collect, split_by_note  # noqa: E402


def auc(y, s):
    pos, neg = s[y == 1], s[y == 0]
    return float(((pos[:, None] > neg).sum() + 0.5 * (pos[:, None] == neg).sum()) / (len(pos) * len(neg)))


def wilson(k, n, z=1.96):
    ph = k / n
    c = (ph + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [c - h, c + h]


def score(y, s):
    pr = s >= 0.5
    k = int(np.sum(pr == y))
    return {"n": int(len(y)), "n_fake": int(np.sum(y == 0)), "n_real": int(np.sum(y == 1)),
            "accuracy": k / len(y), "acc_ci95": wilson(k, len(y)), "auc": auc(y, s),
            "fake_detection": float(np.mean(~pr[y == 0])), "genuine_acceptance": float(np.mean(pr[y == 1])),
            "errors": int(len(y) - k)}


def main():
    parts = split_by_note(collect(os.path.join(ROOT, "data", "jaaltaka")), seed=42)
    split_of = {i[2]: s for s, v in parts.items() for i in v}
    dup = json.load(open(os.path.join(HERE, "duplicates.json")))
    group_of = {k: gi for gi, g in enumerate(dup["groups"]["all"]) for k in g}
    groups = dup["groups"]["all"]
    mixed = {k for g in dup["groups"]["mixed_label_groups"] for k in g}

    d = np.load(os.path.join(HERE, "predictions.npz"))
    notes, y, p = d["notes"], d["labels"], d["p"]
    ids = sorted(set(notes))
    yn = np.array([y[notes == n][0] for n in ids])
    pn = np.array([p[notes == n].mean() for n in ids])
    leaked = np.array([any(split_of[k] != "test" for k in groups[group_of[n]]) for n in ids])
    in_mixed = np.array([n in mixed for n in ids])

    # frozen-feature baselines, scored per note
    F = np.load(os.path.join(HERE, "frozen_feats.npz"))
    ytr = np.array([i[1] for i in parts["train"]])
    te_notes = np.array([i[2] for i in parts["test"]])
    knn = ytr[(F["test"] @ F["train"].T).argmax(1)].astype(float)
    lp = LogisticRegression(C=1.0, max_iter=3000, class_weight="balanced").fit(F["train"], ytr).predict_proba(F["test"])[:, 1]
    base = {name: np.array([s[te_notes == n].mean() for n in ids]) for name, s in (("knn1", knn), ("linear_probe", lp))}

    out = {"definition": "clean = no member of the note's duplicate group (NCC>0.98) in train or val",
           "test_notes_with_copy_in_train_or_val": int(leaked.sum()),
           "test_notes_in_mixed_label_groups": int(in_mixed.sum()),
           "test_errors": [{"note": n, "p": float(q), "group": groups[group_of[n]]}
                           for n, q, l in zip(ids, pn, yn) if (q >= 0.5) != l]}
    for subset, m in (("all", np.ones(len(ids), bool)), ("leaked", leaked), ("clean", ~leaked),
                      ("all_minus_mixed", ~in_mixed)):
        out[subset] = {"model": score(yn[m], pn[m])}
        for name, s in base.items():
            out[subset][name] = score(yn[m], s[m])
    with open(os.path.join(HERE, "leakage.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items()}, indent=1)[:4000])


if __name__ == "__main__":
    main()
