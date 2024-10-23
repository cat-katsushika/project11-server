from rest_framewirk.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Message
from .serializers import MessageSerialiser, MessagePollingSerializer


class ChatMessagePollingListAPIView(APIView):
    def get(self, request, chat_id):
        latest_message_created_at = request.query_params.get("latest_message_created_at")
        if latest_message_created_at is None:
            return Response({"detail": "クエリパラメータ'latest_message_created_at'は空にできません。"}, status=status.HTTP_400_BAD_REQUEST)
        messages = Message.objects.filter(chat=chat_id, created_at__gt=latest_message_created_at).order_by("created_at")
        serializer = MessagePollingSerializer(messages, many=True)
        return Response(serializer.data)


class ChatLatestMessageAPIView(APIView):
    def post(self, request):
        chat_id = request.data.get("chat_id")
        if chat_id is None:
            return Response({"detail": "'chat_id'は空にできません。"}, status=status.HTTP_400_BAD_REQUEST)
        message = Message.objects.filter(chat=chat_id).latest("created_at")
        serializer = MessageSerialiser(message)
        return Response(serializer.data)


class MessageCreateAPIView(APIView):
    def post(self, request):
        serializer = MessageSerialiser(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        # TODO: 非同期でDifyのAPIを呼び出す
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
