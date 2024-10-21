import uuid6
from django.db import models

from trials.models import Trial, Player


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    trail_id = models.ForeignKey(Trial, on_delete=models.CASCADE, verbose_name="裁判")
    isMain = models.BooleanField(default=False, verbose_name="メインチャットかどうか")

    class Meta:
        verbose_name = "チャット"

    def __str__(self):
        return f"[{'Main' if self.isMain else 'Sub'}] {self.trail_id.subject[:15]}..."


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    chat_id = models.ForeignKey(Chat, on_delete=models.CASCADE, verbose_name="チャット")
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name="発言者")
    message = models.CharField(max_length=100, verbose_name="発言内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    class Meta:
        verbose_name = "メッセージ"

    def __str__(self):
        return f"[{self.created_at}] {self.player_id.name}: {self.message[:15]}..."


class Good(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    message_id = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="メッセージ")
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name="グッドを押したプレイヤー")

    class Meta:
        verbose_name = "グッド"

    def __str__(self):
        return f"{self.player_id.name} -> {self.message_id.message[:15]}..."
