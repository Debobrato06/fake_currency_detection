# DETECTION OF FAKE BANK CURRENCY WITH MACHINE LEARNING ALGORITHMS

This project is an implementation of a multi-layered counterfeit currency detection system, as described in contemporary research. It utilizes **Optical Character Recognition (OCR)**, **Face Recognition**, and **Hough Transformation** to achieve high accuracy (~93.33%) in identifying fake banknotes.

## Features
- **OCR Analysis:** Verifies serial numbers and micro-printing authenticity.
- **Face Recognition:** Detects and verifies portraits on banknotes using Haar Cascade classifiers.
- **Hough Line Transform:** Identifies security threads and geometric patterns.
- **Visual Mapping:** Displays Canny edges, Hough patterns, and face detections for expert review.

## Tech Stack
- **Python** 3.12+
- **Streamlit** (Premium Web Dashboard)
- **OpenCV** (Image Processing & Feature Extraction)
- **PyTesseract** (OCR Engine)
- **NumPy** (Numerical Computing)

## Installation

1. **Clone/Move to this directory:**
   ```bash
   cd /media/debu/C218B74418B735EF/fake_currency_detection
   ```

2. **Run Setup Script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Install Tesseract OCR (System Level):**
   ```bash
   sudo apt update
   sudo apt install tesseract-ocr
   ```

4. **Run the Application:**
   ```bash
   source venv/bin/activate
   streamlit run app.py
   ```

## Workflow
1. **Upload Image:** Upload a high-resolution image of a banknote (e.g., 1000 Taka note).
2. **Analysis:** The system performs preprocessing, edge detection, and feature extraction.
3. **Scoring:** A multi-factor score is calculated based on the presence of security features.
4. **Result:** View the final verdict along with detailed visual evidence in the dashboard.

---
*Developed based on the provided thesis outline.*
