from django.shortcuts import get_object_or_404
from rest_framework import serializers

from trials.models import Player

from .models import Chat, Good, Message


class MessageSerializer(serializers.ModelSerializer):
    message_id = serializers.ReadOnlyField(source="id")
    chat_id = serializers.UUIDField(write_only=True)
    player_id = serializers.UUIDField()
    player_name = serializers.ReadOnlyField(source="player.name")

    class Meta:
        model = Message
        fields = ("message_id", "chat_id", "player_id", "player_name", "message", "created_at")

    def create(self, validated_data):
        chat_id = validated_data.pop("chat_id")
        player_id = validated_data.pop("player_id")
        chat = get_object_or_404(Chat, id=chat_id)
        player = get_object_or_404(Player, id=player_id)
        return Message.objects.create(chat=chat, player=player, **validated_data)


class MessagePollingSerializer(MessageSerializer):
    player_role = serializers.ReadOnlyField(source="player.role")

    class Meta:
        model = Message
        fields = ("message_id", "chat_id", "player_id", "player_name", "player_role", "message", "created_at")


class GoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Good
        fields = "__all__"
