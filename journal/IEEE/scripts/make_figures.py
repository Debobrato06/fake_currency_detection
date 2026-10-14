"""
Build every figure of the IEEE paper from predictions.npz (+ Grad-CAM crops).

    python journal/IEEE/scripts/make_figures.py      # any Python with numpy, pillow, matplotlib

Writes journal/IEEE/figures/*.pdf (vector, used by the paper), *.png previews,
and scripts/stats.json with the numbers quoted in the text.
"""
import itertools
import json
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FIG = os.path.join(HERE, "..", "figures")
IMG_SIZE = 288
COL, FULL = 3.5, 7.16  # IEEE column / page width in inches

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"], "mathtext.fontset": "stix",
    "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 7,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.linewidth": 0.6, "lines.linewidth": 1.2,
    "savefig.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.02, "pdf.fonttype": 42,
})
GREEN, RED, BLUE, AMBER, GREY = "#1a9850", "#d73027", "#2c7bb6", "#f39c12", "#7f7f7f"

d = np.load(os.path.join(HERE, "predictions.npz"))
y, p, notes, views = d["labels"], d["p"], d["notes"], d["views"]
stats = {}


def save(fig, name):
    fig.savefig(os.path.join(FIG, name + ".pdf"))
    fig.savefig(os.path.join(FIG, name + ".png"), dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------- metrics
def roc(yv, pv):
    order = np.argsort(-pv)
    ys = yv[order]
    tpr = np.concatenate([[0], np.cumsum(ys) / ys.sum()])
    fpr = np.concatenate([[0], np.cumsum(1 - ys) / (1 - ys).sum()])
    return fpr, tpr


def auc(yv, pv):
    pos, neg = pv[yv == 1], pv[yv == 0]
    return float(((pos[:, None] > neg[None]).sum() + 0.5 * (pos[:, None] == neg[None]).sum()) / (len(pos) * len(neg)))


def conf(yv, pv, thr=0.5):
    pr = pv >= thr
    return np.array([[np.sum(~pr & (yv == 0)), np.sum(pr & (yv == 0))],
                     [np.sum(~pr & (yv == 1)), np.sum(pr & (yv == 1))]])


def wilson(k, n, z=1.96):
    ph = k / n
    c = (ph + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h


def summary(yv, pv, thr=0.5):
    c = conf(yv, pv, thr)
    tn, fp, fn, tp = c[0, 0], c[0, 1], c[1, 0], c[1, 1]
    acc = (tp + tn) / len(yv)
    prec = tp / max(tp + fp, 1)
    rec = tp / max(tp + fn, 1)
    spec = tn / max(tn + fp, 1)
    lo, hi = wilson(tp + tn, len(yv))
    return {"n": int(len(yv)), "accuracy": acc, "acc_ci95": [lo, hi], "auc": auc(yv, pv),
            "precision_genuine": prec, "recall_genuine": rec, "specificity_fake_detection": spec,
            "f1_genuine": 2 * prec * rec / max(prec + rec, 1e-9),
            "balanced_accuracy": (rec + spec) / 2, "confusion_[[ff,fr],[rf,rr]]": c.tolist()}


note_ids = sorted(set(notes))
idx_of = {n: np.where(notes == n)[0] for n in note_ids}
yn = np.array([y[idx_of[n][0]] for n in note_ids])
pn = np.array([p[idx_of[n]].mean() for n in note_ids])

stats["per_photo"] = summary(y, p)
stats["per_note"] = summary(yn, pn)
stats["center_hidden"] = summary(y, d["p_center"])
stats["border_hidden"] = summary(y, d["p_border"])
stats["per_view_accuracy"] = {int(v): float(np.mean((p[views == v] >= 0.5) == y[views == v])) for v in range(1, 7)}
stats["n_params"] = int(d["n_params"])
stats["latency_ms_median"] = float(np.median(d["latency_ms"]))
stats["split_counts_[photos,notes,real_photos,fake_photos]"] = d["counts"].tolist()

# accuracy vs number of averaged views (all C(6,k) subsets of every note)
kv = {}
for k in range(1, 7):
    accs, aucs = [], []
    for comb in itertools.combinations(range(6), k):
        pk = np.array([p[idx_of[n][list(comb)]].mean() for n in note_ids])
        accs.append(np.mean((pk >= 0.5) == yn)); aucs.append(auc(yn, pk))
    kv[k] = {"acc_mean": float(np.mean(accs)), "acc_min": float(np.min(accs)), "acc_max": float(np.max(accs)),
             "auc_mean": float(np.mean(aucs)), "subsets": len(accs)}
stats["views_k"] = kv

# three-way decision vs strictness threshold tau (note level)
taus = np.round(np.arange(0.50, 0.991, 0.01), 2)
tw = []
for t in taus:
    gen, unc = pn >= t, (pn >= 0.5) & (pn < t)
    tw.append({"tau": float(t),
               "genuine_accepted": float(np.mean(gen[yn == 1])), "genuine_uncertain": float(np.mean(unc[yn == 1])),
               "fake_accepted": float(np.mean(gen[yn == 0])), "fake_uncertain": float(np.mean(unc[yn == 0])),
               "uncertain_total": float(np.mean(unc))})
stats["three_way"] = {f"{r['tau']:.2f}": r for r in tw if r["tau"] in (0.5, 0.6, 0.7, 0.85, 0.9)}

ood_t, ood_v = d["ood_test"], d["ood_val"]
stats["ood"] = {"test_rejected_frac": float(np.mean(ood_t > 1.0)), "val_rejected_frac": float(np.mean(ood_v > 1.0)),
                "test_median": float(np.median(ood_t))}

with open(os.path.join(HERE, "stats.json"), "w") as f:
    json.dump(stats, f, indent=2, default=float)

# ---------------------------------------------------------------- Fig: pipeline
fig, ax = plt.subplots(figsize=(FULL, 1.75))
ax.set_xlim(0, 100); ax.set_ylim(0, 24); ax.axis("off")
boxes = [
    (0.5, "Smartphone\nphotos (1–6 views\nof one note)", "#eef3fb"),
    (14.8, "Pre-processing\nresize 331 px,\ncentre crop 288 px,\nImageNet norm.", "#eef3fb"),
    (29.1, "EfficientNet-B0\nbackbone\n(ImageNet init.,\nfine-tuned)", "#e7f5ec"),
    (43.4, "Global avg. pool\n1280-d\nembedding $\\mathbf{e}$", "#e7f5ec"),
    (57.7, "Linear head\n(dropout 0.3)\n$P(\\mathrm{genuine}\\,|\\,x_i)$", "#e7f5ec"),
    (72.0, "Multi-view fusion\n$\\bar{p}=\\frac{1}{|\\mathcal{V}|}\\sum_{i\\in\\mathcal{V}} p_i$", "#fdf2e3"),
    (86.3, "Three-way\ndecision:\ngenuine /\nuncertain /\ncounterfeit", "#fdf2e3"),
]
W, H, Y = 13.2, 12.5, 10.5
for x, txt, col in boxes:
    ax.add_patch(FancyBboxPatch((x, Y), W, H, boxstyle="round,pad=0.25,rounding_size=1.2", fc=col, ec="#33415c", lw=0.7))
    ax.text(x + W / 2, Y + H / 2, txt, ha="center", va="center", fontsize=6.6, linespacing=1.15)
for (x, *_), (x2, *_) in zip(boxes, boxes[1:]):
    ax.add_patch(FancyArrowPatch((x + W + 0.3, Y + H / 2), (x2 - 0.3, Y + H / 2), arrowstyle="-|>", mutation_scale=7, lw=0.8, color="#33415c"))
# OOD gate and Grad-CAM branches
ax.add_patch(FancyBboxPatch((43.4, 0.6), W + 14.3, 6.6, boxstyle="round,pad=0.25,rounding_size=1.2", fc="#fbe9e9", ec="#a33", lw=0.7))
ax.text(43.4 + (W + 14.3) / 2, 3.9, "OOD gate (PCA-Mahalanobis + residual):\nphoto excluded if $r(\\mathbf{e})>1$", ha="center", va="center", fontsize=6.4)
ax.add_patch(FancyArrowPatch((50, Y - 0.3), (50, 7.5), arrowstyle="-|>", mutation_scale=7, lw=0.8, color="#a33"))
ax.add_patch(FancyArrowPatch((71.6, 3.9), (78.6, Y - 0.3), arrowstyle="-|>", mutation_scale=7, lw=0.8, color="#a33", connectionstyle="arc3,rad=0.25"))
ax.add_patch(FancyBboxPatch((14.8, 0.6), W + 14.3, 6.6, boxstyle="round,pad=0.25,rounding_size=1.2", fc="#f1ecf8", ec="#5b3f8c", lw=0.7))
ax.text(14.8 + (W + 14.3) / 2, 3.9, "Grad-CAM on last conv. stage\n(visual explanation for the user)", ha="center", va="center", fontsize=6.4)
ax.add_patch(FancyArrowPatch((35.7, Y - 0.3), (35.7, 7.5), arrowstyle="-|>", mutation_scale=7, lw=0.8, color="#5b3f8c"))
save(fig, "fig_pipeline")

# ---------------------------------------------------------------- Fig: dataset samples
def crop_full(path, h=150):
    im = Image.open(os.path.join(ROOT, path)).convert("RGB")
    return im.resize((round(im.width * h / im.height), h))


real_n = next(n for n in note_ids if yn[note_ids.index(n)] == 1)
fake_n = next(n for n in note_ids if yn[note_ids.index(n)] == 0)
fig, axs = plt.subplots(2, 6, figsize=(FULL, 2.45), gridspec_kw={"wspace": 0.04, "hspace": 0.12})
for r, n in enumerate([real_n, fake_n]):
    ii = idx_of[n][np.argsort(views[idx_of[n]])]
    for c, i in enumerate(ii):
        axs[r, c].imshow(crop_full(str(d["paths"][i]), 260)); axs[r, c].set_xticks([]); axs[r, c].set_yticks([])
        for s in axs[r, c].spines.values():
            s.set_edgecolor(GREEN if r == 0 else RED); s.set_linewidth(1.2)
        if r == 0:
            axs[r, c].set_title(f"View {c + 1}", pad=2)
    axs[r, 0].set_ylabel("Genuine" if r == 0 else "Counterfeit", color=GREEN if r == 0 else RED, fontweight="bold")
save(fig, "fig_samples")

# ---------------------------------------------------------------- Fig: confusion matrices
fig, axs = plt.subplots(1, 2, figsize=(COL, 1.65), gridspec_kw={"wspace": 0.55})
for ax, (c, title) in zip(axs, [(conf(y, p), "Per photo ($n$=1248)"), (conf(yn, pn), "Per note, 6 views ($n$=208)")]):
    norm = c / c.sum(1, keepdims=True)
    ax.imshow(norm, cmap="Blues", vmin=0, vmax=1)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{c[i, j]}\n({100 * norm[i, j]:.1f}%)", ha="center", va="center", fontsize=7,
                    color="white" if norm[i, j] > 0.6 else "black")
    ax.set_xticks([0, 1], ["Counterfeit", "Genuine"]); ax.set_yticks([0, 1], ["Counterfeit", "Genuine"], rotation=90, va="center")
    ax.set_xlabel("Predicted"); ax.set_ylabel("Actual"); ax.set_title(title)
save(fig, "fig_confusion")

# ---------------------------------------------------------------- Fig: ROC
fig, ax = plt.subplots(figsize=(COL, 2.55))
for yv, pv, lab, col, ls in [(yn, pn, "Per note, 6 views", GREEN, "-"), (y, p, "Per photo", BLUE, "-"),
                             (y, d["p_border"], "Photo, border hidden", AMBER, "--"),
                             (y, d["p_center"], "Photo, centre hidden", RED, ":")]:
    f_, t_ = roc(yv, pv)
    ax.plot(f_, t_, ls, color=col, label=f"{lab} (AUC = {auc(yv, pv):.3f})")
ax.plot([0, 1], [0, 1], color=GREY, lw=0.6, ls="--")
ax.set_xlabel("False-acceptance rate (counterfeit accepted)"); ax.set_ylabel("Genuine acceptance rate")
ax.set_xlim(-0.01, 1); ax.set_ylim(0, 1.01); ax.legend(loc="lower right", frameon=False); ax.grid(alpha=0.25, lw=0.4)
ins = ax.inset_axes([0.36, 0.42, 0.34, 0.34])
for yv, pv, col in [(yn, pn, GREEN), (y, p, BLUE)]:
    f_, t_ = roc(yv, pv); ins.plot(f_, t_, color=col, lw=1)
ins.set_xlim(0, 0.1); ins.set_ylim(0.85, 1.0); ins.tick_params(labelsize=5.5); ins.grid(alpha=0.25, lw=0.4)
save(fig, "fig_roc")

# ---------------------------------------------------------------- Fig: score distribution + three-way decision
fig, axs = plt.subplots(1, 2, figsize=(FULL, 2.1), gridspec_kw={"wspace": 0.28, "width_ratios": [1, 1.1]})
ax = axs[0]
bins = np.linspace(0, 1, 26)
ax.hist(pn[yn == 0], bins, color=RED, alpha=0.75, label="Counterfeit notes")
ax.hist(pn[yn == 1], bins, color=GREEN, alpha=0.75, label="Genuine notes")
ax.axvline(0.5, color="k", lw=0.8, ls="--"); ax.axvline(0.7, color=AMBER, lw=0.8, ls="--")
ax.text(0.5, 1.6, " 0.5", fontsize=6.5); ax.text(0.7, 1.6, r" $\tau$=0.7", fontsize=6.5, color=AMBER)
ax.set_yscale("log"); ax.set_xlabel(r"Fused genuine probability $\bar{p}$"); ax.set_ylabel("Number of test notes (log)")
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 0.82)); ax.set_title("(a) Note-level score distribution")
ax = axs[1]
T = np.array([r["tau"] for r in tw])
ax.plot(T, [100 * r["genuine_accepted"] for r in tw], color=GREEN, label="Genuine accepted")
ax.plot(T, [100 * r["genuine_uncertain"] for r in tw], color=GREEN, ls="--", label="Genuine → uncertain")
ax.plot(T, [100 * r["fake_accepted"] for r in tw], color=RED, label="Counterfeit accepted")
ax.plot(T, [100 * r["uncertain_total"] for r in tw], color=AMBER, ls=":", label="All notes → uncertain")
ax.set_xlabel(r"Strictness threshold $\tau$"); ax.set_ylabel("Test notes (%)"); ax.set_ylim(-2, 102)
ax.grid(alpha=0.25, lw=0.4); ax.legend(frameon=False, loc="center left"); ax.set_title(r"(b) Three-way decision vs. $\tau$")
save(fig, "fig_scores")

