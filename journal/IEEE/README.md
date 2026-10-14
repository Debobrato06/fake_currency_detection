# IEEE journal paper: Reliable Smartphone-Based Detection of Counterfeit Bangladeshi Banknotes

| File | Content |
|---|---|
| `IEEE_paper.tex` | Paper (IEEEtran, journal mode) |
| `references.bib` | 32 references, each checked against Crossref or the publisher's record |
| `figures/` | All figures (`.pdf` is used by the paper, `.png` is a preview) |
| `IEEE_paper_preview.pdf` | Test build made with Tectonic. Times is not available there, so it uses Latin Modern; Overleaf/pdfLaTeX output uses Times |
| `scripts/` | Code that produces every number, table and figure |

## Compile

On Overleaf, upload `IEEE_paper.tex`, `references.bib` and the `figures/` folder, then set the compiler to **pdfLaTeX**.

Locally, run: `pdflatex IEEE_paper && bibtex IEEE_paper && pdflatex IEEE_paper && pdflatex IEEE_paper`

Before submission:
- complete the biographies at the end of the file (or delete them);
- adapt the Generative AI Disclosure to the journal's policy;
- check the acknowledgment;
- screening checks: two-column IEEE layout (single-column copy: `IEEE_paper_v5_onecolumn.tex/.pdf`) in IMRaD order (Introduction, Materials and Methods, Results, Discussion, Conclusion); 2,955 words excluding references (main text 1,937); 159-word structured abstract as its own section; Plain Language Summary, Word Count and Ethics Statement sections; no figure citation ends a sentence (a trailing "Fig. 7(b)." was read as a legend); figure legends set as one paragraph each (caption package) and kept in order with \FloatBarrier. Update the Word Count section if you edit the text.

Earlier versions: `IEEE_paper_before_screening_fixes.tex` (before any screening fix) `IEEE_paper_v2_before_length_cut.tex/.pdf` (longer version, 246-word unstructured abstract), `IEEE_paper_v3_twocolumn.tex/.pdf` (two-column layout), and `IEEE_paper_v4_before_imrad.tex` (before the IMRaD headings and legend fix).

## Reproduce the results (from the project root)

```bat
venv\Scripts\python journal\IEEE\scripts\run_inference.py   :: test-set predictions, OOD ratios, latency  -> predictions.npz
venv\Scripts\python journal\IEEE\scripts\run_gradcam.py      :: Grad-CAM crops                              -> gradcam/
venv\Scripts\python journal\IEEE\scripts\run_baselines.py    :: frozen-feature 1-NN / linear probe          -> baselines.json
python              journal\IEEE\scripts\find_duplicates.py  :: pixel-NCC duplicate groups                  -> duplicates.json
venv\Scripts\python journal\IEEE\scripts\analyze_leakage.py  :: scores on duplicate-free test subsets       -> leakage.json
python              journal\IEEE\scripts\make_figures.py     :: all figures + stats.json  (needs matplotlib)
```

The scripts use the trained `models/taka_authenticator.pth` and the JaalTaka images in `data/jaaltaka`.
