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
