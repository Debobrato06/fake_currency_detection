Supplementary Information
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
