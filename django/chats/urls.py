from django.urls import path

from . import views


app_name = "chats"

urlpatterns = [
    path("chat/<uuid:chat_id>/message/polling/", views.ChatMessagePollingListAPIView.as_view()),
    path("message/create/", views.MessageCreateAPIView.as_view()),
]
