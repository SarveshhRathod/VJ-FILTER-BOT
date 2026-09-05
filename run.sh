#!/usr/bin/env bash
set -e

echo "=================================================="
echo "🚀 VJ-FILTER-BOT V2: Linux Auto Setup & Runner"
echo "=================================================="

# 1. Folders Ensure Karein
mkdir -p core downloads
touch core/__init__.py

# 2. Virtual Environment Setup
if [ ! -d "venv" ]; then
    echo "📦 Creating Virtual Environment (venv)..."
    python3 -m venv venv
fi

echo "🔄 Activating Virtual Environment..."
source venv/bin/activate

# 3. Dependencies Install/Update
echo "📥 Checking and Installing Dependencies..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi
pip install motor psutil pymongo

# 4. Check .env
if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: '.env' file nahi mili! Bot error de sakta hai."
    echo "Kripya '.env' banakar credentials set karein."
fi

# 5. Start the bot
echo "⚡ Starting Bot..."
python3 bot.py
