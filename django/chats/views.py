from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Chat, Message
from .serializers import GoodSerializer, MessagePollingSerializer, MessageSerializer


class ChatMessagePollingListAPIView(APIView):
    def get(self, request, chat_id):
        latest_message_created_at = request.query_params.get("latest_message_created_at")
        if latest_message_created_at is None:
            return Response(
                {"detail": "クエリパラメータ'latest_message_created_at'は空にできません。"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        chat = get_object_or_404(Chat, id=chat_id)
        messages = chat.message_set.filter(created_at__gt=latest_message_created_at).order_by("created_at")
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
        # TODO: 非同期でDifyのAPIを呼び出す # noqa: TD002, TD003, FIX002
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GiveGoodAPIView(APIView):
    def post(self, request, message_id):
        serializer = GoodSerializer(data={"message": message_id, "player": request.user.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": "グッドをつけました。"}, status=status.HTTP_200_OK)


class CancelGoodAPIView(APIView):
    def post(self, request, message_id):
        message = get_object_or_404(Message, id=message_id)
        good = message.good_set.get(player=request.user)
        good.delete()
        return Response({"success": "グッドを取り消しました。"}, status=status.HTTP_200_OK)
