from time import sleep

from celery import shared_task

from .models import Trial


@shared_task
def create_provisional_judgment(trial_id) -> str:
    """暫定判決を作成する"""

    trial = Trial.objects.get(id=trial_id)
    sleep(10)  # 動作確認用
    trial.provisional_judgment = "暫定的な判決"
    trial.save()
