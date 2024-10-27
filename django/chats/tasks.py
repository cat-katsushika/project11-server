
import json
import logging

from config import settings
from trials.models import Player, Trial

from .models import Message, Question
from .utils import call_dify_api

logger = logging.getLogger("config")


# @shared_task
def generate_ai_reply(message_id):
    """
    AI裁判官の返答を作成し,新しい質問がある場合は質問リストに追加する
    """
    message = Message.objects.get(id=message_id)
    trial = Trial.objects.get(id=message.chat.trial.id)

    past_messages_array = [
        {
            "player_name": message.player.name,
            "message_content": message.message,
            "created_at": message.created_at.isoformat()
        }
        for message in Message.objects.filter(chat=message.chat)
    ]
    waiting_messages_array = [
        {
            "message": question.content,
            "priority": question.order
        }
        for question in Question.objects.filter(trial=trial)
    ]

    inputs = {
        "target_message": message.message,
        "target_player_role": message.player.role,
        "past_messages": json.dumps(past_messages_array, ensure_ascii=False),
        "trial_subject": trial.subject,
        "plaintiff_name": Player.objects.get(trial=trial, role="plaintiff").name,
        "defendant_name": Player.objects.get(trial=trial, role="defendant").name,
        "plaintiff_claim": trial.plaintiff_claim,
        "defendant_claim": trial.defendant_claim,
        "waiting_messages": json.dumps(waiting_messages_array, ensure_ascii=False),
        "target_player_name": message.player.name
    }
    res = call_dify_api(inputs, settings.DIFY_API_KEY)

    # 一時
    Message.objects.create(
        chat=message.chat, player=Player.objects.get(trial=trial, role="judge"), message=json.loads(res)["reply_message"]
        )

    # # AIに確認
    # # mock
    # should_speak_new_question = bool(secrets.choice([0, 1]))
    # # mock end

    # if should_speak_new_question:
    #     # 新しい質問を発言
    #     ai_judge = Player.objects.get_or_create(trial=trial, role="judge", name="AI裁判官")[0]
    #     question = get_question_by_trial_id(str(trial.id))
    #     Message.objects.create(chat=chat, player=ai_judge, message=question)


# @shared_task
# def response_and_question_list_update(chat_id, player_id):
#     """
#     傍聴人とAI裁判官のチャットにおいて, AI裁判官の返答を作成し,
#     新しい質問がある場合は質問リストに追加する
#     """
#     chat = Chat.objects.get(id=chat_id)
#     trial = chat.trial

#     # AIに確認
#     # mock
#     ai_response = "いい質問だね, 現状答えられないので, 状況を見て私が質問します."
#     new_question_is_exist = bool(secrets.choice([0, 1]))
#     new_question = "新しい大事な質問" + "".join(secrets.choice(string.ascii_letters) for _ in range(2))
#     new_question_order = 1
#     # mock end

#     # 返信メッセージを作成
#     Message.objects.create(chat=chat, player_id=player_id, message=ai_response)

#     # 新しい質問候補がある場合
#     if new_question_is_exist:
#         trial_id = str(trial.id)
#         set_question_to_list(trial_id, new_question, new_question_order)
