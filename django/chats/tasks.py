import secrets
import string

from celery import shared_task

from trials.models import Player

from .models import Chat, Message
from .utils import get_question_by_trial_id, set_question_to_list


@shared_task
def conversation_check(chat_id):
    """mainチャットのchat_idのみを受け取る可能性がある.
    会話をチェックし, 新しい質問を発言するかどうかをAIにより判定
    必要に応じて質問リストの優先度の一番高いものをチャットで発言
    """

    chat = Chat.objects.get(id=chat_id)
    trial = chat.trial

    # AIに確認
    # mock
    should_speak_new_question = bool(secrets.choice([0, 1]))
    # mock end

    if should_speak_new_question:
        # 新しい質問を発言
        ai_judge = Player.objects.get_or_create(trial=trial, role="judge", name="AI裁判官")[0]
        question = get_question_by_trial_id(str(trial.id))
        Message.objects.create(chat=chat, player=ai_judge, message=question)


@shared_task
def response_and_question_list_update(chat_id, player_id):
    """
    傍聴人とAI裁判官のチャットにおいて, AI裁判官の返答を作成し,
    新しい質問がある場合は質問リストに追加する
    """
    chat = Chat.objects.get(id=chat_id)
    trial = chat.trial

    # AIに確認
    # mock
    ai_response = "いい質問だね, 現状答えられないので, 状況を見て私が質問します."
    new_question_is_exist = bool(secrets.choice([0, 1]))
    new_question = "新しい大事な質問" + "".join(secrets.choice(string.ascii_letters) for _ in range(2))
    new_question_order = 1
    # mock end

    # 返信メッセージを作成
    Message.objects.create(chat=chat, player_id=player_id, message=ai_response)

    # 新しい質問候補がある場合
    if new_question_is_exist:
        trial_id = str(trial.id)
        set_question_to_list(trial_id, new_question, new_question_order)
