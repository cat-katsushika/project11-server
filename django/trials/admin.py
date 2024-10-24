from django.contrib import admin

from .models import Player, Trial, GameState

admin.site.register(Trial)
admin.site.register(Player)
admin.site.register(GameState)
