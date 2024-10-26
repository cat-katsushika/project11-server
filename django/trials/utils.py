from chats.models import Chat

from .models import GameState, Player, Trial


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
    if plaintiff and defendant:
        game_state.state = "show_one_qr_codes"
        game_state.save()
        return

    trial = Trial.objects.get(id=trial_id)
    if trial.defendant_claim and trial.plaintiff_claim:
        game_state.state = "show_first_claim_and_judge"
        game_state.save()
        return
