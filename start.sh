#!/bin/bash

# Installer Playwright + navigateurs (avec dépendances Linux pour Render)
echo "▶ Installing Playwright browsers..."
npx playwright install --with-deps

# Lancer le script principal
echo "▶ Starting bot..."
python vinted_bot.py
