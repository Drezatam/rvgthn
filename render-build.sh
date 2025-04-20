#!/bin/bash

echo "▶ Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "▶ Installing Playwright browsers..."
npx playwright install --with-deps
