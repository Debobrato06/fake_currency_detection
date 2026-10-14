"""
Pixel-level near-duplicate search between JaalTaka notes.

JaalTaka's authors enlarged the collection by augmentation (649 original notes
-> 1,390 notes), so some "different" notes are re-coloured / transformed copies
of the same six photographs. Two notes are compared with the mean, over the six
views, of the normalised cross-correlation (NCC) of 48x48 grey thumbnails
(brightness/contrast invariant; flips and 180-degree rotation are also tried).

    python journal/IEEE/scripts/find_duplicates.py     # numpy + pillow

Writes scripts/duplicates.json: for every val/test note, the best-matching
training note and its score.
"""
import json
import os
import re
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
S = 48


def thumb(path):
    a = np.asarray(Image.open(path).convert("L").resize((S, S), Image.BILINEAR), np.float32)
    return a


def norm(a):
    a = a - a.mean(axis=(-2, -1), keepdims=True)
    return a / (np.linalg.norm(a, axis=(-2, -1), keepdims=True) + 1e-6)


def main():
    # same split as train_ai.py, without importing torch
    from collections import defaultdict
    import random
    NOTE_RE = re.compile(r"note_(\d+)_(\d+)\.jpg$", re.I)
    items = []
    for label, cls in enumerate(["fake", "real"]):
        folder = os.path.join(ROOT, "data", "jaaltaka", cls)
        for f in sorted(os.listdir(folder)):
            m = NOTE_RE.search(f)
            if m:
                items.append((os.path.join(folder, f), label, f"{cls}_{m.group(1)}", int(m.group(2))))
    notes = defaultdict(list)
    for it in items:
        notes[(it[1], it[2])].append(it)
    rng = random.Random(42)
    part = {}
    for label in range(2):
        keys = sorted(k for k in notes if k[0] == label)
        rng.shuffle(keys)
        n_val, n_test = round(len(keys) * 0.15), round(len(keys) * 0.15)
        for i, k in enumerate(keys):
            part[k[1]] = "test" if i < n_test else ("val" if i < n_test + n_val else "train")

    keys = sorted({it[2] for it in items})
    kidx = {k: i for i, k in enumerate(keys)}
    T = np.zeros((len(keys), 6, S, S), np.float32)
    lab = np.zeros(len(keys), int)
    for n, it in enumerate(items):
        T[kidx[it[2]], it[3] - 1] = thumb(it[0])
        lab[kidx[it[2]]] = it[1]
        if n % 1000 == 0:
            print(n, "/", len(items), flush=True)
    variants = [norm(T), norm(T[..., ::-1]), norm(T[..., ::-1, :]), norm(T[..., ::-1, ::-1])]
    X = variants[0].reshape(len(keys), 6, -1)

    tr = np.array([part[k] == "train" for k in keys])
    out = {}
    for split in ("val", "test"):
        q = np.array([part[k] == split for k in keys])
        best = np.full(q.sum(), -1.0); arg = np.zeros(q.sum(), int)
        for V in variants:  # transformed query vs. original training notes
            Q = V[q].reshape(q.sum(), 6, -1)
            sim = np.einsum("avd,bvd->ab", Q, X[tr]) / 6
            b = sim.max(1); better = b > best
            best[better] = b[better]; arg[better] = sim.argmax(1)[better]
        tk = [k for k, f in zip(keys, q) if f]
        trk = [k for k, f in zip(keys, tr) if f]
        out[split] = {k: {"label": int(lab[kidx[k]]), "best_train": trk[a], "ncc": round(float(s), 4)}
                      for k, s, a in zip(tk, best, arg)}
    # reference: within-training best match excluding itself (original variant only)
    Xt = X[tr]
    simtt = np.einsum("avd,bvd->ab", Xt, Xt) / 6
    np.fill_diagonal(simtt, -1)
    out["train_self_best"] = [round(float(v), 4) for v in simtt.max(1)]
    # dataset-wide duplicate groups (connected components of NCC > DUP over all notes)
    DUP = 0.98
    allbest = np.full((len(keys), len(keys)), -1.0, np.float32)
    for V in variants:
        allbest = np.maximum(allbest, np.einsum("avd,bvd->ab", V.reshape(len(keys), 6, -1), X) / 6)
    np.fill_diagonal(allbest, -1)
    parent = list(range(len(keys)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for a, b in zip(*np.where(allbest > DUP)):
        parent[find(a)] = find(b)
    groups = defaultdict(list)
    for i in range(len(keys)):
        groups[find(i)].append(keys[i])
    groups = list(groups.values())
    mixed = [g for g in groups if len({k.split("_")[0] for k in g}) > 1]
    out["groups"] = {
        "threshold": DUP, "n_notes": len(keys), "n_groups": len(groups),
        "n_singletons": sum(len(g) == 1 for g in groups),
        "notes_in_dup_groups": int(sum(len(g) for g in groups if len(g) > 1)),
        "size_hist": {str(s): sum(len(g) == s for g in groups) for s in sorted({len(g) for g in groups})},
        "mixed_label_groups": mixed,
        "per_class_groups": {c: sum(all(k.startswith(c) for k in g) for g in groups) for c in ("fake", "real")},
        "all": groups,
    }
    with open(os.path.join(HERE, "duplicates.json"), "w") as f:
        json.dump(out, f, indent=1)
    for split in ("val", "test"):
        s = np.array([v["ncc"] for v in out[split].values()]); l = np.array([v["label"] for v in out[split].values()])
        for c, name in ((0, "fake"), (1, "real")):
            print(split, name, "n", (l == c).sum(), "hist",
                  np.histogram(s[l == c], bins=[-1, .5, .7, .8, .85, .9, .95, .98, 1.01])[0])


if __name__ == "__main__":
    main()
