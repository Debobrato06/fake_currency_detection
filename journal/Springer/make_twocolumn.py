"""Derive Springer_paper_twocolumn.tex from Springer_paper.tex (the single source of text).

    python make_twocolumn.py

Wide figures and tables become figure*/table*, small figures take the column width, the
loss equation is split over two lines, and the audit table gets shorter labels.
"""
import re

src = open("Springer_paper.tex", encoding="utf8").read()

s = src.replace("%%  Springer Nature journal paper (sn-jnl class",
                "%%  Springer Nature journal paper, TWO-COLUMN (sn-jnl class")
s = s.replace("pdflatex Springer_paper -> bibtex Springer_paper",
              "pdflatex Springer_paper_twocolumn -> bibtex Springer_paper_twocolumn")
s = s.replace("upload this folder (Springer_paper.tex,", "upload this folder (Springer_paper_twocolumn.tex,")
s = s.replace("%% For double line spacing during review, add the \"referee\" option;\n"
              "%% for line numbers, add \"lineno\".\n\\documentclass[pdflatex,sn-mathphys-num]{sn-jnl}",
              "%% Two-column Springer Nature layout (option iicol). Single-column version:\n"
              "%% Springer_paper.tex. For line numbers, add the \"lineno\" option.\n"
              "\\documentclass[pdflatex,iicol,sn-mathphys-num]{sn-jnl}")

# floats: column-wide unless listed here
NARROW_FIG = {"fig:confusion", "fig:roc", "fig:ood"}
NARROW_TAB = {"tab:audit"}


def widen(m):
    env, body = m.group(1), m.group(2)
    label = re.search(r"\\label\{([^}]+)\}", body).group(1)
    if label in (NARROW_FIG if env == "figure" else NARROW_TAB):
        body = body.replace("width=0.75\\textwidth", "width=\\columnwidth")
        body = body.replace("\\begin{tabular*}{\\textwidth}", "\\footnotesize\n\\begin{tabular*}{\\columnwidth}")
        return f"\\begin{{{env}}}{body}\\end{{{env}}}"
    body = body.replace("[!htbp]", "[!tp]", 1)  # starred floats accept only t and p
    return f"\\begin{{{env}*}}{body}\\end{{{env}*}}"


s = re.sub(r"\\begin\{(figure|table)\}(.*?)\\end\{\1\}", widen, s, flags=re.S)

s = s.replace("""\\begin{equation}
\\mathcal{L} = -\\sum_{c\\in\\{0,1\\}} w_c\\, q_c \\log \\hat{y}_c, \\quad
q_c = (1-\\varepsilon)\\,\\mathbb{1}[c=y] + \\tfrac{\\varepsilon}{2},
\\label{eq:loss}
\\end{equation}""", """\\begin{align}
\\mathcal{L} &= -\\sum_{c\\in\\{0,1\\}} w_c\\, q_c \\log \\hat{y}_c, \\nonumber\\\\
q_c &= (1-\\varepsilon)\\,\\mathbb{1}[c=y] + \\tfrac{\\varepsilon}{2},
\\label{eq:loss}
\\end{align}""")

for a, b in [
    ("3{,}877 words excluding references", "3{,}862 words excluding references"),
    ("Notes / distinct photograph sets (groups) &", "Notes / distinct photograph sets &"),
    ("Notes sharing their photographs with another note &", "Notes sharing photographs with another &"),
    ("Groups with only counterfeit / only genuine labels &", "Counterfeit-only / genuine-only groups &"),
    ("Test notes with a copy in training or validation & 116 of 208 (55.8\\%)", "Test notes with a copy in train/val & 116/208 (55.8\\%)"),
    ("\\quad counterfeit / genuine & 60 of 88 / 56 of 120", "\\quad counterfeit / genuine & 60/88 / 56/120"),
    ("Test errors explained by label conflicts &", "Test errors due to label conflicts &"),
]:
    assert a in s, a
    s = s.replace(a, b)

open("Springer_paper_twocolumn.tex", "w", encoding="utf8").write(s)
print("written Springer_paper_twocolumn.tex")
