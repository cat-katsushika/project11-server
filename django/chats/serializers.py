from rest_framework import serializers

from .models import Good, Message


class MessageSerialiser(serializers.ModelSerializer):
    messge_id = serializers.UUIDField(source="id")
    chat_id = serializers.UUIDField(source="chat.id")
    player_id = serializers.UUIDField(source="player.id")
    player_name = serializers.CharField(source="player.name", read_only=True)

    class Meta:
        model = Message
        fields = "__all__"


class MessagePollingSerializer(MessageSerialiser):
    player_role = serializers.CharField(source="player.role", read_only=True)

    class Meta:
        model = Message
        fields = "__all__"


class GoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Good
        fields = "__all__"
