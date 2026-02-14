#!/bin/bash

# --- Stop Script for AI Currency Guardian PRO ---

echo "🛑 Terminating AI Currency Guardian Services..."

# Stop Streamlit
if [ -f .streamlit.pid ]; then
    PID=$(cat .streamlit.pid)
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "✅ Streamlit (PID: $PID) stopped."
    fi
    rm .streamlit.pid
fi

# Stop Flask
if [ -f .flask.pid ]; then
    PID=$(cat .flask.pid)
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "✅ Flask (PID: $PID) stopped."
    fi
    rm .flask.pid
fi

# PID file from previous version
if [ -f .server.pid ]; then
    PID=$(cat .server.pid)
    kill $PID 2>/dev/null
    rm .server.pid
fi

# Fallback cleanup
pkill -f "streamlit run app.py" 2>/dev/null
pkill -f "python3 server.py" 2>/dev/null

echo "✅ All services stopped."
