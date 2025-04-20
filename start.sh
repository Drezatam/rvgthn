#!/bin/bash

# Installer les navigateurs Playwright (indispensable pour fonctionner)
playwright install --with-deps

# Lancer le script Python
python vinted_bot.py
