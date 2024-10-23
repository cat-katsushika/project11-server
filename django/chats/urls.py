from django.urls import path

from . import views


app_name = "chats"

urlpatterns = [
    path("chats/<uuid:chat_id>/", views.ChatMessagePollingListAPIView.as_view()),
    path("messages/", views.MessageCreateAPIView.as_view()),
]
