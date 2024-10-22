from django.contrib import admin

from .models import Chat, Good, Message

admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(Good)
