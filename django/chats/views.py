from urllib.parse import unquote

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Chat, Message
from .serializers import GoodSerializer, MessagePollingSerializer, MessageSerializer
from .tasks import conversation_check, response_and_question_list_update
from .utils import check_chat_is_main


class ChatMessagePollingListAPIView(APIView):
    def get(self, request, chat_id):
        encoded_timestamp_param = request.query_params.get("latest_message_created_at", "")
        if encoded_timestamp_param != "":
            latest_message_created_at = unquote(encoded_timestamp_param)
            chat = get_object_or_404(Chat, id=chat_id)
            messages = chat.message_set.filter(created_at__gt=latest_message_created_at).order_by("created_at")
        else:
            messages = Message.objects.all()
        serializer = MessagePollingSerializer(messages, many=True)
        return Response(serializer.data)


class ChatLatestMessageAPIView(APIView):
    def post(self, request):
        chat_id = request.data.get("chat_id")
        if chat_id is None:
            return Response({"detail": "'chat_id'は空にできません。"}, status=status.HTTP_400_BAD_REQUEST)
        chat = get_object_or_404(Chat, id=chat_id)
        message = chat.message_set.latest("created_at")
        serializer = MessageSerializer(message)
        return Response(serializer.data)


class MessageCreateAPIView(APIView):
    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # AIが絡む処理
        chat_id = request.data.get("chat_id", None)
        player_id = request.data.get("player_id", None)

        chat_is_main = check_chat_is_main(chat_id)
        if chat_is_main:
            # メインチャットの場合は、AI裁判官の新しい質問を追加するかどうか
            conversation_check.delay_on_commit(chat_id)
        else:
            # サブチャットの場合は、返答と質問リストの更新
            response_and_question_list_update.delay_on_commit(chat_id, player_id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GiveGoodAPIView(APIView):
    def post(self, request, message_id):
        serializer = GoodSerializer(data={"message": message_id, "player": request.data["player_id"]})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": "グッドをつけました。"}, status=status.HTTP_200_OK)


class CancelGoodAPIView(APIView):
    def post(self, request, message_id):
        message = get_object_or_404(Message, id=message_id)
        good = message.good_set.get(player=request.data["player_id"])
        good.delete()
        return Response({"success": "グッドを取り消しました。"}, status=status.HTTP_200_OK)
