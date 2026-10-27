"""Build the Supplementary Information folder cited in the Declarations.

    ../../venv/Scripts/python make_supplementary.py

Writes supplementary/ (and supplementary.zip): duplicate groups, split assignments,
per-note test predictions, and the scripts that produce every number in the paper.
"""
import csv
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SCRIPTS = os.path.join(HERE, "scripts")
sys.path.insert(0, ROOT)

import numpy as np  # noqa: E402

from train_ai import collect, split_by_group, split_by_note  # noqa: E402

OUT = os.path.join(HERE, "supplementary")


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(os.path.join(OUT, "code"))
    items = collect(os.path.join(ROOT, "data", "jaaltaka"))
    dup = json.load(open(os.path.join(SCRIPTS, "duplicates.json")))
    groups = dup["groups"]["all"]
    group_of = {k: gi for gi, g in enumerate(groups) for k in g}
    mixed = {k for g in dup["groups"]["mixed_label_groups"] for k in g}

    with open(os.path.join(OUT, "S1_duplicate_groups.json"), "w") as f:
        json.dump({"definition": "connected components of notes whose six-view mean pixel NCC "
                                 "(48x48 grey thumbnails, flips tried) exceeds 0.98",
                   "n_notes": dup["groups"]["n_notes"], "n_groups": dup["groups"]["n_groups"],
                   "label_conflict_groups": dup["groups"]["mixed_label_groups"],
                   "groups": groups}, f, indent=1)

    note_split = {i[2]: s for s, v in split_by_note(items, seed=42).items() for i in v}
    gparts, dropped = split_by_group(items, groups, seed=42)
    group_split = {i[2]: s for s, v in gparts.items() for i in v}
    label = {i[2]: i[1] for i in items}
    with open(os.path.join(OUT, "S2_splits.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["note", "label", "duplicate_group", "label_conflict_group", "note_level_split",
                    "group_aware_split"])
        for n in sorted(label):
            w.writerow([n, "genuine" if label[n] else "counterfeit", group_of[n], int(n in mixed),
                        note_split[n], group_split.get(n, "excluded")])

    d = np.load(os.path.join(SCRIPTS, "predictions.npz"))
    notes, p = d["notes"], d["p"]
    with open(os.path.join(OUT, "S3_test_predictions_note_level_split.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["note", "label", "p_genuine_fused", "copy_in_train_or_val", "label_conflict_group"])
        for n in sorted(set(notes)):
            leaked = any(note_split[m] != "test" for m in groups[group_of[n]])
            w.writerow([n, "genuine" if label[n] else "counterfeit", f"{p[notes == n].mean():.4f}",
                        int(leaked), int(n in mixed)])

    for name in ("stats.json", "leakage.json", "extra_stats.json", "group_eval_baselines.json", "group_eval.json"):
        if os.path.exists(os.path.join(SCRIPTS, name)):
            shutil.copy(os.path.join(SCRIPTS, name), os.path.join(OUT, "results_" + name))
    for name in sorted(os.listdir(SCRIPTS)):
        if name.endswith(".py"):
            shutil.copy(os.path.join(SCRIPTS, name), os.path.join(OUT, "code", name))
    for name in ("train_ai.py", "model_arch.py"):
        shutil.copy(os.path.join(ROOT, name), os.path.join(OUT, "code", name))

    with open(os.path.join(OUT, "README.txt"), "w") as f:
        f.write("""Supplementary Information
Reliable Smartphone-Based Detection of Counterfeit Bangladeshi Banknotes

S1_duplicate_groups.json   846 duplicate groups of the 1,390 JaalTaka notes and the 12
                           groups that contain both labels.
S2_splits.csv              For every note: label, duplicate group, label-conflict flag,
                           note-level split (seed 42) and group-aware split (seed 42;
                           "excluded" = note of a label-conflict group).
S3_test_predictions_note_level_split.csv
                           Fused genuine probability of the 208 test notes of the
                           note-level split, with the leakage and conflict flags.
results_*.json             Raw outputs of the analysis scripts.
code/                      train_ai.py, model_arch.py and the analysis scripts.

Data: JaalTaka, Mendeley Data, doi:10.17632/2m7wk5cy4c.2 (CC BY 4.0), placed in
data/jaaltaka/{real,fake}/ as note_<id>_<view>.jpg.
Order: train_ai.py -> run_inference.py -> run_baselines.py -> find_duplicates.py ->
analyze_leakage.py -> extra_stats.py; group-aware: train_ai.py --split group ->
eval_group.py.
""")
    shutil.make_archive(OUT, "zip", OUT)
    print("written", OUT, "and supplementary.zip")


if __name__ == "__main__":
    main()
