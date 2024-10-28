import json

import requests

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


def execute_dify_workflow(input_params, api_key):
    """Dify APIでワークフローを実行する
    Args:
        input_params (dict[str, Any]): ワークフローの開始ノードの入力
        api_key (str): 実行したいワークフローのAPIキー
    Returns:
        Any: ワークフローの終了ノードの出力
    """
    url = "https://api.dify.ai/v1/workflows/run"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "inputs": input_params,
        "response_mode": "blocking",
        "user": "from_django",
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
        response.raise_for_status()
        return response.json()["data"]["outputs"]["text"]
    except requests.exceptions.RequestException as e:
        raise
