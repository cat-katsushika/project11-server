from django.urls import path

from .views import (
    ClaimsAndJudgmentsAPIView,
    TrialClaimAPIView,
    TrialCreateAPIView,
    TrialGameStateAPIView,
    TrialGameStateSetAPIView,
    TrialPlayerCreateAPIView,
    TrialProjectorDiscussionAPIView,
    TrialToPdfAPIView,
)

app_name = "trials"

urlpatterns = [
    path("create/", TrialCreateAPIView.as_view(), name="trial-create"),
    path("projector/discussion/", TrialProjectorDiscussionAPIView.as_view(), name="trial-projector-discussion"),
    path("claims_and_judgments/", ClaimsAndJudgmentsAPIView.as_view(), name="claims-and-judgments"),
    path("game_state/", TrialGameStateAPIView.as_view(), name="trial-game-state"),
    path("game_state/set/", TrialGameStateSetAPIView.as_view(), name="trial-game-state-set"),
    path("player/create/", TrialPlayerCreateAPIView.as_view(), name="trial-player-create"),
    path("claim/", TrialClaimAPIView.as_view(), name="trial-claim"),
    path("to_pdf/", TrialToPdfAPIView.as_view(), name="trial-to-pdf"),
]
