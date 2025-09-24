#!/bin/bash

# Personal Accounting App Launcher
# This script creates a simple .app bundle that launches the accounting app

APP_NAME="Personal Accounting App"
SCRIPT_DIR="/Users/joy/Code/Python Projects/Accounting"
PYTHON_EXE="/Users/joy/Code/.venv/bin/python"
MAIN_SCRIPT="$SCRIPT_DIR/app_launcher.py"

echo "🏦 Starting Personal Accounting App..."
echo "📍 Working directory: $SCRIPT_DIR"

# Change to the script directory to ensure relative paths work
cd "$SCRIPT_DIR"

# Check if Python and main script exist
if [ ! -f "$PYTHON_EXE" ]; then
    echo "❌ Error: Python not found at $PYTHON_EXE"
    echo "Please make sure your virtual environment is set up correctly."
    exit 1
fi

if [ ! -f "$MAIN_SCRIPT" ]; then
    echo "❌ Error: app_launcher.py not found at $MAIN_SCRIPT"
    exit 1
fi

# Launch the app
echo "🚀 Launching the accounting app..."
exec "$PYTHON_EXE" "$MAIN_SCRIPT"