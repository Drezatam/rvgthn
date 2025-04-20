#!/bin/bash

echo "▶ Installing Python dependencies..."
pip install -r requirements.txt

echo "▶ Installing Playwright browsers (sans sudo)..."
npx playwright install chromium
