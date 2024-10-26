#!/bin/bash
# entrypoint.sh

# データベースマイグレーション
python manage.py migrate

# 静的ファイルの収集
python manage.py collectstatic --noinput

# Djangoサーバーを実行
gunicorn config.wsgi:application --bind 0.0.0.0:8000
