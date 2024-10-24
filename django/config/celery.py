import os

from celery import Celery

# Djangoの設定モジュールを環境変数として指定
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("project11")

# Djangoの設定ファイルの中で、CELERY_で始まる設定をCELERY用として読み込む
app.config_from_object("django.conf:settings", namespace="CELERY")

# Djangoの各アプリからタスクを自動的に読み込む
app.autodiscover_tasks()
