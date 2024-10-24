from django.contrib import admin

from .models import GameState, Player, Trial

admin.site.register(Trial)
admin.site.register(Player)
admin.site.register(GameState)
