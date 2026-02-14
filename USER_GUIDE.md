# 🛡️ AI Currency Guardian | User Manual Guide

Welcome to the **AI Currency Guardian (Elite Forensic Suite)**. This guide will help you understand how to navigate and use the system to detect counterfeit currency effectively.

---

## 🚀 1. Getting Started
1. **Launch the System**: Run the `start.sh` script or execute `streamlit run app.py`.
2. **Access the UI**: Open your browser and go to the local URL provided (usually `http://localhost:8501`).
3. **Choose Theme**: Use the ☀️/🌙 icon in the top navigation bar to switch between Light and Dark mode.

---

## 🔍 2. Using the Intelligence Scanner
The Scanner is the primary tool for analyzing banknotes.

### Step 1: Upload Image
- Click on the upload box or drag and drop a high-resolution image of the banknote (JPG, JPEG, PNG).
- **Tip**: For best results, use a flat, well-lit image with a plain background.

### Step 2: Analysis Core (Side Panel)
You can toggle specific forensic modules on or off:
- **Watermark (জলছাপ)**: Checks for pixel density and light transparency.
- **Security Thread (সুতা)**: Verifies the continuity of the metallic thread.
- **Intaglio (উঁচু ছাপা)**: Analyzes the sharpness of the printed ink texture.
- **Microprint (ক্ষুদ্র লেখা)**: Attempts to read microscopic text using OCR.
- **Color Shift (রঙ পরিবর্তন)**: Maps the color spectrum to check for OVI shift.

### Step 3: Set Strictness Mode
- Use the **Strictness Slider** to adjust the sensitivity. 
- Higher values require more features to pass for a "GENUINE" verdict.

---

## 📊 3. Interpreting Results
After the scan, the system provides a comprehensive verdict:

1. **The Verdict Box**: 
   - 🟢 **GENUINE**: The note passed the required forensic checks.
   - 🔴 **SUSPICIOUS**: The note failed several security checks.
2. **Forensic Score**: A score out of 20. Each enabled feature contributes 4 points if it passes.
3. **Forensic Streams**: Scroll down to see the visual output for each module (e.g., the edge map for Intaglio or the pattern map for Watermark).

---

## 📜 4. Technical Journal
- Click on the **Journal** tab in the navigation bar to read the scientific manuscript.
- This section details the algorithms and methodology used by the AI engine.

---

## ⚙️ 5. Tips for High Accuracy
- **Alignment**: Ensure the banknote is aligned straight in the photo.
- **Resolution**: Use a camera with at least 12MP for Microprint detection.
- **Lighting**: Avoid glares or shadows that might confuse the Color Shift analysis.

---

## 🛠️ Troubleshooting
- **Text Not Readable**: Adjust the **Text Scaling** slider in the "System Config" section of the sidebar.
- **Slow Processing**: Ensure your system has the necessary dependencies installed (`pytesseract`, `opencv-python`).
- **Classic UI**: If you prefer the legacy dashboard, click the "Classic UI" link in the navigation bar.

---
*© 2026 AI Currency Guardian | Advanced Forensic Intelligence*
