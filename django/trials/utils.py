from chats.models import Chat

from .models import GameState, Player, Trial
from django.conf import settings


def get_chat_id(trial_id, role) -> tuple:
    """trial_idとroleからメインチャットとサブチャットのIDを取得する"""

    if role == "spectator":
        sub_chat = Chat.objects.create(trial_id=trial_id, is_main=False)
        sub_chat_id = str(sub_chat.id)
    else:
        sub_chat_id = ""

    main_chat = Chat.objects.get(trial_id=trial_id, is_main=True)
    main_chat_id = str(main_chat.id)

    return main_chat_id, sub_chat_id


def update_trial_game_state(trial_id) -> None:
    """裁判のゲーム状態を更新する"""

    game_state = GameState.objects.get(trial_id=trial_id)

    plaintiff = Player.objects.filter(trial_id=trial_id, role="plaintiff").exists()
    defendant = Player.objects.filter(trial_id=trial_id, role="defendant").exists()
    if plaintiff and defendant and game_state.state == "show_two_qr_codes":
        game_state.state = "show_one_qr_codes"
        game_state.save()
        return

    trial = Trial.objects.get(id=trial_id)
    if trial.defendant_claim and trial.plaintiff_claim and game_state.state == "show_one_qr_codes":
        game_state.state = "show_first_claim_and_judge"
        game_state.save()
        return
    

def call_zaitei_api(inputs):
    api_key = settings.ZENTEIHANKETHI_KEY
    url = "https://api.dify.ai/v1/workflows/run"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "inputs": inputs,
        "response_mode": "blocking",
        "user": "abc-1234"
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()["data"]["outputs"]["text"]
