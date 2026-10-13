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

# Trained model
if [ ! -f "models/taka_authenticator.pth" ]; then
    echo "⚠️  Trained model not found. Run: python3 download_dataset.py && python3 train_ai.py"
fi

echo "✅ Setup complete!"
echo "To run the Premium Design (New): source venv/bin/activate && python3 server.py"
echo "To run the Streamlit version: source venv/bin/activate && streamlit run app.py"
