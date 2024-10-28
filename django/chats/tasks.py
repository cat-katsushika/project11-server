import json

from config import settings
from trials.models import Player, Trial

from .models import Message, Question
from .utils import execute_dify_workflow


def generate_ai_reply(message_id):
    """AI裁判官の返答メッセージを生成して保存する

    - MessageCreateAPIView内で呼び出されることを想定している
    - 生成されたメッセージはAI裁判官の名前で保存される
    - TODO: API呼び出し後すぐにメッセージを保存するのではなく、質問モデルに追加するように変更する

    Args:
        message_id (UUID): 対象のメッセージID
    Returns:
        None
    """
    message = Message.objects.get(id=message_id)
    trial = Trial.objects.get(id=message.chat.trial.id)
    if not Player.objects.filter(trial=trial, role="judge").exists():
        Player.objects.create(trial=trial, role="judge", name="AI裁判官")
    past_messages_array = [
        {
            "player_name": message.player.name,
            "message_content": message.message,
            "created_at": message.created_at.isoformat(),
        }
        for message in Message.objects.filter(chat=message.chat)
    ]
    waiting_messages_array = [
        {"message": question.content, "priority": question.order} for question in Question.objects.filter(trial=trial)
    ]

    input_params = {
        "target_message": message.message,
        "target_player_role": message.player.role,
        "past_messages": json.dumps(past_messages_array, ensure_ascii=False),
        "trial_subject": trial.subject,
        "plaintiff_name": Player.objects.get(trial=trial, role="plaintiff").name,
        "defendant_name": Player.objects.get(trial=trial, role="defendant").name,
        "plaintiff_claim": trial.plaintiff_claim,
        "defendant_claim": trial.defendant_claim,
        "waiting_messages": json.dumps(waiting_messages_array, ensure_ascii=False),
        "target_player_name": message.player.name,
    }

    response = execute_dify_workflow(input_params, settings.DIFY_API_KEY_GENR_AI_REP)

    # NOTE: temp    # noqa: ERA001
    Message.objects.create(
        chat=message.chat,
        player=Player.objects.get(trial=trial, role="judge"),
        message=json.loads(response)["reply_message"],
    )
