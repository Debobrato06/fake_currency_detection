# SN Computer Science submission package

Journal: **SN Computer Science** (Springer Nature, ISSN 2661-8907), single-blind review.
Submit at: https://www.springer.com/journal/42979 → "Submit manuscript".
Guidelines checked on 8 Nov 2026: https://link.springer.com/journal/42979/submission-guidelines

## Files in this folder

| File | What it is | Upload as (Editorial Manager item type) |
|---|---|---|
| `SNCS_manuscript.pdf` | Compiled manuscript (single-column, 19 pages) | Manuscript (PDF), if the system asks for a PDF |
| `SNCS_manuscript.tex` | LaTeX source of the manuscript | Manuscript / LaTeX source file |
| `SNCS_manuscript.bbl` | Compiled bibliography (the system needs it to build the PDF) | LaTeX supplementary file |
| `references.bib` | BibTeX database (41 references, all DOIs checked) | LaTeX supplementary file |
| `sn-jnl.cls`, `sn-mathphys-num.bst` | Springer Nature class and reference style | LaTeX supplementary file |
| `figures/Fig1_pipeline.pdf` ... `Fig9_leakage.pdf` | Nine figures, numbered in citation order | Figure 1 ... Figure 9 |
| `SNCS_LaTeX_source.zip` | All LaTeX files above in one zip (for Overleaf, or if the system accepts one zip) | Alternative to uploading files one by one |
| `ESM_1.zip` | **Online Resource 1**: duplicate groups, split assignments, test predictions, result JSON files, all code | Electronic Supplementary Material |
| `Cover_Letter.pdf` / `.tex` | Cover letter to the Editor-in-Chief | Cover letter |

To rebuild: `pdflatex SNCS_manuscript && bibtex SNCS_manuscript && pdflatex SNCS_manuscript && pdflatex SNCS_manuscript`
(or upload `SNCS_LaTeX_source.zip` to Overleaf, compiler pdfLaTeX).

## Changes from `../Springer_paper.tex` for this journal

- Structured abstract with the required headings **Purpose / Methods / Results / Conclusion**
  (225 words; limit 150-250). The Purpose states the research questions.
- 6 keywords (limit 4-6).
- Plain Language Summary and Word Count removed (not requested by SN Computer Science).
- Declarations heading renamed **Statements and Declarations** (required heading).
- Use of the AI assistant for analysis scripts is now also documented in the Methods
  (Section 3.6, "Software and use of AI tools"), as the journal's LLM policy requires.
- Supplementary material renamed `ESM_1.zip` and cited in the text as "Online Resource 1";
  its README carries the article title, journal, authors and corresponding author, as required.
- Numbered references in square brackets with full DOI links (journal style); ORCID of the
  corresponding author on the title page.

## Submission form: text to paste

**Article type:** Original Research

**Title:** Reliable Smartphone-Based Detection of Counterfeit Bangladeshi Banknotes: Multi-View Deep
Learning with Out-of-Distribution Rejection and a Benchmark Audit

**Short title (running head):** Reliable Smartphone-Based Detection of Counterfeit Bangladeshi Banknotes

**Keywords:** Counterfeit banknote detection; Bangladeshi Taka; Benchmark audit; Data leakage;
Out-of-distribution detection; Explainable AI

**Abstract:**

Purpose: Counterfeit high-value banknotes harm retailers and individuals who cannot afford verification hardware. We ask whether the near-perfect accuracy reported on the public JaalTaka benchmark measures counterfeit recognition, and whether a smartphone authenticator can also reject unsupported inputs, admit uncertainty, and explain its decisions in real time.

Methods: We present a smartphone-based authenticator for Bangladeshi Tk 500 and Tk 1000 notes, evaluated on JaalTaka (1,390 notes: 802 genuine, 588 seized counterfeits; six photographs each). It fine-tunes EfficientNet-B0, fuses up to six photographs per note, returns a genuine, uncertain, or counterfeit verdict, rejects unsupported inputs, and explains decisions with Grad-CAM. We audited the benchmark for duplicates.

Results: On 208 held-out test notes, the system reaches 98.08% accuracy (95% CI 95.16-99.25%) and an ROC-AUC of 0.994 at 37 ms per photograph. However, the 1,390 notes form only 846 distinct photograph sets, 116 test notes have a copy in training or validation, and 12 duplicate groups carry both labels, causing all four test errors. On the 92 test notes without a copy, the system and two simple baselines are error-free. On a group-aware split without shared photographs, the retrained system and nearest-neighbour classification on generic features are both error-free on all 205 test notes.

Conclusion: The benchmark is saturated. We release the duplicate groups and recommend group-aware, counterfeit-family hold-out evaluation.

**Authors:**
1. Debobrato Biswas (corresponding), Department of Software Engineering, Daffodil International
   University, Dhaka 1207, Bangladesh; biswas2305343003@diu.edu.bd; ORCID 0009-0005-0088-8657
2. Imran Mahmud, same affiliation; *e-mail and ORCID: fill in*

**Funding:** none. **Competing interests:** none. **Ethics:** not applicable (public CC BY 4.0
image dataset, no human participants or animals). **Data availability:** JaalTaka on Mendeley
Data (doi:10.17632/2m7wk5cy4c.2); derived data and code in Online Resource 1.

**Publishing model:** choose the subscription (non-open-access) route to publish without an
article processing charge; Open Choice (open access) has a fee.

## Before you press Submit

- [ ] **No parallel submission.** The journal states that a submission implies the work "is not
      under consideration for publication anywhere else", and the cover letter says so. Withdraw the
      JAIIT submission (and any other journal, including the IEEE version) and receive the
      confirmation before submitting here.
- [ ] Co-author Imran Mahmud has approved the final PDF and the submission; add the co-author's
      e-mail (and ORCID, if available) in the submission form.
- [ ] Read `SNCS_manuscript.pdf` once more in full; check the PDF that Editorial Manager builds
      (all 9 figures, 6 tables, references 1-41, no "??").
- [ ] Optional: suggest 2-4 independent reviewers (different institutions and countries, no
      co-authorship with you, institutional e-mail).
- [ ] Optional, recommended by Springer Nature's research data policy: deposit `ESM_1.zip` on
      Zenodo to get a DOI, then add that DOI to "Data availability" and "Code availability".

## Known limitations reviewers may raise (already stated in Section 5.1)

Single training run per split (no seed variation); no retraining of ResNet50/MobileNetV2 on our
splits; preliminary OOD test (105 images, no MSP/energy comparison). If reviewers ask, these can be
added in the revision.