# ---------------------------------------------------------------- Fig: shortcut diagnostic
def eval_crop(path):
    im = Image.open(os.path.join(ROOT, path)).convert("RGB")
    s = int(IMG_SIZE * 1.15) / min(im.size)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.BILINEAR)
    l, t = (im.width - IMG_SIZE) // 2, (im.height - IMG_SIZE) // 2
    return np.array(im.crop((l, t, l + IMG_SIZE, t + IMG_SIZE)))


ex = eval_crop(str(d["paths"][idx_of[real_n][0]]))
b = int(IMG_SIZE * 0.2)
cen = ex.copy(); cen[b:-b, b:-b] = 0
bor = np.zeros_like(ex); bor[b:-b, b:-b] = ex[b:-b, b:-b]
fig = plt.figure(figsize=(FULL, 1.75))
gs = fig.add_gridspec(1, 5, width_ratios=[1, 1, 1, 0.22, 3.0], wspace=0.06)
for i, (im, t) in enumerate([(ex, "(a) Full input"), (cen, "(b) Centre hidden"), (bor, "(c) Border hidden")]):
    a = fig.add_subplot(gs[0, i]); a.imshow(im); a.set_xticks([]); a.set_yticks([]); a.set_title(t)
a = fig.add_subplot(gs[0, 4])
cond = ["Full input", "Border hidden", "Centre hidden"]
keys = ["per_photo", "border_hidden", "center_hidden"]
xx = np.arange(3); w = 0.26
for j, (m, lab, col) in enumerate([("accuracy", "Accuracy", BLUE), ("specificity_fake_detection", "Counterfeit detected", RED),
                                   ("recall_genuine", "Genuine accepted", GREEN)]):
    v = [100 * stats[k][m] for k in keys]
    a.bar(xx + (j - 1) * w, v, w, color=col, alpha=0.85, label=lab)
    for xi, vi in zip(xx + (j - 1) * w, v):
        a.text(xi, vi + 1.5, f"{vi:.1f}", ha="center", va="bottom", fontsize=5.2, rotation=90)
