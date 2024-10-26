from typing import ClassVar

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
        constraints: ClassVar[list[models.UniqueConstraint]] = [
            models.UniqueConstraint(fields=["message", "player"], name="unique_good"),
        ]

    def __str__(self):
        return f"{self.player.name} -> {self.message.message[:15]}..."


class Question(models.Model):
    trial = models.ForeignKey(Trial, on_delete=models.CASCADE, related_name="questions")  # 裁判への外部キー
    content = models.TextField()
    order = models.PositiveIntegerField()

    class Meta:
        ordering: ClassVar[list] = ["order"]
        constraints: ClassVar[list] = [models.UniqueConstraint(fields=["trial", "order"], name="unique_trial_order")]

    def __str__(self):
        return f"{self.trial.subject} - {self.order}: {self.content[:15]}..."

    def save(self, *args, **kwargs):
        if not self.pk:  # 新規作成時に order を設定
            max_order = Question.objects.filter(trial=self.trial).aggregate(models.Max("order"))["order__max"]
            self.order = (max_order or 0) + 1
        super().save(*args, **kwargs)

    def insert_at_order(self, new_order):
        """指定の順番に挿入し、他の質問の順番をずらす"""
        Question.objects.filter(trial=self.trial, order__gte=new_order).update(order=models.F("order") + 1)
        self.order = new_order
        self.save()

    @classmethod
    def pop_first_question(cls, trial):
        """特定の裁判の最初の質問を取得して削除し、順番をリセットする関数"""
        first_question = cls.objects.filter(trial=trial).order_by("order").first()
        if first_question:
            first_question.delete()
            # 削除後、残りの質問の order を 1 からリセット
            remaining_questions = cls.objects.filter(trial=trial).order_by("order")
            for idx, question in enumerate(remaining_questions, start=1):
                question.order = idx
                question.save()
        return first_question
