from typing import ClassVar

import uuid6
from django.db import models


class Trial(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    subject = models.CharField(max_length=50, verbose_name="裁判内容")
    plaintiff_claim = models.CharField(max_length=100, verbose_name="原告(A)の主張")
    plaintiff_final_claim = models.CharField(max_length=100, verbose_name="原告(A)の最終主張")
    defendant_claim = models.CharField(max_length=100, verbose_name="被告(B)の主張")
    defendant_final_claim = models.CharField(max_length=100, verbose_name="被告(B)の最終主張")
    provisional_judgment = models.CharField(max_length=100, verbose_name="暫定的な判決")
    final_judgment = models.CharField(max_length=100, verbose_name="最終判決")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    class Meta:
        verbose_name = "裁判"

    def __str__(self):
        return f"[{self.created_at}] {self.subject[:15]}..."


class GameState(models.Model):
    STATE_CHOICES: ClassVar[dict[str, str]] = {
        "show_two_qr_codes": "QRコードを2つ表示",
        "show_one_qr_codes": "QRコードを1つ表示",
        "show_first_claim_and_judge": "原告の主張,被告の主張,裁判官の暫定的な判決を表示",
        "discussion": "話し合い",
        "show_final_claim_and_judge": "最終主張と判決を表示",
    }
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    trial = models.ForeignKey(Trial, on_delete=models.CASCADE, verbose_name="裁判")
    state = models.CharField(max_length=30, choices=STATE_CHOICES.items(), verbose_name="ゲーム状態")

    def __str__(self):
        return f"[{self.trial.subject}] {self.state}"


class Player(models.Model):
    ROLE_CHOICES: ClassVar[dict[str, str]] = {
        "plaintiff": "原告(A)",
        "defendant": "被告(B)",
        "judge": "裁判官",
        "spectator": "傍聴人",
    }

    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    trial = models.ForeignKey(Trial, on_delete=models.CASCADE, verbose_name="裁判")
    name = models.CharField(max_length=10, verbose_name="名前")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES.items(), verbose_name="役職")

    class Meta:
        verbose_name = "プレイヤー"

    def __str__(self):
        return f"[{self.role}] {self.name}"