a.set_xticks(xx, cond); a.set_ylim(0, 135); a.set_yticks(range(0, 101, 25)); a.set_ylabel("Test photos (%)"); a.yaxis.set_label_position("right"); a.yaxis.tick_right()
a.legend(frameon=False, ncol=3, loc="upper center", fontsize=6.2); a.set_title("(d) Per-photo test results under occlusion")
save(fig, "fig_shortcut")

# ---------------------------------------------------------------- Fig: OOD score
fig, ax = plt.subplots(figsize=(COL, 1.8))
bins = np.logspace(np.log10(min(ood_t.min(), ood_v.min()) * 0.9), np.log10(max(ood_t.max(), ood_v.max(), 1.2) * 1.1), 45)
ax.hist(ood_v, bins, color=GREY, alpha=0.6, label=f"Validation photos ($n$={len(ood_v)})")
ax.hist(ood_t, bins, histtype="step", color=BLUE, lw=1.1, label=f"Test photos ($n$={len(ood_t)})")
ax.set_ylim(0, ax.get_ylim()[1] * 1.45)
ax.axvline(1.0, color=RED, ls="--", lw=0.9); ax.text(1.03, ax.get_ylim()[1] * 0.85, "reject if $r>1$", color=RED, fontsize=6.5)
ax.set_xscale("log"); ax.set_xlabel("OOD ratio $r(\\mathbf{e})$"); ax.set_ylabel("Photos"); ax.legend(frameon=False, loc="upper left")
save(fig, "fig_ood")

