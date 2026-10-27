# Springer Nature journal paper: Reliable Smartphone-Based Detection of Counterfeit Bangladeshi Banknotes

Same study as `../IEEE/IEEE_paper.tex`, set in the official Springer Nature LaTeX template
(`sn-jnl.cls`, version 3.1, December 2024).

| File | Content |
|---|---|
| `Springer_paper_twocolumn.tex` / `.pdf` | **Two-column** version (`sn-jnl` option `iicol`), 11 pages |
| `Springer_paper.tex` / `.pdf` | Single-column version (default `sn-jnl` manuscript layout), 15 pages |
| `sn-jnl.cls`, `sn-mathphys-num.bst` | Springer Nature class and bibliography style |
| `references.bib` | Same 32 references as the IEEE version |
| `figures/` | All figures (PDF) |

## Compile

On Overleaf, upload the whole folder and set the compiler to **pdfLaTeX**.

Locally (replace the name with `Springer_paper_twocolumn` for the two-column version):
`pdflatex Springer_paper && bibtex Springer_paper && pdflatex Springer_paper && pdflatex Springer_paper`

The PDFs are test builds made with Tectonic. In the two-column file, wide figures and tables use `figure*`/`table*`, the loss equation is split over two lines, and the labels of the duplicate-audit table are shortened to fit one column.

Options in `\documentclass`: add `referee` for double line spacing or `lineno` for line numbers if the
journal asks for them. To change the reference style, replace `sn-mathphys-num` with another style
from the template (e.g. `sn-basic`, `sn-vancouver-num`) and copy its `.bst` file here.

## Differences from the IEEE version

- Title, authors and affiliation use `\author`, `\affil` and `\email`; structured abstract and
  keywords use `\abstract` and `\keywords`.
- Related Work is its own section (Springer Nature introductions have no subheadings).
- Captions follow Springer style (no final period, bold panel labels **a**, **b**, ...).
- Back matter uses `\backmatter`, `\bmhead{Acknowledgements}` and a standard **Declarations**
  section (funding, competing interests, ethics, consent, data/materials/code availability,
  author contributions, use of generative AI).
- IEEE-only parts are removed: biographies, `\markboth`, the Plain Language Summary and the Word
  Count section. Add them back if the target journal asks for them.

Before submission: check the target journal's instructions (reference style, abstract format,
declarations) and adapt the generative AI statement to its policy.

## Screening fixes (current version)

The previous files are kept as `Springer_paper_v1_before_screening.tex/.pdf` and
`Springer_paper_twocolumn_v1_before_screening.tex/.pdf`. Three screening issues were fixed in both versions:

1. **Missing word count:** a *Word Count* section after the abstract. Single-column: 2,857 words excluding
   references (two-column: 2,842, because its audit-table labels are shorter); main text 1,944 words;
   abstract 157 words; 9 figures; 4 tables. Update it if you edit the text.
2. **Missing plain language summary:** a *Plain Language Summary* section after the abstract.
3. **Figure legends out of order:** body lines beginning with a citation ("Table 2 compares ...",
   "Fig. 3), and both ...") were read as legends. The baseline sentence was reworded, and every
   `Fig.~\ref` / `Table~\ref` is now tied to the word before it with `~`, so a figure or table number can
   no longer start a line. In both PDFs the only lines starting with "Fig. N" / "Table N" are the real legends,
   in order: Figs. 1-9, Tables 1-4.

## Audit fixes (27 Oct 2026)

Fixes for the issues in `Paper_12Point_Audit_Springer.pdf`. The previous sources are kept as
`Springer_paper_v2_before_audit_fixes.tex`, `Springer_paper_twocolumn_v2_before_audit_fixes.tex` and
`references_v2_before_audit_fixes.bib`.

- **Single source:** edit only `Springer_paper.tex`, then run `python make_twocolumn.py` to regenerate
  the two-column file.
- **Text:** abstract ("training or validation"), 6 keywords, introduction without uncited claims and with
  two research questions, audit-first contributions, expanded Related Work with a scope table, baseline
  definitions, statistics, NCC-threshold sensitivity (649 vs 846), group-aware re-evaluation, discussion
  of RQ1/RQ2, structured limitations, rewritten conclusion, final AI statement (TODO removed).
- **New numbers:** `scripts/extra_stats.py` -> `scripts/extra_stats.json` (group bootstrap CI, McNemar,
  NCC sensitivity); group-aware baselines -> `scripts/group_eval_baselines.json`.
- **References:** 9 added (all checked on Crossref / PMLR); JaalTaka year corrected to 2026 (vol. 64).
- **Supplementary Information:** `python make_supplementary.py` -> `supplementary/` and `supplementary.zip`;
  upload the zip with the manuscript.
- **Pending:** the fine-tuned row of Table 6 (group-aware split). Training finished; run
  `python train_ai.py --split group --out journal/Springer/models/taka_authenticator_group.pth --epochs 6 --resume`
  from the repository root (the checkpoint `models/taka_authenticator_group_train_state.pth` is here;
  only the final evaluation remains), then `venv/Scripts/python journal/Springer/scripts/eval_group.py`.
- **Folder layout:** everything the Springer paper uses lives in this folder. `scripts/` holds copies of
  the analysis scripts and their inputs (`duplicates.json`, `predictions.npz`, `frozen_feats.npz`,
  `gradcam/`) plus the audit-fix scripts and results; `models/` holds the group-split checkpoint and
  training log. `train_ai.py` and `model_arch.py` stay at the repository root (shared with the app).

## Length and figure-order fixes (27 Oct 2026, second screening)

Previous sources: `Springer_paper_v3_before_length_fix.tex`, `Springer_paper_twocolumn_v3_before_length_fix.tex`.

1. **Length (limit 2,500-4,000 words):** the text was tightened (introduction, related work, training,
   decision rule, discussion, limitations, conclusion, two captions) without removing any result.
   Single-column: 3,877 words excluding references (main text 2,838; abstract 179); two-column: 3,862.
   The broken `\ref{sec:groupsplit}` in the Discussion ("Section ef...") was repaired.
2. **Figure order:** figure files are numbered in citation order (`figures/Fig1_pipeline.pdf` ...
   `Fig9_leakage.pdf`; `scripts/make_figures.py` writes these names), floats use `[!htbp]` and
   `placeins` keeps every float inside its section, so in the single-column PDF each figure follows its
   first citation. In both PDFs the only lines starting with "Fig. N" / "Table N" are the legends, in order.
   Upload the figure files in this numbered order if the system asks for separate figures.
