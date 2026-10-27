"""
Train the genuine-vs-counterfeit Taka classifier on the JaalTaka dataset.

    python download_dataset.py        # once, fetches data/jaaltaka/{real,fake}
    python train_ai.py --epochs 8

Notes
-----
* Every banknote has 6 photos. The split is done per NOTE (not per photo), so the
  same physical note never appears in both train and test -> honest accuracy.
* Output: models/taka_authenticator.pth (weights + out-of-distribution statistics)
          models/metrics.json         (test-set results)
"""
import os

# Keep numpy/OpenBLAS from reserving per-thread buffers in every DataLoader worker
# (on Windows this exhausted memory on a 16 GB machine).
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import random
import re
import time
from collections import defaultdict

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torch.utils.data import DataLoader, Dataset, Subset

from model_arch import CLASSES, IMG_SIZE, TakaAuthNet, eval_transform, train_transform

NOTE_RE = re.compile(r"note_(\d+)_(\d+)\.jpg$", re.I)


def collect(data_dir):
    """Return list of (path, label, note_key, view)."""
    items = []
    for label, cls in enumerate(CLASSES):
        folder = os.path.join(data_dir, cls)
        for f in sorted(os.listdir(folder)):
            m = NOTE_RE.search(f)
            if m:
                items.append((os.path.join(folder, f), label, f"{cls}_{m.group(1)}", int(m.group(2))))
    return items


def split_by_note(items, seed=42, val=0.15, test=0.15):
    """Stratified split on note ids so the 6 views of one note stay together."""
    notes = defaultdict(list)
    for it in items:
        notes[(it[1], it[2])].append(it)
    rng = random.Random(seed)
    parts = {"train": [], "val": [], "test": []}
    for label in range(len(CLASSES)):
        keys = sorted(k for k in notes if k[0] == label)
        rng.shuffle(keys)
        n_val, n_test = round(len(keys) * val), round(len(keys) * test)
        for i, k in enumerate(keys):
            part = "test" if i < n_test else ("val" if i < n_test + n_val else "train")
            parts[part].extend(notes[k])
    return parts


def split_by_group(items, groups, seed=42, val=0.15, test=0.15):
    """Split on duplicate groups (journal/IEEE/scripts/duplicates.json) so augmented copies
    of a note never cross splits. Groups holding both labels are dropped (labels unreliable)."""
    by_note = defaultdict(list)
    for it in items:
        by_note[it[2]].append(it)
    pure = {0: [], 1: []}
    dropped = []
    for g in groups:
        labels = {by_note[k][0][1] for k in g}
        if len(labels) > 1:
            dropped.extend(g)
        else:
            pure[labels.pop()].append(sorted(g))
    rng = random.Random(seed)
    parts = {"train": [], "val": [], "test": []}
    for label in sorted(pure):
        gs = sorted(pure[label])
        rng.shuffle(gs)
        total = sum(len(g) for g in gs)
        filled = {"test": 0, "val": 0}
        for g in gs:
            # fill test, then val, up to their share of NOTES; the rest goes to train
            part = ("test" if filled["test"] < total * test else
                    "val" if filled["val"] < total * val else "train")
            if part in filled:
                filled[part] += len(g)
            for k in g:
                parts[part].extend(by_note[k])
    return parts, sorted(dropped)


class NoteDataset(Dataset):
    def __init__(self, items, tf, mask=None):
        self.items, self.tf, self.mask = items, tf, mask

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        path, label, _, _ = self.items[i]
        img = Image.open(path).convert("RGB")
        x = self.tf(img)
        if self.mask is not None:
            x = apply_mask(x, self.mask)
        return x, label


def apply_mask(x, mode):
    """Diagnostics: hide the centre (only background/border visible) or the border."""
    _, h, w = x.shape
    bh, bw = int(h * 0.2), int(w * 0.2)
    y = x.clone()
    if mode == "center_hidden":
        y[:, bh:h - bh, bw:w - bw] = 0
    elif mode == "border_hidden":
        keep = y[:, bh:h - bh, bw:w - bw].clone()
        y.zero_()
        y[:, bh:h - bh, bw:w - bw] = keep
    return y


@torch.no_grad()
def predict(model, loader, device):
    model.eval()
    probs, embs, labels = [], [], []
    for x, y in loader:
        logits, emb = model(x.to(device), return_embedding=True)
        probs.append(torch.softmax(logits, 1)[:, 1].cpu())
        embs.append(emb.cpu())
        labels.append(y)
    return torch.cat(probs).numpy(), torch.cat(embs).numpy(), torch.cat(labels).numpy()


