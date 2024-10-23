from rest_framework import serializers

from .models import Trial


class TrialCreateSerializer(serializers.ModelSerializer):
    trial_id = serializers.UUIDField(source="id")

    class Meta:
        model = Trial
        fields = ("trial_id", "subject", "created_at")
