"""
Evaluate the model trained on the GROUP-aware split (train_ai.py --split group) and the
frozen-feature baselines on its test split, with the same note-level definitions as
analyze_leakage.py (note score = mean of the six photograph scores).

    venv/Scripts/python journal/Springer/scripts/eval_group.py

Needs journal/Springer/models/taka_authenticator_group.pth, frozen_feats.npz, duplicates.json.
Writes journal/Springer/scripts/group_eval.json.
"""
import json
import os
import sys

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression

from analyze_leakage import score
from extra_stats import cluster_bootstrap, mcnemar_exact
from model_arch import TakaAuthNet
from run_inference import run
from train_ai import collect, split_by_group, split_by_note


def main():
    torch.set_num_threads(max(1, (os.cpu_count() or 2) // 2))
    items = collect(os.path.join(ROOT, "data", "jaaltaka"))
    dup = json.load(open(os.path.join(HERE, "duplicates.json")))
    groups = dup["groups"]["all"]
    group_of = {k: gi for gi, g in enumerate(groups) for k in g}
    parts, dropped = split_by_group(items, groups, seed=42)
    test = parts["test"]

    ckpt = torch.load(os.path.join(HERE, "..", "models", "taka_authenticator_group.pth"), map_location="cpu",
                      weights_only=False)
    assert sorted({i[2] for i in test}) == ckpt["test_notes"], "split differs from the trained model"
    model = TakaAuthNet(pretrained=False)
    model.load_state_dict(ckpt["state_dict"])
    model.eval()
    p, _ = run(model, test)

    # frozen features cached by run_baselines.py, re-indexed by photograph path
    cached = np.load(os.path.join(HERE, "frozen_feats.npz"))
    feat = {it[0]: f for k, v in split_by_note(items, seed=42).items() for it, f in zip(v, cached[k])}
    Ftr = np.stack([feat[it[0]] for it in parts["train"]])
    Fte = np.stack([feat[it[0]] for it in test])
    ytr = np.array([i[1] for i in parts["train"]])
    knn = ytr[(Fte @ Ftr.T).argmax(1)].astype(float)
    lp = LogisticRegression(C=1.0, max_iter=3000, class_weight="balanced").fit(Ftr, ytr).predict_proba(Fte)[:, 1]

    y = np.array([i[1] for i in test])
    notes = np.array([i[2] for i in test])
    ids = sorted(set(notes))
    yn = np.array([y[notes == n][0] for n in ids])
    gn = np.array([group_of[n] for n in ids])
    out = {"split": {k: {"notes": len({i[2] for i in v}), "photos": len(v),
                         "genuine_notes": len({i[2] for i in v if i[1] == 1}),
                         "counterfeit_notes": len({i[2] for i in v if i[1] == 0}),
                         "groups": len({group_of[i[2]] for i in v})} for k, v in parts.items()},
           "dropped_conflict_notes": len(dropped)}
    note_scores = {}
    for name, s in (("model", p), ("knn1", knn), ("linear_probe", lp)):
        sn = np.array([s[notes == n].mean() for n in ids])
        note_scores[name] = sn
        out[name] = {"per_photo": score(y, s), "per_note": score(yn, sn),
                     "per_note_ci95_group_bootstrap": cluster_bootstrap((sn >= 0.5) == yn, gn)}
    ok = {k: (v >= 0.5) == yn for k, v in note_scores.items()}
    out["mcnemar_per_note"] = {b: mcnemar_exact(ok["model"], ok[b]) for b in ("knn1", "linear_probe")}
    out["model_errors"] = [{"note": n, "p": float(q)} for n, q, l in zip(ids, note_scores["model"], yn)
                           if (q >= 0.5) != l]
    with open(os.path.join(HERE, "group_eval.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