def auc_score(y, p):
    order = np.argsort(p)
    ranks = np.empty(len(p))
    ranks[order] = np.arange(1, len(p) + 1)
    pos = y == 1
    n_pos, n_neg = pos.sum(), (~pos).sum()
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    return float((ranks[pos].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def metrics(y, p, thr=0.5):
    pred = (p >= thr).astype(int)
    tp = int(((pred == 1) & (y == 1)).sum()); tn = int(((pred == 0) & (y == 0)).sum())
    fp = int(((pred == 1) & (y == 0)).sum()); fn = int(((pred == 0) & (y == 1)).sum())
    return {
        "accuracy": round((tp + tn) / len(y), 4),
        "auc": round(auc_score(y, p), 4),
        # a counterfeit accepted as real is the costly mistake
        "fake_detection_rate": round(tn / max(tn + fp, 1), 4),
        "real_acceptance_rate": round(tp / max(tp + fn, 1), 4),
        "confusion": {"fake_as_fake": tn, "fake_as_real": fp, "real_as_fake": fn, "real_as_real": tp},
        "n": int(len(y)),
    }


def note_level(items, p):
    """Average the per-photo probabilities of each note (multi-view decision)."""
    agg = defaultdict(list)
    lab = {}
    for (path, label, key, _), pi in zip(items, p):
        agg[key].append(pi)
        lab[key] = label
    keys = sorted(agg)
    return np.array([lab[k] for k in keys]), np.array([np.mean(agg[k]) for k in keys])


def fit_ood(train_emb, val_emb, k=64, pct=99.5):
    """Gaussian model of genuine/fake banknote embeddings in a PCA subspace."""
    mu = train_emb.mean(0)
    xc = train_emb - mu
    _, s, vt = np.linalg.svd(xc, full_matrices=False)
    comps = vt[:k]
    var = (s[:k] ** 2) / (len(xc) - 1)

    def scores(e):
        z = (e - mu) @ comps.T
        maha = (z ** 2 / var).sum(1)
        resid = ((e - mu) - z @ comps) ** 2
        return maha, resid.sum(1)

    vm, vr = scores(val_emb)
    return {
        "mean": mu.astype(np.float32), "components": comps.astype(np.float32), "var": var.astype(np.float32),
        "maha_thr": float(np.percentile(vm, pct)), "resid_thr": float(np.percentile(vr, pct)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/jaaltaka")
    ap.add_argument("--out", default="models/taka_authenticator.pth")
    ap.add_argument("--epochs", type=int, default=8)
    ap.add_argument("--batch", type=int, default=12)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--freeze", type=int, default=4, help="number of early EfficientNet stages to freeze")
    ap.add_argument("--resume", action="store_true", help="continue from the last finished epoch")
    ap.add_argument("--split", choices=["note", "group"], default="note",
                    help="note: per-note split; group: per duplicate group, label-conflict groups removed")
    ap.add_argument("--groups", default="journal/IEEE/scripts/duplicates.json",
                    help="duplicate groups from find_duplicates.py (used with --split group)")
    args = ap.parse_args()

    torch.manual_seed(args.seed); random.seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cpu":
        torch.set_num_threads(max(1, (os.cpu_count() or 2) // 2))

    items = collect(args.data)
    dropped = []
    if args.split == "group":
        with open(args.groups) as f:
            groups = json.load(f)["groups"]["all"]
        parts, dropped = split_by_group(items, groups, seed=args.seed)
        print(f"group split: {len(groups)} groups, {len(dropped)} notes in label-conflict groups dropped")
    else:
        parts = split_by_note(items, seed=args.seed)
    for k, v in parts.items():
        print(f"{k:5s}: {len(v)} photos, {len({i[2] for i in v})} notes, "
              f"{sum(i[1] == 1 for i in v)} real / {sum(i[1] == 0 for i in v)} fake photos")

    mk = lambda its, tf, mask=None: DataLoader(
        NoteDataset(its, tf, mask), batch_size=args.batch, shuffle=False,
        num_workers=args.workers, persistent_workers=False)
    train_set = NoteDataset(parts["train"], train_transform())
    steps_per_epoch = (len(train_set) + args.batch - 1) // args.batch

    def epoch_loader(epoch, skip_batches=0):
        # deterministic shuffle per epoch so a resumed run continues at the exact batch
        order = torch.randperm(len(train_set), generator=torch.Generator().manual_seed(args.seed + epoch))
        order = order[skip_batches * args.batch:].tolist()
        return DataLoader(Subset(train_set, order), batch_size=args.batch, shuffle=False,
                          num_workers=args.workers, persistent_workers=False)
    val_loader = mk(parts["val"], eval_transform())
    test_loader = mk(parts["test"], eval_transform())

    model = TakaAuthNet(pretrained=True).to(device)
    # Freeze the first stages (generic edge/colour filters). They then keep no
    # activations for backprop, which cuts training memory a lot on CPU machines.
    frozen = model.features[:args.freeze]
    for prm in frozen.parameters():
        prm.requires_grad = False
    # class weights balance the 802 real / 588 fake imbalance
    counts = np.bincount([i[1] for i in parts["train"]], minlength=2)
    weights = torch.tensor(counts.sum() / (2 * counts), dtype=torch.float32, device=device)
    criterion = nn.CrossEntropyLoss(weight=weights, label_smoothing=0.05)
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=args.lr, weight_decay=1e-4)
    steps = args.epochs * steps_per_epoch
    scheduler = torch.optim.lr_scheduler.OneCycleLR(optimizer, max_lr=args.lr, total_steps=steps, pct_start=0.15)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    stem = os.path.splitext(args.out)[0]
    state_path = os.path.join(os.path.dirname(args.out), "train_state.pth") if args.split == "note" \
        else stem + "_train_state.pth"
    best_auc, best_state, start_epoch, start_step = -1, None, 0, 0
    if args.resume and os.path.exists(state_path):
        st = torch.load(state_path, map_location="cpu", weights_only=False)
        model.load_state_dict(st["model"]); optimizer.load_state_dict(st["optimizer"])
        scheduler.load_state_dict(st["scheduler"])
        best_auc, best_state, start_epoch = st["best_score"], st["best_state"], st["epoch"]
        start_step = st.get("step", 0)
        print(f"Resumed at epoch {start_epoch + 1}, step {start_step}", flush=True)

    def save_state(epoch, step):
        torch.save({"model": model.state_dict(), "optimizer": optimizer.state_dict(),
                    "scheduler": scheduler.state_dict(), "epoch": epoch, "step": step,
                    "best_score": best_auc, "best_state": best_state}, state_path + ".tmp")
        os.replace(state_path + ".tmp", state_path)

    for epoch in range(start_epoch, args.epochs):
        model.train()
        frozen.eval()  # keep pretrained BatchNorm statistics in the frozen stages
        t0, run_loss, seen = time.time(), 0.0, 0
        first = start_step if epoch == start_epoch else 0
        for step, (x, y) in enumerate(epoch_loader(epoch, first), start=first):
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            loss = criterion(model(x), y)
            loss.backward()
            optimizer.step()
            scheduler.step()
            run_loss += loss.item() * len(y); seen += len(y)
            if step % 20 == 0:
                print(f"  epoch {epoch + 1} step {step}/{steps_per_epoch} loss {run_loss / seen:.4f} "
                      f"({time.time() - t0:.0f}s)", flush=True)
            if step % 100 == 99:
                save_state(epoch, step + 1)
        vp, _, vy = predict(model, val_loader, device)
        vm = metrics(vy, vp)
        print(f"Epoch {epoch + 1}/{args.epochs}: train loss {run_loss / seen:.4f}, "
              f"val acc {vm['accuracy']}, val auc {vm['auc']} ({time.time() - t0:.0f}s)", flush=True)
        score = vm["auc"] + vm["accuracy"]
        if score > best_auc:
            best_auc = score
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        # checkpoint so an interrupted run can continue with --resume
        save_state(epoch + 1, 0)

    model.load_state_dict(best_state)

    # ---- final evaluation on the held-out test notes ----
    _, train_emb, _ = predict(model, mk(parts["train"], eval_transform()), device)
    vp, val_emb, vy = predict(model, val_loader, device)
    tp, _, ty = predict(model, test_loader, device)
    ood = fit_ood(train_emb, val_emb)

    report = {
        "dataset": "JaalTaka (Mendeley Data, doi:10.17632/2m7wk5cy4c.2, CC BY 4.0) - Tk 500 & Tk 1000",
        "split_mode": args.split,
        "dropped_conflict_notes": dropped,
        "split": {k: {"photos": len(v), "notes": len({i[2] for i in v}),
                      "real_notes": len({i[2] for i in v if i[1] == 1}),
                      "fake_notes": len({i[2] for i in v if i[1] == 0})} for k, v in parts.items()},
        "val_per_photo": metrics(vy, vp),
        "test_per_photo": metrics(ty, tp),
        "test_per_note_6_views": metrics(*note_level(parts["test"], tp)),
    }
    # shortcut check: if the model is right with the banknote centre hidden it is
    # reading the background; we want ~50% / AUC ~0.5 there, and high with border hidden.
    for mode in ("center_hidden", "border_hidden"):
        mp, _, my = predict(model, mk(parts["test"], eval_transform(), mask=mode), device)
        report[f"diagnostic_{mode}"] = metrics(my, mp)
    print(json.dumps(report, indent=2))

    torch.save({
        "state_dict": best_state,
        "classes": CLASSES,
        "img_size": IMG_SIZE,
        "arch": "efficientnet_b0",
        "ood": {k: (torch.from_numpy(v) if isinstance(v, np.ndarray) else v) for k, v in ood.items()},
        "metrics": report,
        "test_notes": sorted({i[2] for i in parts["test"]}),
    }, args.out)
    metrics_path = os.path.join(os.path.dirname(args.out), "metrics.json") if args.split == "note" \
        else stem + "_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(report, f, indent=2)
    if os.path.exists(state_path):
        os.remove(state_path)
    print(f"Saved model to {args.out}")


if __name__ == "__main__":
    main()
