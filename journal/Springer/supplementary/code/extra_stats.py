"""
Statistics requested by the manuscript audit (needs predictions.npz, frozen_feats.npz,
duplicates.json and the JaalTaka images):

  1. group-level (cluster) bootstrap 95% CIs, resampling duplicate groups instead of
     treating correlated notes / photographs as independent;
  2. exact McNemar tests, fine-tuned model vs. each frozen-feature baseline (per note);
  3. sensitivity of the duplicate audit to the NCC threshold.

    venv/Scripts/python journal/Springer/scripts/extra_stats.py

Writes scripts/extra_stats.json.
"""
import json
import os
import sys
from collections import defaultdict
from math import comb

import numpy as np
from sklearn.linear_model import LogisticRegression

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
from train_ai import collect, split_by_note  # noqa: E402
from find_duplicates import S, norm, thumb  # noqa: E402


def cluster_bootstrap(correct, cluster, n_boot=10000, seed=0):
    """95% percentile CI of accuracy, resampling clusters with replacement."""
    rng = np.random.default_rng(seed)
    ids = np.unique(cluster)
    k = np.array([correct[cluster == c].sum() for c in ids], float)
    n = np.array([(cluster == c).sum() for c in ids], float)
    draw = rng.integers(0, len(ids), (n_boot, len(ids)))
    acc = k[draw].sum(1) / n[draw].sum(1)
    return [float(np.percentile(acc, 2.5)), float(np.percentile(acc, 97.5))]


def mcnemar_exact(a_correct, b_correct):
    """Two-sided exact McNemar (binomial) test on the discordant pairs."""
    b = int(np.sum(a_correct & ~b_correct))
    c = int(np.sum(~a_correct & b_correct))
    n = b + c
    if n == 0:
        return {"a_only_correct": b, "b_only_correct": c, "p": 1.0}
    p = 2 * sum(comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n
    return {"a_only_correct": b, "b_only_correct": c, "p": min(1.0, p)}


def components(sim, thr):
    parent = list(range(len(sim)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for a, b in zip(*np.where(sim > thr)):
        parent[find(a)] = find(b)
    groups = defaultdict(list)
    for i in range(len(sim)):
        groups[find(i)].append(i)
    return list(groups.values())


def main():
    items = collect(os.path.join(ROOT, "data", "jaaltaka"))
    parts = split_by_note(items, seed=42)
    split_of = {i[2]: s for s, v in parts.items() for i in v}
    dup = json.load(open(os.path.join(HERE, "duplicates.json")))
    group_of = {k: gi for gi, g in enumerate(dup["groups"]["all"]) for k in g}

    d = np.load(os.path.join(HERE, "predictions.npz"))
    notes, y, p = d["notes"], d["labels"], d["p"]
    ids = sorted(set(notes))
    yn = np.array([y[notes == n][0] for n in ids])
    pn = np.array([p[notes == n].mean() for n in ids])
    gn = np.array([group_of[n] for n in ids])
    gp = np.array([group_of[n] for n in notes])

    F = np.load(os.path.join(HERE, "frozen_feats.npz"))
    ytr = np.array([i[1] for i in parts["train"]])
    te_notes = np.array([i[2] for i in parts["test"]])
    knn = ytr[(F["test"] @ F["train"].T).argmax(1)].astype(float)
    lp = LogisticRegression(C=1.0, max_iter=3000, class_weight="balanced").fit(F["train"], ytr).predict_proba(F["test"])[:, 1]
    base = {name: np.array([s[te_notes == n].mean() for n in ids]) for name, s in (("knn1", knn), ("linear_probe", lp))}

    ok_note = (pn >= 0.5) == yn
    ok_photo = (p >= 0.5) == y
    out = {
        "bootstrap": {
            "n_boot": 10000,
            "per_note_test_groups": int(len(np.unique(gn))),
            "per_note_accuracy": float(ok_note.mean()),
            "per_note_ci95_group_bootstrap": cluster_bootstrap(ok_note, gn),
            "per_photo_accuracy": float(ok_photo.mean()),
            "per_photo_ci95_group_bootstrap": cluster_bootstrap(ok_photo, gp),
        },
        "mcnemar_per_note": {name: mcnemar_exact(ok_note, (s >= 0.5) == yn) for name, s in base.items()},
    }

    # NCC-threshold sensitivity of the audit (same similarity as find_duplicates.py)
    keys = sorted({it[2] for it in items})
    kidx = {k: i for i, k in enumerate(keys)}
    T = np.zeros((len(keys), 6, S, S), np.float32)
    for it in items:
        T[kidx[it[2]], it[3] - 1] = thumb(it[0])
    variants = [norm(T), norm(T[..., ::-1]), norm(T[..., ::-1, :]), norm(T[..., ::-1, ::-1])]
    X = variants[0].reshape(len(keys), 6, -1)
    sim = np.full((len(keys), len(keys)), -1.0, np.float32)
    for V in variants:
        sim = np.maximum(sim, np.einsum("avd,bvd->ab", V.reshape(len(keys), 6, -1), X) / 6)
    np.fill_diagonal(sim, -1)
    sens = {}
    for thr in (0.90, 0.95, 0.97, 0.98, 0.99):
        groups = [[keys[i] for i in g] for g in components(sim, thr)]
        gof = {k: gi for gi, g in enumerate(groups) for k in g}
        test = [k for k in keys if split_of[k] == "test"]
        leaked = sum(any(split_of[m] != "test" for m in groups[gof[k]]) for k in test)
        sens[str(thr)] = {
            "groups": len(groups),
            "mixed_label_groups": sum(len({k.split("_")[0] for k in g}) > 1 for g in groups),
            "test_notes_with_copy": int(leaked),
        }
    out["ncc_threshold_sensitivity"] = sens

    with open(os.path.join(HERE, "extra_stats.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
