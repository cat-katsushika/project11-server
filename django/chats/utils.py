from trials.models import Trial

from .models import Chat, Question


def set_question_to_list(trial_id, content, order):
    """
    質問をリストに追加する
    """
    try:
        trial = Trial.objects.get(id=trial_id)
    except Trial.DoesNotExist:
        return

    new_question = Question(trial=trial, content=content)
    new_question.insert_at_order(order)

    return


def get_question_by_trial_id(trial_id) -> str | None:
    """
    次にAI裁判官が三者間対話に投げかける質問を取得する
    エラー時はNoneを返す
    """

    try:
        trial = Trial.objects.get(id=trial_id)
    except Trial.DoesNotExist:
        return None

    first_question = Question.pop_first_question(trial)

    empty_question = "私から問いかけることはありせん. 傍聴人の皆様からの意見をお待ちしております."

    return first_question.content if first_question.content else empty_question


def check_chat_is_main(chat_id):
    """
    チャットがメインチャットかどうかを判定する
    """
    try:
        chat = Chat.objects.get(id=chat_id)
    except Chat.DoesNotExist:
        return None

    return chat.is_main
