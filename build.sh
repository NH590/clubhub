#!/usr/bin/env bash
# Render chay file nay khi deploy
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
