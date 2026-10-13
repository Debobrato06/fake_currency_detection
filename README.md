# AI Currency Guardian: Fake Taka Detection

Detects whether a **Bangladeshi Tk 500 or Tk 1000 banknote** is genuine or counterfeit from
smartphone photos, using a deep-learning model trained on real seized counterfeit notes.

## How it works

1. **Classifier**: EfficientNet-B0 (ImageNet pretrained) fine-tuned on the
   [JaalTaka dataset](https://data.mendeley.com/datasets/2m7wk5cy4c): 802 genuine and 588
   counterfeit notes (counterfeits supplied by RAB), 6 photos per note.
2. **Multi-photo decision**: upload 1-6 photos of the same note (front, back, against light).
   Their probabilities are averaged.
3. **"Not supported" gate**: the model only knows Tk 500 / Tk 1000. Photos that don't look like those
   notes (other denominations, random pictures) are rejected instead of guessed. This is an
   out-of-distribution check on the network's embedding.
4. **Explainability**: a Grad-CAM heatmap shows which part of the note drove the decision.

Verdicts: `GENUINE`, `COUNTERFEIT`, `UNCERTAIN` (P(real) between 50% and the chosen threshold),
`NOT_SUPPORTED`.

## Results (held-out test set: 208 notes / 1,248 photos never seen in training)

| Metric | Per photo | Per note (6 photos) |
|---|---|---|
| Accuracy | 98.1% | 98.1% |
| ROC-AUC | 0.990 | 0.994 |
| Counterfeits caught | 97.7% | 97.7% (86/88) |
| Genuine accepted | 98.3% | 98.3% (118/120) |

The split is per note, so no physical note appears in both train and test. Full numbers are in
`models/metrics.json`.

"Not supported" gate: it rejects 95% of other-denomination notes (100/105 photos of Tk 2-200 from a
separate dataset), as well as noise, blank and unrelated images. It wrongly rejects 0.3% of genuine
test photos.

## Setup (Windows)

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

:: 1. download the dataset (~2.7 GB after resizing; the source zip is 7.6 GB)
python download_dataset.py

:: 2. train (CPU: about 1 hour; GPU: a few minutes). Add --resume to continue an interrupted run.
python train_ai.py --epochs 6

:: 3. run the apps
start.bat
```

Linux/macOS: use `python3` and `./start.sh`.

- Pro UI (Streamlit): http://localhost:8501
- Classic UI (Flask): http://127.0.0.1:5000. The API is `POST /analyze` (form field `file`, can be repeated;
  optional `threshold`, 0.5-0.99). `GET /status` returns the model status and metrics.

## Files

| File | Purpose |
|---|---|
| `download_dataset.py` | Streams JaalTaka from Mendeley, resizes to 1024 px, saves to `data/jaaltaka/{real,fake}` |
| `model_arch.py` | `TakaAuthNet` (EfficientNet-B0) and image transforms |
| `train_ai.py` | Per-note split, training, evaluation, OOD calibration, background-shortcut diagnostics |
| `detector.py` | Inference: classifier + OOD gate + Grad-CAM |
| `app.py` / `server.py` | Streamlit and Flask front-ends |

## Limitations

- Only **Tk 500 and Tk 1000** are covered, because no public dataset has counterfeit notes of other
  denominations. Other notes get `NOT_SUPPORTED`.
- The model learned from the counterfeit types in JaalTaka. A new kind of forgery may not be detected.
- The model is trained on close-up phone photos. Flatbed scans and far-away whole-note photos are mostly
  rejected as "not supported". When they are not rejected, they are unreliable: in a test, genuine Tk 500/1000
  scans were often called counterfeit.
- A phone photo cannot capture UV features or the feel of intaglio print. Treat the result as decision
  support and confirm suspicious notes at a bank.

## Dataset credit

JaalTaka: A benchmark dataset for detecting counterfeit Bangladeshi banknotes. *Data in Brief* (2025),
doi:10.1016/j.dib.2025.112377. Data: doi:10.17632/2m7wk5cy4c.2, licensed CC BY 4.0. Images were resized
for training.
