from django.urls import path

from .views import (
    TrialClaimAPIView,
    TrialCreateAPIView,
    TrialGameStateAPIView,
    TrialGameStateSetAPIView,
    TrialPlayerCreateAPIView,
)

app_name = "trials"

urlpatterns = [
    path("create/", TrialCreateAPIView.as_view(), name="trial-create"),
    path("game_state/", TrialGameStateAPIView.as_view(), name="trial-game-state"),
    path("game_state/set/", TrialGameStateSetAPIView.as_view(), name="trial-game-state-set"),
    path("player/create/", TrialPlayerCreateAPIView.as_view(), name="trial-player-create"),
    path("claim/", TrialClaimAPIView.as_view(), name="trial-claim"),
]
