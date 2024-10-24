import uuid6
from django.db import models

from trials.models import Player, Trial


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    trial = models.ForeignKey(Trial, on_delete=models.CASCADE, verbose_name="裁判")
    is_main = models.BooleanField(default=False, verbose_name="メインチャットかどうか")

    class Meta:
        verbose_name = "チャット"

    def __str__(self):
        return f"[{'Main' if self.is_main else 'Sub'}] {self.trial.subject[:15]}..."


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, verbose_name="チャット")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name="発言者")
    message = models.CharField(max_length=100, verbose_name="発言内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    class Meta:
        verbose_name = "メッセージ"

    def __str__(self):
        return f"[{self.created_at}] {self.player.name}: {self.message[:15]}..."


class Good(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="メッセージ")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name="グッドを押したプレイヤー")

    class Meta:
        verbose_name = "グッド"
        constraints = [
            models.UniqueConstraint(fields=["message", "player"], name="unique_good"),
        ]

    def __str__(self):
        return f"{self.player.name} -> {self.message.message[:15]}..."
