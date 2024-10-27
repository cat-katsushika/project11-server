import json
from time import sleep

import requests
from celery import shared_task
from django.conf import settings

from chats.models import Chat, Message

from .models import Player, Trial

from .utils import call_zaitei_api


# @shared_task
def create_provisional_judgment(trial_id) -> str:
    """暫定判決を作成する"""

    trial = Trial.objects.get(id=trial_id)
    inputs = {
        "subject": trial.subject,
        "plaintiff_claim": trial.plaintiff_claim,
        "defendant_claim": trial.defendant_claim,
        "defendant_name": Player.objects.get(trial=trial, role="defendant").name,
        "plaintiff_name": Player.objects.get(trial=trial, role="plaintiff").name,
    }
    try:
        res = call_zaitei_api(inputs)
        trial.provisional_judgment = res
    except Exception:
        pass
    trial.save()

@shared_task
def create_discussion_content(trial_id) -> str:
    """話し合い内容を作成する"""

    trial = Trial.objects.get(id=trial_id)
    plaintiff = Player.objects.get(trial=trial, role="plaintiff")
    defendant = Player.objects.get(trial=trial, role="defendant")
    chat = Chat.objects.get(trial=trial, is_main=True)
    messages = Message.objects.filter(chat=chat)

    past_messages = ""

    for message in messages:
        past_messages += f"{plaintiff.player.role}: {message.message}\n"

    past_message_constraints = 1000
    if len(past_messages) > past_message_constraints:
        past_messages = past_messages[:past_message_constraints]

    api_key = settings.DIFY_API_KEY_DISCUSSION_CONTENT
    url = "https://api.dify.ai/v1/workflows/run"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "inputs": {
            "subject": trial.subject,
            "plaintiff_claim": trial.plaintiff_claim,
            "plaintiff_final_claim": trial.plaintiff_final_claim,
            "defendant_claim": trial.defendant_claim,
            "defendant_final_claim": trial.defendant_final_claim,
            "provisional_judgment": trial.provisional_judgment,
            "past_messages": past_messages,
            "plaintiff_name": plaintiff.name,
            "defendant_name": defendant.name,
        },
        "response_mode": "blocking",
        "user": "abc-123",
    }

    response = requests.post(url, headers=headers, data=json.dumps(data), timeout=20)
    text = response.json()["data"]["outputs"]["text"]

    trial.discussion_content = text
    trial.save()
