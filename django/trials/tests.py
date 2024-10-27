from typing import ClassVar

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TrialCreateAPITestCase(APITestCase):
    fixtures: ClassVar = [
        "trials/fixtures/trial.yaml",
    ]

    def test_create(self):
        request_data = {
            "subject": "subject",
        }
        response = self.client.post(
            reverse("trials:trial-create"),
            request_data,
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["subject"] == "subject"


class TrialProjectorDiscussionAPITestCase(APITestCase):
    fixtures: ClassVar = [
        "trials/fixtures/trial.yaml",
    ]

    def test_post_success(self):
        request_data = {
            "trial_id": "00000000-0000-0000-0000-000000000001",
        }
        response = self.client.post(
            reverse("trials:trial-projector-discussion"),
            request_data,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["trial_id"] == "00000000-0000-0000-0000-000000000001"
        assert response.data["subject"] == "裁判1 内容が全て埋まっている"
        assert response.data["plaintiff_claim"] == "原告主張"
        assert response.data["defendant_claim"] == "被告主張"
        assert response.data["provisional_judgment"] == "暫定判決"
