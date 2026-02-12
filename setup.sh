#!/bin/bash

# Setup script for Fake Currency Detection Project
echo "🚀 Setting up Fake Currency Detection Project..."

# Check if python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ python3 could not be found. Please install it."
    exit
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check for Tesseract
if ! command -v tesseract &> /dev/null
then
    echo "⚠️  Tesseract OCR not found. Please install it (sudo apt install tesseract-ocr)."
fi

echo "✅ Setup complete! Run 'source venv/bin/activate && streamlit run app.py' to start."