# ---------------------------------------------------------------- Fig: Grad-CAM
gdir = os.path.join(HERE, "gradcam")
if os.path.exists(os.path.join(gdir, "picks.txt")):
    rows = [l.split("\t") for l in open(os.path.join(gdir, "picks.txt")).read().strip().splitlines()]
    picked = list(dict.fromkeys(r[0] for r in rows))
    cols = 4
    fig, axs = plt.subplots(len(picked), cols, figsize=(FULL, 1.72 * len(picked)), gridspec_kw={"wspace": 0.03, "hspace": 0.42})
    titles = ["(a) Genuine note, correctly accepted", "(b) Counterfeit note, correctly rejected", "(c) Test error: label-conflict note"]
    for r, n in enumerate(picked):
        rr = [x for x in rows if x[0] == n][:2]
        lab = "genuine" if rr[0][2] == "1" else "counterfeit"
        for c in range(cols):
            v, _, pi, pm = rr[c // 2][1:5]
            kind = "img" if c % 2 == 0 else "cam"
            axs[r, c].imshow(Image.open(os.path.join(gdir, f"{n}_{v}_{kind}.png")).convert("RGB"))
            axs[r, c].set_xticks([]); axs[r, c].set_yticks([])
            axs[r, c].set_xlabel((f"View {v}" if kind == "img" else f"Grad-CAM, $p$={float(pi):.3f}"), fontsize=6.8, labelpad=2)
        axs[r, 0].set_title(f"{titles[min(r, 2)]} (true: {lab}, fused $\\bar{{p}}$={float(rr[0][4]):.3f})", loc="left", fontsize=7.4)
    save(fig, "fig_gradcam")

# ---------------------------------------------------------------- Fig: duplicate / label audit
dpath = os.path.join(HERE, "duplicates.json")
if os.path.exists(dpath):
    dup = json.load(open(dpath))
    fig = plt.figure(figsize=(FULL, 2.2))
    gs = fig.add_gridspec(2, 5, width_ratios=[2.2, 0.2, 1, 1, 1], wspace=0.05, hspace=0.32)
    ax = fig.add_subplot(gs[:, 0])
    bins = np.linspace(0.6, 1.0, 41)
    for split, lab, col, name in [("test", 0, RED, "Counterfeit"), ("test", 1, GREEN, "Genuine")]:
        v = np.array([x["ncc"] for x in dup[split].values() if x["label"] == lab])
        ax.hist(v, bins, color=col, alpha=0.65, label=f"{name} test notes ({np.sum(v > 0.98)}/{len(v)} > 0.98)")
    ax.axvline(0.98, color="k", ls="--", lw=0.8)
    ax.set_yscale("log"); ax.set_xlabel("Best NCC with any training note (mean of 6 views)")
    ax.set_ylabel("Test notes (log)"); ax.legend(frameon=False, loc="upper left"); ax.grid(alpha=0.25, lw=0.4)
    ax.set_title("(a) Pixel-level match between test and training notes")
    pairs = [("fake_543", "fake_102", "same label"), ("real_402", "fake_549", "label conflict"),
             ("fake_400", "real_802", "label conflict")]
    for c, (a_, b_, kind) in enumerate(pairs):
        for r, n in enumerate((a_, b_)):
            cls, num = n.split("_")
            a = fig.add_subplot(gs[r, 2 + c])
            a.imshow(crop_full(f"data/jaaltaka/{cls}/note_{num}_1.jpg", 220)); a.set_xticks([]); a.set_yticks([])
            for s in a.spines.values():
                s.set_edgecolor(GREEN if cls == "real" else RED); s.set_linewidth(1.3)
            a.set_xlabel(f"{'test' if r == 0 else 'train'}: {'genuine' if cls == 'real' else 'counterfeit'} "
                         f"#{int(num)}", fontsize=6.2, labelpad=1.5)
            if r == 0:
                a.set_title(f"({'bcd'[c]}) {kind}", fontsize=7.4)
    save(fig, "fig_leakage")

print(json.dumps({k: stats[k] for k in ("per_photo", "per_note")}, indent=1, default=float))
