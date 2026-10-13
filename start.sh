#!/bin/bash

# --- Start Script for AI Currency Guardian PRO ---

echo "🚀 Initializing AI Currency Guardian PRO Suite..."

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment not found. Running setup.sh..."
    chmod +x setup.sh
    ./setup.sh
fi

# Activate venv
source venv/bin/activate

# Trained model check
if [ ! -f "models/taka_authenticator.pth" ]; then
    echo "⚠️  Trained model not found. Run: python3 download_dataset.py && python3 train_ai.py"
fi

# Function to start streamlit
start_streamlit() {
    if pgrep -f "streamlit run app.py" > /dev/null; then
        echo "⚠️  Streamlit Pro UI is already running."
    else
        echo "🛡️  Starting Streamlit Pro UI at http://localhost:8501 ..."
        nohup streamlit run app.py --server.port 8501 > streamlit.log 2>&1 &
        echo $! > .streamlit.pid
        sleep 3
        echo "✅ Streamlit started. Logs: streamlit.log"
    fi
}

# Function to start flask
start_flask() {
    if pgrep -f "python3 server.py" > /dev/null; then
        echo "⚠️  Flask Classic UI is already running."
    else
        echo "🌐 Starting Flask Classic UI at http://127.0.0.1:5000 ..."
        nohup python3 server.py > server.log 2>&1 &
        echo $! > .flask.pid
        sleep 2
        echo "✅ Flask started. Logs: server.log"
    fi
}

start_streamlit
start_flask

echo "-------------------------------------------------------"
echo "📊 Dashboard Status:"
echo "👉 Pro Interface: http://localhost:8501"
echo "👉 Classic Interface: http://127.0.0.1:5000"
echo "-------------------------------------------------------"
echo "Use ./stop.sh to terminate all services."
