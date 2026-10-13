# 🛡️ AI Currency Guardian | User Manual Guide

Welcome to the **AI Currency Guardian (Elite Forensic Suite)**. This guide will help you understand how to navigate and use the system to detect counterfeit currency effectively.

---

## 🚀 1. Getting Started
1. **Launch the System**: First time only: `python download_dataset.py` then `python train_ai.py`. Then run `start.bat` (Windows) / `start.sh`, or `streamlit run app.py`.
2. **Access the UI**: Open your browser and go to the local URL provided (usually `http://localhost:8501`).
3. **Choose Theme**: Use the ☀️/🌙 icon in the top navigation bar to switch between Light and Dark mode.

---

## 🔍 2. Using the Intelligence Scanner
The Scanner is the primary tool for analyzing banknotes.

### Step 1: Upload Photo(s)
- Click the upload box or drag and drop **1 to 6 photos of the same note** (JPG, PNG, WEBP).
- Supported notes: **Tk 500 and Tk 1000**. Other notes are reported as *NOT SUPPORTED*.
- **Tip**: Take close photos that fill the frame: the front (portrait and security thread), the back,
  and the note held against light (watermark). More photos give a more reliable verdict.

### Step 2: Set the Required Confidence
- The **"Required confidence for GENUINE"** slider (default 70%) sets how sure the AI must be before
  calling a note genuine. Raise it to be stricter.

---

## 📊 3. Interpreting Results
1. **The Verdict Box**:
   - 🟢 **GENUINE**: P(real) is above the required confidence.
   - 🔴 **COUNTERFEIT**: P(real) is below 50%. Do not accept the note.
   - 🟠 **UNCERTAIN**: P(real) is between 50% and the required confidence. Check by hand or add photos.
   - ⚪ **NOT SUPPORTED**: The photo does not look like a Tk 500 / Tk 1000 note.
2. **Per-photo Analysis**: each photo's own P(real), plus:
   - **AI focus (Grad-CAM)**: red areas influenced the decision most.
   - **Edge map**: shows print sharpness (blurry edges often mean a printed copy).
3. Photos rejected by the gate are ignored in the final verdict.

---

## 📜 4. Technical Journal
- Click on the **Journal** tab in the navigation bar to read the scientific manuscript.
- This section details the algorithms and methodology used by the AI engine.

---

## ⚙️ 5. Tips for High Accuracy
- **Alignment**: Ensure the banknote is aligned straight in the photo.
- **Lighting**: Avoid glare and strong shadows.
- **Decision support**: The AI can be wrong. Always confirm a suspicious note at a bank.

---

## 🛠️ Troubleshooting
- **Text Not Readable**: Adjust the **Text Scaling** slider in the "System Config" section of the sidebar.
- **"Trained model not found"**: run `python download_dataset.py` and `python train_ai.py`.
- **Classic UI**: If you prefer the legacy dashboard, click the "Classic UI" link in the navigation bar.

---
*© 2026 AI Currency Guardian | Advanced Forensic Intelligence*
