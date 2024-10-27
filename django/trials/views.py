from typing import ClassVar

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from chats.models import Chat

from .models import GameState, Player, Trial
from .serializers import TrialCreateSerializer
from .tasks import create_discussion_content, create_provisional_judgment
from .utils import get_chat_id, update_trial_game_state


class TrialCreateAPIView(APIView):
    def post(self, request):
        subject = request.data.get("subject", None)
        if subject:
            trial = Trial.objects.create(subject=subject)
            serializer = TrialCreateSerializer(trial)

            # メインチャットを作成
            Chat.objects.create(trial=trial, is_main=True)

            # ゲーム状態を作成
            GameState.objects.create(trial=trial, state="show_two_qr_codes")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TrialProjectorDiscussionAPIView(APIView):
    def post(self, request):
        trial_id = request.data.get("trial_id", None)

        if not trial_id:
            detail = {"detail": "trial_idは必須です"}
            return Response(detail, status=status.HTTP_400_BAD_REQUEST)

        try:
            trial = Trial.objects.get(id=trial_id)
        except Trial.DoesNotExist:
            detail = {"detail": "指定されたtrial_idに対応するTrialが存在しません"}
            return Response(detail, status=status.HTTP_404_NOT_FOUND)

        response_data = {
            "trial_id": trial_id,
            "subject": trial.subject,
            "plaintiff_claim": trial.plaintiff_claim,
            "defendant_claim": trial.defendant_claim,
            "provisional_judgment": trial.provisional_judgment,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class ClaimsAndJudgmentsAPIView(APIView):
    RESOURCE_MAPPING: ClassVar[dict[str, str]] = {
        "plaintiff_claim": "plaintiff",
        "defendant_claim": "defendant",
        "provisional_judgment": "AI裁判官",
        "plaintiff_final_claim": "plaintiff",
        "defendant_final_claim": "defendant",
        "final_judgment": "AI裁判官",
    }

    def post(self, request):
        trial_id = request.data.get("trial_id", None)
        resource_type = request.data.get("resource_type", None)

        # 必須フィールドのバリデーション
        if not trial_id or not resource_type:
            return Response({"detail": "trial_id, resource_typeは必須です"}, status=status.HTTP_400_BAD_REQUEST)

        # Trialの取得
        try:
            trial = Trial.objects.get(id=trial_id)
        except Trial.DoesNotExist:
            return Response(
                {"detail": "指定されたtrial_idに対応するTrialが存在しません"}, status=status.HTTP_404_NOT_FOUND
            )

        # resource_typeのバリデーション
        if resource_type not in self.RESOURCE_MAPPING:
            return Response({"detail": "resource_typeが不正です"}, status=status.HTTP_400_BAD_REQUEST)

        # resourceの取得
        resource = getattr(trial, resource_type, None)

        # Player名の取得
        player_role = self.RESOURCE_MAPPING.get(resource_type)
        if player_role == "AI裁判官":
            player_name = player_role
        else:
            try:
                player = Player.objects.get(trial=trial, role=player_role)
                player_name = player.name
            except Player.DoesNotExist:
                return Response({"detail": f"{player_role}のPlayerが存在しません"}, status=status.HTTP_404_NOT_FOUND)

        # レスポンスデータの作成
        response_data = {
            "trial_id": trial_id,
            "player_name": player_name,
            "resource_type": resource_type,
            "resource": resource,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class TrialGameStateAPIView(APIView):
    def post(self, request):
        trial_id = request.data.get("trial_id", None)

        if not trial_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            game_state = GameState.objects.get(trial_id=trial_id)
        except GameState.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        response_data = {
            "trial_id": trial_id,
            "state": game_state.state,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class TrialGameStateSetAPIView(APIView):
    def post(self, request):
        trial_id = request.data.get("trial_id", None)
        state = request.data.get("state", None)

        if not trial_id or not state:
            detail = {"detail": "trial_id, stateは必須です"}
            return Response(detail, status=status.HTTP_400_BAD_REQUEST)

        if state not in GameState.STATE_CHOICES:
            detail = {"detail": "stateが不正です"}
            return Response(detail, status=status.HTTP_400_BAD_REQUEST)

        try:
            game_state = GameState.objects.get(trial_id=trial_id)
        except GameState.DoesNotExist:
            detail = {"detail": "指定されたtrial_idに対応するGameStateが存在しません"}
            return Response(status=status.HTTP_404_NOT_FOUND)

        game_state.state = state
        game_state.save()

        if state == "show_final_claim_and_judge":
            create_discussion_content.delay_on_commit(trial_id)

        response_data = {
            "trial_id": trial_id,
            "state": state,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class TrialPlayerCreateAPIView(APIView):
    def post(self, request):
        trial_id = request.data.get("trial_id", None)
        role = request.data.get("role", None)
        player_name = request.data.get("player_name", None)

        if not trial_id or not role or not player_name:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            trial = Trial.objects.get(id=trial_id)
        except Trial.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if role in ("plaintiff", "defendant", "spectator"):
            player = Player.objects.create(trial=trial, role=role, name=player_name)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        update_trial_game_state(trial_id)

        main_chat_id, sub_chat_id = get_chat_id(trial_id, role)
        response_data = {
            "player_id": str(player.id),
            "player_name": player.name,
            "role": player.role,
            "main_chat_id": main_chat_id,
            "sub_chat_id": sub_chat_id,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class TrialClaimAPIView(APIView):
    def post(self, request):
        trial_id = request.data.get("trial_id", None)
        player_id = request.data.get("player_id", None)
        claim = request.data.get("claim", None)

        if not trial_id or not player_id or not claim:
            detail = {"detail": "trial_id, player_id, claimは必須です"}
            return Response(detail, status=status.HTTP_400_BAD_REQUEST)

        try:
            trial = Trial.objects.get(id=trial_id)
        except Trial.DoesNotExist:
            detail = {"detail": "指定されたtrial_idに対応するTrialが存在しません"}
            return Response(detail, status=status.HTTP_404_NOT_FOUND)

        try:
            player = Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            detail = {"detail": "指定されたplayer_idに対応するPlayerが存在しません"}
            return Response(detail, status=status.HTTP_404_NOT_FOUND)

        role = player.role
        if role not in ("plaintiff", "defendant"):
            detail = {"detail": "原告または被告のPlayerでないとclaimを提出できません"}
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if role == "plaintiff":
            trial.plaintiff_claim = claim
        elif role == "defendant":
            trial.defendant_claim = claim
        trial.save()

        if trial.plaintiff_claim and trial.defendant_claim and not trial.provisional_judgment:
            create_provisional_judgment.delay_on_commit(trial_id)

        update_trial_game_state(trial_id)

        response_data = {
            "trial_id": trial_id,
            "player_id": player_id,
            "claim": claim,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def patch(self, request):
        trial_id = request.data.get("trial_id", None)
        player_id = request.data.get("player_id", None)
        claim = request.data.get("claim", None)

        if not trial_id or not player_id or not claim:
            detail = {"detail": "trial_id, player_id, claimは必須です"}
            return Response(detail, status=status.HTTP_400_BAD_REQUEST)

        try:
            trial = Trial.objects.get(id=trial_id)
        except Trial.DoesNotExist:
            detail = {"detail": "指定されたtrial_idに対応するTrialが存在しません"}
            return Response(detail, status=status.HTTP_404_NOT_FOUND)

        try:
            player = Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            detail = {"detail": "指定されたplayer_idに対応するPlayerが存在しません"}
            return Response(detail, status=status.HTTP_404_NOT_FOUND)

        role = player.role
        if role not in ("plaintiff", "defendant"):
            detail = {"detail": "原告または被告のPlayerでないとclaimを提出できません"}
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if role == "plaintiff":
            trial.plaintiff_final_claim = claim
        elif role == "defendant":
            trial.defendant_final_claim = claim
        trial.save()

        response_data = {
            "trial_id": trial_id,
            "player_id": player_id,
            "claim": claim,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class TrialToPdfAPIView(APIView):
    def post(self, request):
        trial_id = request.data.get("trial_id", None)

        if not trial_id:
            detail = {"detail": "trial_idは必須です"}
            return Response(detail, status=status.HTTP_400_BAD_REQUEST)

        try:
            trial = Trial.objects.get(id=trial_id)
        except Trial.DoesNotExist:
            detail = {"detail": "指定されたtrial_idに対応するTrialが存在しません"}
            return Response(detail, status=status.HTTP_404_NOT_FOUND)

        response_data = {
            "trial_id": trial_id,
            "subject": trial.subject,
            "discussion_content": trial.discussion_content,
            "plaintiff_claim": trial.plaintiff_claim,
            "defendant_claim": trial.defendant_claim,
            "provisional_judgment": trial.provisional_judgment,
            "plaintiff_final_claim": trial.plaintiff_final_claim,
            "defendant_final_claim": trial.defendant_final_claim,
            "final_judgment": trial.final_judgment,
        }

        return Response(response_data, status=status.HTTP_200_OK)
